import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from PIL import Image, ImageTk
from datetime import date
from db import get_connection, execute
from qr_service import generate_qr_image
from xml_service import export_koi_xml
import io
from tkinter import filedialog
from camera_service import scan_qr_from_camera
import barcode
from barcode.writer import ImageWriter
from passport_view import render_passport
from register_koi import open_registration_window

from xrpl.clients import JsonRpcClient
from xrpl.models.requests import AccountInfo, AccountTx
from xrpl.utils import drops_to_xrp
from threading import Thread

from splash import show_splash
show_splash(4000)

BUYER_ADDRESS = "rM3Eq9kfVmEYBWTVZYripuLwkkCdvhH7Zz"
TESTNET_URL = "https://s.altnet.rippletest.net:51234/"


class KoiLedgerDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("KOI LEDGER MVP")
        self.root.geometry("1200x750")
        self.root.state('zoomed')  # Fullscreen on Windows


        # Current Koi being viewed
        self.current_koi_id = None

        # Transfer window reference
        self.transfer_window = None

        # List to track all popups (QR code, Add Health, Add Pedigree, etc.)
        self.open_popups = []

        # --- Top Frame: Title + Logo ---
        top_frame = tk.Frame(root)
        top_frame.pack(side=tk.TOP, fill=tk.X, pady=10)

        title = tk.Label(top_frame, text="KOI LEDGER", font=("Arial", 26, "bold"))
        title.pack(side=tk.LEFT, padx=20)

        koi_image = Image.open("Koi.png")
        koi_image = koi_image.resize((200, 80))
        koi_photo = ImageTk.PhotoImage(koi_image)
        img_label = tk.Label(top_frame, image=koi_photo)
        img_label.image = koi_photo
        img_label.pack(side=tk.RIGHT, padx=20)

        # --- Search Frame ---
        # --- Search Frame ---
        search_frame = tk.Frame(root)
        search_frame.pack(side=tk.TOP, fill=tk.X, pady=10)

        # Left container: Search + Scan QR
        left_container = tk.Frame(search_frame)
        left_container.pack(side=tk.LEFT, fill=tk.X, expand=True)  # <-- IMPORTANT: expand=True

        tk.Label(left_container, text="Search Koi ID:").pack(side=tk.LEFT, padx=5)
        self.search_entry = tk.Entry(left_container, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_btn = tk.Button(left_container, text="Search", command=self.search_koi)
        self.search_btn.pack(side=tk.LEFT, padx=5)
        self.scan_btn = tk.Button(left_container, text="Scan QR", command=self.scan_qr)
        self.scan_btn.pack(side=tk.LEFT, padx=5)

        # Right container: Action buttons
        self.action_frame = tk.Frame(search_frame)
        self.action_frame.pack(side=tk.RIGHT)  # No expand here

        self.action_buttons = {}
        btn_names = [
            "View",
            "Generate QR",
            "Transfer",
            "Ledger",
            "XRPL Verify",
            "Export",
            "Ownership History",
            "Health Records",
            "Pedigree",
            "Certificates"
        ]
        for name in btn_names:
            btn = tk.Button(self.action_frame, text=name, width=15, command=lambda n=name: self.handle_action(n))
            btn.pack(side=tk.LEFT, padx=2)

        self.action_frame.pack_forget()  # Hide initially


        # Add after creating self.action_frame
        self.input_frame = tk.Frame(self.root)
        self.input_frame.pack(fill=tk.X, pady=10)
        # Initially hide input_frame
        self.input_frame.pack_forget()

        # --- Display Frame: Treeview Table ---
        self.display_frame = tk.Frame(root, relief=tk.SUNKEN, bd=2)
        self.display_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.tree = ttk.Treeview(self.display_frame)
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.scrollbar = ttk.Scrollbar(self.display_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")

        # --- Footer with Close Koi ---
        footer_frame = tk.Frame(root)
        footer_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.close_btn = tk.Button(footer_frame, text="Close Koi", command=self.close_koi)
        self.close_btn.pack(pady=5)

    # -------------------------------
    # DB Helpers
    # -------------------------------
    def fetch_one(self, query, params):
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute(query, params)
        row = cur.fetchone()
        cur.close()
        conn.close()
        return row

    def fetch_all(self, query, params):
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute(query, params)
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows

    def execute(self, query, params):
        execute(query, params)


    def center_popup(self, window, width=600, height=400):
        """Centers a Toplevel window on the screen."""
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = int((screen_width - width) / 2)
        y = int((screen_height - height) / 2)
        window.geometry(f"{width}x{height}+{x}+{y}")



    def after_koi_registered(self, koi_id):
        """
        Called after a new koi is successfully registered.
        Automatically load it into the main screen.
        """
        self.current_koi_id = koi_id
        self.search_entry.config(state=tk.NORMAL)
        self.search_entry.delete(0, tk.END)
        self.search_entry.insert(0, str(koi_id))
        self.search_koi()




    # -------------------------------
    # SHOW LEDGER RECORDS
    # -------------------------------
    def show_ledger_records(self):
        """Display XRPL transactions for the buyer wallet in the dashboard display area"""

        # Clear current display area
        for widget in self.display_frame.winfo_children():
            widget.destroy()

        tk.Label(self.display_frame, text="XRPL Ledger Records",
                 font=("Arial", 14, "bold")).pack(pady=10)

        tree_frame = tk.Frame(self.display_frame)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("type", "amount", "from", "to", "memo", "tx_hash")
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings")

        for col in columns:
            tree.heading(col, text=col.upper())
            tree.column(col, width=140)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscroll=scrollbar.set)

        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # ---------------- LOAD XRPL TRANSACTIONS ----------------
        from threading import Thread
        from xrpl.clients import JsonRpcClient
        from xrpl.models.requests import AccountTx
        from xrpl.utils import drops_to_xrp

        def fetch_xrpl():
            try:
                client = JsonRpcClient("https://s.altnet.rippletest.net:51234/")
                BUYER_ADDRESS = "rM3Eq9kfVmEYBWTVZYripuLwkkCdvhH7Zz"

                resp = client.request(AccountTx(account=BUYER_ADDRESS, limit=50))
                txs = resp.result.get("transactions", [])

                for entry in txs:
                    tx = entry.get("tx", {})
                    tx_type = tx.get("TransactionType", "")
                    from_addr = tx.get("Account", "")
                    to_addr = tx.get("Destination", "")
                    amt = tx.get("Amount")
                    if not amt:
                        amt = "N/A"

                    # Handle Amount
                    if isinstance(amt, dict):
                        # Issued currency
                        amt = f"{amt.get('value','?')} {amt.get('currency','?')}"
                    else:
                        amt = drops_to_xrp(str(amt))

                    # Extract memo if present
                    memo_text = ""
                    memos = tx.get("Memos", [])
                    for m in memos:
                        data = m.get("Memo", {})
                        hex_data = data.get("MemoData", "")
                        try:
                            memo_text += bytes.fromhex(hex_data).decode() + " | "
                        except:
                            pass

                    tree.insert("", "end", values=(tx_type, amt, from_addr, to_addr, memo_text, tx.get("hash", "")))

            except Exception as e:
                messagebox.showerror("XRPL Error", str(e))

        Thread(target=fetch_xrpl, daemon=True).start()


    # -------------------------------
    # SEARCH KOI
    # -------------------------------
    def search_koi(self):
        search_value = self.search_entry.get()
        if not search_value:
            messagebox.showerror("Error", "Enter Koi ID")
            return

        koi = self.fetch_one("""
            SELECT * FROM koi 
            WHERE koi_id=%s 
               OR koi_code=%s 
               OR standard_koi_id=%s
        """, (search_value, search_value, search_value))
                

        if koi:
            self.current_koi_id = koi["koi_id"]
            self.current_koi = koi       # <-- store full koi record
            self.search_entry.config(state=tk.DISABLED)  # Disable search while working on this koi
            self.display_koi_passport(koi)
        else:
            answer = messagebox.askyesno("Not Found", "Koi record not found. Enter new record?")
            if answer:
                open_registration_window(
                    self.root,
                    prefill_code=search_value,
                    after_register_callback=self.after_koi_registered
                )
            else:
                self.search_entry.focus_set()


    def show_qr_with_barcode(self, koi_id):
        qr_window = tk.Toplevel(self.root)
        qr_window.title("Koi QR & Barcode")
        qr_window.geometry("320x500")
        qr_window.resizable(False, False)
        self.center_popup(qr_window)

        # --- QR Code ---
        qr_img = generate_qr_image(koi_id, f"QR:{koi_id}").resize((260,260))
        qr_photo = ImageTk.PhotoImage(qr_img)
        tk.Label(qr_window, image=qr_photo).pack(pady=5)
        qr_window.qr_photo = qr_photo  # keep reference

        # --- Barcode ---
        barcode_img = self.generate_koi_barcode(koi_id)
        tk.Label(qr_window, image=barcode_img).pack(pady=5)
        qr_window.barcode_img = barcode_img

        # --- Buttons ---
        btn_frame = tk.Frame(qr_window)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Print", width=10, command=lambda: self.print_qr(qr_img)).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Close", width=10, command=qr_window.destroy).pack(side=tk.LEFT, padx=5)


    # -------------------------------
    # CLEAR DISPLAY AREA
    # -------------------------------
    def clear_display(self):
        for widget in self.display_frame.winfo_children():
            # Only destroy widgets that are NOT the Treeview
            if widget != self.tree:
                widget.destroy()
        self.clear_tree()  # remove rows but keep Treeview widget


    # -------------------------------
    # DISPLAY KOI
    # -------------------------------
    def display_koi(self, koi):
        # Recreate tree if it doesn't exist
        if not hasattr(self, "tree") or not self.tree.winfo_exists():
            self.tree = ttk.Treeview(self.display_frame)
            self.tree.pack(fill=tk.BOTH, expand=True)
            self.scrollbar = ttk.Scrollbar(self.display_frame, orient="vertical", command=self.tree.yview)
            self.tree.configure(yscrollcommand=self.scrollbar.set)
            self.scrollbar.pack(side="right", fill="y")
        self.input_frame.pack_forget()
        self.action_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
        self.clear_tree()
        columns = ("ID","Code","Name","Variety","Gender","Birth Date","Breeder","Size","Color","Owner","Status","XRPL TX","Created At")
        self.tree["columns"] = columns
        self.tree["show"] = "headings"
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=90, anchor="center")
        self.tree.insert("", tk.END, values=(
            koi["koi_id"], koi["koi_code"], koi["name"], koi["variety"], koi["gender"], str(koi["birth_date"]),
            koi["breeder_name"], koi["size_cm"], koi["color_pattern"], koi["current_owner_id"], koi["status"],
            koi["xrpl_registration_tx"], str(koi["created_at"])
        ))


    # -------------------------------
    # DISPLAY KOI PASSPORT
    # -------------------------------
    def display_koi_passport(self, koi):
        render_passport(self.display_frame, koi)

        # Make sure action buttons show after displaying the passport
        if hasattr(self, "action_frame") and self.action_frame:
            self.action_frame.pack(side=tk.TOP, fill=tk.X, pady=5)






    # -------------------------------
    # KOI BLOODLINE HELPER
    # -------------------------------
    def get_bloodline(self, koi_id):
        """Return bloodline string from koi_pedigree table for given koi_id"""
        pedigree = self.fetch_one(
            "SELECT bloodline FROM koi_pedigree WHERE koi_id=%s",
            (koi_id,)
        )
        if pedigree:
            return pedigree['bloodline']
        else:
            return "N/A"



    def generate_koi_barcode(self,koi_id):
        CODE128 = barcode.get_barcode_class('code128')
        koi_barcode = CODE128(str(koi_id), writer=ImageWriter())
        koi_barcode_file = f"temp_barcode_{koi_id}.png"
        koi_barcode.save(koi_barcode_file)
        img = Image.open(koi_barcode_file)
        return ImageTk.PhotoImage(img)


    # -------------------------------
    # SHOW QR CODE
    # -------------------------------
    def show_qr(self, pil_img):

        qr_window = tk.Toplevel(self.root)
        qr_window.title("Koi QR Code")
        qr_window.geometry("320x380")
        qr_window.resizable(False, False)

        
        # Keep track of popup
        self.open_popups.append(qr_window)

        # Resize for display
        qr_resized = pil_img.resize((260, 260))

        qr_photo = ImageTk.PhotoImage(qr_resized)

        lbl = tk.Label(qr_window, image=qr_photo)
        lbl.image = qr_photo   # important to keep reference
        lbl.pack(pady=10)

        btn_frame = tk.Frame(qr_window)
        btn_frame.pack(pady=10)

        tk.Button(
            btn_frame,
            text="Print",
            width=10,
            command=lambda: self.print_qr(pil_img)
        ).pack(side=tk.LEFT, padx=10)

        tk.Button(
            btn_frame,
            text="Close",
            width=10,
            command=qr_window.destroy
        ).pack(side=tk.LEFT, padx=10)


    def print_qr(self, pil_img):
        # Save to temp file and open system print dialog
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Image","*.png")])
        if file_path:
            pil_img.save(file_path)
            messagebox.showinfo("Print", f"QR code saved to {file_path} for printing.")


    def scan_qr(self):

        if self.current_koi_id:
            messagebox.showinfo("Info", "Close current Koi before scanning new one")
            return

        messagebox.showinfo("Scan", "Opening camera. Show QR code to webcam")

        koi_id = scan_qr_from_camera()

        if koi_id:
            self.search_entry.delete(0, tk.END)
            self.search_entry.insert(0, koi_id)
            self.search_koi()
        else:
            messagebox.showwarning("Scan Failed", "No QR code detected")


    # -------------------------------
    # HANDLE ACTION BUTTONS
    # -------------------------------
    def handle_action(self, action):
        if not self.current_koi_id:
            messagebox.showerror("Error", "No Koi loaded. Search first.")
            return

        if action == "View":
            if hasattr(self, "current_koi") and self.current_koi:
                self.display_koi_passport(self.current_koi)
            else:
                messagebox.showerror("Error", "No Koi loaded to view")

            
        if action == "Generate QR":
            messagebox.showinfo("QR", "Generating QR Code...")
            img = generate_qr_image(self.current_koi_id, f"QR:{self.current_koi_id}")
            self.show_qr(img)

        elif action == "Transfer":
            self.transfer_koi()

        elif action == "XRPL Verify":
            records = self.fetch_all("SELECT event_type, xrpl_hash, created_at FROM xrpl_transactions WHERE koi_id=%s", (self.current_koi_id,))
            if not records:
                messagebox.showinfo("XRPL Verify", "No XRPL transactions found for this Koi.")
                return
            text = "\n".join([f"{r['event_type']} | {r['xrpl_hash']} | {r['created_at']}" for r in records])
            messagebox.showinfo("XRPL Transactions", text)

        elif action == "Export":
            koi = self.fetch_one("SELECT * FROM koi WHERE koi_id=%s", (self.current_koi_id,))
            if koi:
                file = export_koi_xml(koi)
                messagebox.showinfo("Exported", f"XML saved to {file}")
            else:
                messagebox.showerror("Error", "Koi record not found for export")

        elif action == "Ownership History":
            self.show_ownership_history()

        elif action == "Health Records":
            self.show_health_records()

        elif action == "Ledger":
            self.show_ledger_records()

        elif action == "Pedigree":
            self.show_pedigree()

        elif action == "Certificates":
            self.show_certificates()






    # -------------------------------
    # TRANSFER KOI
    # -------------------------------
    def transfer_koi(self):

        if not self.current_koi_id:
            messagebox.showerror("Error", "No Koi selected")
            return

        if self.transfer_window and tk.Toplevel.winfo_exists(self.transfer_window):
            self.transfer_window.lift()
            return

        self.transfer_window = tk.Toplevel(self.root)
        self.transfer_window.title("Transfer Ownership")
        self.transfer_window.geometry("400x250")

        tk.Label(self.transfer_window, text="New Owner Org ID").pack(pady=5)
        owner_entry = tk.Entry(self.transfer_window)
        owner_entry.pack()

        tk.Label(self.transfer_window, text="Price").pack(pady=5)
        price_entry = tk.Entry(self.transfer_window)
        price_entry.pack()

        def do_transfer():
            new_owner = owner_entry.get()
            price = price_entry.get()

            if not new_owner:
                messagebox.showerror("Error", "Owner ID required")
                return

            execute(
                "UPDATE koi SET current_owner_id=%s WHERE koi_id=%s",
                (new_owner, self.current_koi_id)
            )

            execute(
                "INSERT INTO ownership_history(koi_id, to_org_id, price, transfer_date) VALUES(%s,%s,%s,NOW())",
                (self.current_koi_id, new_owner, price)
            )

            messagebox.showinfo("Success", "Ownership transferred")
            self.transfer_window.destroy()
            self.transfer_window = None

        tk.Button(self.transfer_window, text="Transfer", command=do_transfer).pack(pady=10)

        tk.Button(
            self.transfer_window,
            text="Cancel",
            command=lambda: [self.transfer_window.destroy(), setattr(self, "transfer_window", None)]
        ).pack()

    def show_ownership_history(self):
        win = tk.Toplevel(self.root)
        win.title("Ownership History")
        #win.geometry("700x400")
        self.open_popups.append(win)  # <--- track it
        self.center_popup(win, width=700, height=400)
        

        tree = ttk.Treeview(win, columns=("From Org","To Org","Date","Type","Price","XRPL TX"), show="headings")
        tree.pack(fill=tk.BOTH, expand=True)

        for col in tree["columns"]:
            tree.heading(col, text=col)
            tree.column(col, width=100)

        records = self.fetch_all("""
            SELECT 
                from_org_id, 
                to_org_id, 
                transfer_date, 
                transfer_type, 
                price, 
                xrpl_tx
            FROM ownership_history
            WHERE koi_id=%s
        """, (self.current_koi_id,))

        for r in records:
            tree.insert("", tk.END, values=(
                r["from_org_id"],
                r["to_org_id"],
                r["transfer_date"],
                r["transfer_type"],
                r["price"],
                r["xrpl_tx"]
            ))


    def show_health_records(self):
        self.clear_display()
        self.display_koi(self.current_koi)   # redraw Koi info

        title = tk.Label(self.display_frame, text="Health Records", font=("Arial", 14, "bold"))
        title.pack(pady=5)

        records = self.fetch_all(
            "SELECT record_date, size_cm, weight, vet_name, treatment, notes "
            "FROM koi_health_records WHERE koi_id=%s ORDER BY record_date DESC",
            (self.current_koi_id,)
        )

        for r in records:
            text = f"Date: {r['record_date']} | Size: {r['size_cm']} cm | Weight: {r['weight']} kg\n"
            text += f"Vet: {r['vet_name']} | Treatment: {r['treatment']}\nNotes: {r['notes']}\n"
            lbl = tk.Label(self.display_frame, text=text, justify="left", anchor="w")
            lbl.pack(fill="x", padx=10, pady=5)

        add_btn = tk.Button(
            self.display_frame,
            text="Add Health Record",
            command=self.add_health_record_popup
        )
        add_btn.pack(pady=10)


    def show_pedigree(self):
        self.clear_display()
        self.display_koi(self.current_koi)   # redraw Koi info

        title = tk.Label(self.display_frame, text="Pedigree", font=("Arial", 14, "bold"))
        title.pack(pady=5)

        p = self.fetch_one(
            "SELECT father_koi_code, mother_koi_code, bloodline, breeder "
            "FROM koi_pedigree WHERE koi_id=%s",
            (self.current_koi_id,)
        )

        if p:
            text = f"""
    Father Code: {p['father_koi_code']}
    Mother Code: {p['mother_koi_code']}
    Bloodline: {p['bloodline']}
    Breeder: {p['breeder']}
    """
            tk.Label(self.display_frame, text=text, justify="left").pack(pady=10)
        else:
            tk.Label(self.display_frame, text="No pedigree record found").pack()

        tk.Button(
            self.display_frame,
            text="Add / Update Pedigree",
            command=self.add_pedigree_popup
        ).pack(pady=10)


    def show_certificates(self):
        self.clear_display()
        self.display_koi(self.current_koi)   # redraw Koi info

        title = tk.Label(self.display_frame, text="Certificates", font=("Arial", 14, "bold"))
        title.pack(pady=5)

        records = self.fetch_all(
            "SELECT certificate_type, issued_by, issue_date, document_path "
            "FROM certificates WHERE koi_id=%s",
            (self.current_koi_id,)
        )

        for r in records:
            text = f"Type: {r['certificate_type']} | Issued By: {r['issued_by']} | Date: {r['issue_date']}"
            tk.Label(self.display_frame, text=text, anchor="w").pack(fill="x", padx=10)

        tk.Button(
            self.display_frame,
            text="Add Certificate",
            command=self.add_certificate_popup
        ).pack(pady=10)


    def add_health_record_popup(self):
        win = tk.Toplevel(self.root)
        win.title("Add Health Record")
        self.open_popups.append(win)  # <--- track it
        self.center_popup(win, width=600, height=400)

        fields = {}

        for label in ["Date (YYYY-MM-DD)", "Size (cm)", "Weight (kg)", "Vet Name", "Treatment", "Notes"]:
            tk.Label(win, text=label).pack()
            e = tk.Entry(win, width=40)
            e.pack()
            fields[label] = e

        def save():
            self.execute(
                """
                INSERT INTO koi_health_records
                (koi_id, record_date, size_cm, weight, vet_name, treatment, notes)
                VALUES (%s,%s,%s,%s,%s,%s,%s)
                """,
                (
                    self.current_koi_id,
                    fields["Date (YYYY-MM-DD)"].get(),
                    fields["Size (cm)"].get(),
                    fields["Weight (kg)"].get(),
                    fields["Vet Name"].get(),
                    fields["Treatment"].get(),
                    fields["Notes"].get()
                )
            )

            self.log_xrpl("HEALTH_UPDATE", "Added health record")
            messagebox.showinfo("Success", "Health record added!")
            win.destroy()
            self.show_health_records()

        tk.Button(win, text="Save", command=save).pack(pady=5)
        tk.Button(win, text="Cancel", command=win.destroy).pack()






    def add_pedigree_popup(self):
        win = tk.Toplevel(self.root)
        win.title("Add Pedigree")
        self.open_popups.append(win)  # <--- track it
        self.center_popup(win, width=600, height=400)

        fields = {}

        for label in ["Father Code", "Mother Code", "Bloodline", "Breeder"]:
            tk.Label(win, text=label).pack()
            e = tk.Entry(win, width=40)
            e.pack()
            fields[label] = e

        def save():
            self.execute("DELETE FROM koi_pedigree WHERE koi_id=%s", (self.current_koi_id,))

            self.execute(
                """
                INSERT INTO koi_pedigree
                (koi_id, father_koi_code, mother_koi_code, bloodline, breeder)
                VALUES (%s,%s,%s,%s,%s)
                """,
                (
                    self.current_koi_id,
                    fields["Father Code"].get(),
                    fields["Mother Code"].get(),
                    fields["Bloodline"].get(),
                    fields["Breeder"].get()
                )
            )

            self.log_xrpl("PEDIGREE", "Updated pedigree")
            messagebox.showinfo("Success", "Pedigree saved!")
            win.destroy()
            self.show_pedigree()

        tk.Button(win, text="Save", command=save).pack(pady=5)
        tk.Button(win, text="Cancel", command=win.destroy).pack()





    def add_certificate_popup(self):
        win = tk.Toplevel(self.root)
        win.title("Add Certificate")
        self.open_popups.append(win)  # <--- track it
        self.center_popup(win, width=600, height=400)

        tk.Label(win, text="Certificate Type").pack()
        type_entry = tk.Entry(win)
        type_entry.pack()

        tk.Label(win, text="Issued By").pack()
        issued_entry = tk.Entry(win)
        issued_entry.pack()

        tk.Label(win, text="Issue Date (YYYY-MM-DD)").pack()
        date_entry = tk.Entry(win)
        date_entry.pack()

        file_path = tk.StringVar()

        def choose_file():
            f = filedialog.askopenfilename()
            file_path.set(f)

        tk.Button(win, text="Choose File", command=choose_file).pack()

        def save():
            self.execute(
                """
                INSERT INTO certificates
                (koi_id, certificate_type, issued_by, issue_date, document_path)
                VALUES (%s,%s,%s,%s,%s)
                """,
                (
                    self.current_koi_id,
                    type_entry.get(),
                    issued_entry.get(),
                    date_entry.get(),
                    file_path.get()
                )
            )

            self.log_xrpl("CERTIFICATE", "Added certificate")
            messagebox.showinfo("Success", "Certificate added!")
            win.destroy()
            self.show_certificates()

        tk.Button(win, text="Save", command=save).pack(pady=5)
        tk.Button(win, text="Cancel", command=win.destroy).pack()






    def log_xrpl(self, event_type, memo):
        self.execute(
            "INSERT INTO xrpl_transactions (koi_id, event_type, memo) VALUES (%s,%s,%s)",
            (self.current_koi_id, event_type, memo)
        )


    # -------------------------------
    # CLOSE KOI (Safe Reset + Close All Popups)
    # -------------------------------
    def close_koi(self):
        # Clear current koi reference
        self.current_koi_id = None

        # Re-enable search input and focus
        if hasattr(self, "search_entry") and self.search_entry:
            self.search_entry.config(state=tk.NORMAL)
            self.search_entry.delete(0, tk.END)
            self.search_entry.focus_set()

        # Clear tree view if exists
        if hasattr(self, "tree") and self.tree and self.tree.winfo_exists():
            self.clear_tree()

        # Clear any display widgets in display_frame
        if hasattr(self, "display_frame") and self.display_frame and self.display_frame.winfo_exists():
            for widget in self.display_frame.winfo_children():
                widget.destroy()

        # Clear input frame (New Koi Entry area)
        if hasattr(self, "input_frame") and self.input_frame and self.input_frame.winfo_exists():
            for widget in self.input_frame.winfo_children():
                widget.destroy()
            self.input_frame.pack_forget()

        # Hide action buttons frame safely
        if hasattr(self, "action_frame") and self.action_frame and self.action_frame.winfo_exists():
            self.action_frame.pack_forget()

        # Close QR frame if it exists
        if hasattr(self, "qr_frame") and self.qr_frame and self.qr_frame.winfo_exists():
            self.qr_frame.destroy()
            self.qr_frame = None

        # --- Close any open popups ---
        # Track popups in a list
        if hasattr(self, "open_popups"):
            for popup in self.open_popups:
                if popup and popup.winfo_exists():
                    popup.destroy()
            self.open_popups.clear()
        else:
            self.open_popups = []

        # Ready message
        messagebox.showinfo("Closed", "Ready for new Koi search")


    # -------------------------------
    # CLEAR TREE
    # -------------------------------
    def clear_tree(self):
        try:
            if hasattr(self, "tree") and self.tree.winfo_exists():
                for row in self.tree.get_children():
                    self.tree.delete(row)
        except:
            pass

    def generate_qr_display(self):
        if not self.current_koi_id:
            messagebox.showerror("Error", "No Koi selected")
            return

        img = generate_qr_image(self.current_koi_id)
        self.qr_img_tk = ImageTk.PhotoImage(img)

        # If QR frame already exists, destroy it
        if hasattr(self, "qr_frame") and self.qr_frame:
            self.qr_frame.destroy()

        self.qr_frame = tk.Frame(self.root, bd=2, relief=tk.RIDGE, padx=10, pady=10)
        self.qr_frame.pack(pady=10)

        lbl = tk.Label(self.qr_frame, image=self.qr_img_tk)
        lbl.pack()

        btn_frame = tk.Frame(self.qr_frame)
        btn_frame.pack(pady=5)

        tk.Button(btn_frame, text="Print", command=lambda: self.print_qr(img)).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Cancel", command=self.qr_frame.destroy).pack(side=tk.LEFT, padx=5)

# -------------------------------
# RUN APP
# -------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = KoiLedgerDashboard(root)
    root.mainloop()
