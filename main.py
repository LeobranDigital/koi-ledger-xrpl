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
from owner_manager import OwnerManager


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
        search_frame = tk.Frame(root)
        search_frame.pack(side=tk.TOP, fill=tk.X, pady=10)

        tk.Label(search_frame, text="Search Koi ID:").pack(side=tk.LEFT, padx=5)
        self.search_entry = tk.Entry(search_frame, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_btn = tk.Button(search_frame, text="Search", command=self.search_koi)
        self.search_btn.pack(side=tk.LEFT, padx=5)
        self.scan_btn = tk.Button(search_frame, text="Scan QR", command=self.scan_qr)
        self.scan_btn.pack(side=tk.LEFT, padx=5)

        self.owners_btn = tk.Button(search_frame, text="Owners", command=lambda: OwnerManager(self.root))
        self.owners_btn.pack(side=tk.LEFT, padx=5)


        # --- Action Buttons Frame (below search) ---
        self.action_frame = tk.Frame(root)
        self.action_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        self.action_buttons = {}
        btn_names = [
            "View", "Generate QR", "Transfer", "Ledger",
            "XRPL Verify", "Export", "Ownership History",
            "Health Records", "Pedigree", "Certificates"
        ]

        # All buttons in one row
        for name in btn_names:
            btn = tk.Button(
                self.action_frame,
                text=name,
                width=15,
                command=lambda n=name: self.handle_action(n)
            )
            btn.pack(side=tk.LEFT, padx=2, pady=2)
            self.action_buttons[name] = btn

        self.action_frame.pack_forget()  # hide initially

        # --- Optional input frame to avoid AttributeError ---
        self.input_frame = tk.Frame(root)
        self.input_frame.pack_forget()

        # --- Display Frame (fixed height) ---
        self.display_frame = tk.Frame(root, relief=tk.SUNKEN, bd=2)
        self.display_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Fix height so footer never disappears
        self.display_frame.pack_propagate(False)
        self.display_frame.config(height=500)

        # Treeview inside display frame
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

        elif action == "Owners":
            OwnerManager(self.root)






    # -------------------------------
    # TRANSFER KOI
    # -------------------------------
    def transfer_koi(self):
        if not self.current_koi_id:
            messagebox.showerror("Error", "No Koi selected")
            return

        koi = self.current_koi

        # Load current owner
        current_owner = self.fetch_one("""
            SELECT org_id, org_name, xrpl_wallet, country
            FROM organizations
            WHERE org_id=%s
        """, (koi["current_owner_id"],))

        if not current_owner:
            messagebox.showerror("Error", "Current owner information missing")
            return

        win = tk.Toplevel(self.root)
        win.title("Professional Koi Transfer")
        self.center_popup(win, 600, 550)

        # --- Current Owner Info ---
        tk.Label(win, text="CURRENT OWNER DETAILS", font=("Arial", 12, "bold")).pack(pady=5)
        tk.Label(win, text="Present Owner").pack()
        cur_owner_entry = tk.Entry(win, width=50)
        cur_owner_entry.insert(0, current_owner["org_name"])
        cur_owner_entry.config(state="readonly")
        cur_owner_entry.pack()

        tk.Label(win, text="Present Owner Wallet").pack()
        cur_wallet_entry = tk.Entry(win, width=50)
        cur_wallet_entry.insert(0, current_owner["xrpl_wallet"] or "NOT CONFIGURED")
        cur_wallet_entry.config(state="readonly")
        cur_wallet_entry.pack()

        tk.Label(win, text="Country").pack()
        cur_country = tk.Entry(win, width=50)
        cur_country.insert(0, current_owner["country"])
        cur_country.config(state="readonly")
        cur_country.pack(pady=10)

        # --- Select New Owner ---
        tk.Label(win, text="SELECT NEW OWNER", font=("Arial", 12, "bold")).pack(pady=5)
        owners = self.get_all_owners()
        owner_map = {f"{o['org_name']} (ID:{o['org_id']})": o for o in owners}
        owner_var = tk.StringVar()
        owner_combo = ttk.Combobox(win, textvariable=owner_var, values=list(owner_map.keys()), width=60)
        owner_combo.pack(pady=5)

        tk.Label(win, text="New Owner XRPL Wallet").pack()
        wallet_entry = tk.Entry(win, width=50)
        wallet_entry.pack()

        tk.Label(win, text="Buyer XRPL Secret (Demo)").pack()
        secret_entry = tk.Entry(win, width=50, show="*")
        secret_entry.pack()

        # --- Price Section ---
        tk.Label(win, text="Price in JPY").pack()
        jpy_entry = tk.Entry(win, width=20)
        jpy_entry.pack()

        tk.Label(win, text="Converted XRP").pack()
        xrp_entry = tk.Entry(win, width=20)
        xrp_entry.pack()

        def convert_to_xrp():
            try:
                jpy = float(jpy_entry.get())
                rate = 0.0028  # conversion rate demo
                xrp = round(jpy * rate, 2)
                xrp_entry.delete(0, tk.END)
                xrp_entry.insert(0, str(xrp))
            except:
                messagebox.showerror("Error", "Enter valid JPY amount")

        tk.Button(win, text="Convert JPY → XRP", command=convert_to_xrp).pack(pady=5)

        tk.Label(win, text="Transfer Reason").pack()
        reason_var = tk.StringVar()
        reason_combo = ttk.Combobox(
            win, textvariable=reason_var,
            values=["SALE", "GIFT", "AUCTION", "BREEDING LOAN"],
            state="readonly", width=40
        )
        reason_combo.pack(pady=5)

        # --- Owner select event ---
        def owner_selected(event):
            sel = owner_var.get()
            if sel in owner_map:
                wallet_entry.delete(0, tk.END)
                wallet_entry.insert(0, owner_map[sel]["xrpl_wallet"] or "")
                buyer_secret = owner_map[sel].get("xrpl_secret", "")
                secret_entry.delete(0, tk.END)
                secret_entry.insert(0, buyer_secret)
                messagebox.showinfo("Demo Only", f"Buyer secret: {buyer_secret}")

        owner_combo.bind("<<ComboboxSelected>>", owner_selected)

        # --- Execute Transfer ---
        def do_transfer():
            sel = owner_var.get()
            if not sel:
                messagebox.showerror("Error", "Please select new owner (Buyer)")
                return

            buyer = owner_map[sel]
            buyer_org_id = buyer["org_id"]
            buyer_wallet = wallet_entry.get()
            buyer_secret = secret_entry.get()
            seller_wallet = current_owner["xrpl_wallet"]

            if buyer_org_id == current_owner["org_id"]:
                messagebox.showerror("Error", "Buyer cannot be same as current owner")
                return
            if not buyer_wallet:
                messagebox.showerror("Error", "Buyer has no XRPL wallet configured")
                return
            if not buyer_secret:
                messagebox.showerror("Error", "Enter Buyer XRPL secret (for demo)")
                return
            if not seller_wallet:
                messagebox.showerror("Error", "Seller has no XRPL wallet configured")
                return

            try:
                jpy = float(jpy_entry.get())
                xrp = float(xrp_entry.get())
            except:
                messagebox.showerror("Error", "Enter valid JPY and XRP amounts")
                return

            reason = reason_var.get() or "SALE"

            confirm = messagebox.askyesno(
                "Confirm Transfer",
                f"Transfer Koi ID {self.current_koi_id}\n\n"
                f"Buyer: {buyer['org_name']}\n"
                f"Seller: {current_owner['org_name']}\n\n"
                f"JPY: {jpy}\nXRP: {xrp}\n\nProceed with payment?"
            )
            if not confirm:
                return

            from datetime import datetime
            memo = f"KOI|TRANSFER|KOI_ID:{self.current_koi_id}|BUYER:{buyer_org_id}|SELLER:{current_owner['org_id']}|JPY:{jpy}|XRP:{xrp}|REASON:{reason}|DATE:{datetime.now().date()}"

            # --- Send XRP ---
            try:
                from xrpl_utils import send_xrp
                tx_hash = send_xrp(
                    from_secret=buyer_secret,
                    to_address=seller_wallet,
                    amount_xrp=xrp,
                    memo_text=memo
                )
            except Exception as e:
                messagebox.showerror("XRPL Error", str(e))
                return

            # --- Update Koi Owner ---
            execute(
                "UPDATE koi SET current_owner_id=%s WHERE koi_id=%s",
                (buyer_org_id, self.current_koi_id)
            )

            # --- Insert Ownership History ---
            execute("""
                INSERT INTO ownership_history
                (koi_id, from_org_id, to_org_id, transfer_type, transfer_date, price, xrpl_tx)
                VALUES (%s,%s,%s,%s,NOW(),%s,%s)
            """, (
                self.current_koi_id,
                current_owner["org_id"],
                buyer_org_id,
                reason,
                jpy,
                tx_hash
            ))

            # --- Insert XRPL Transaction ---
            execute("""
                INSERT INTO xrpl_transactions
                (koi_id, event_type, xrpl_hash, memo)
                VALUES (%s,'TRANSFER',%s,%s)
            """, (
                self.current_koi_id,
                tx_hash,
                memo
            ))

            messagebox.showinfo("SUCCESS", f"Transfer Completed!\n\nXRPL TX:\n{tx_hash}")
            win.destroy()
            self.search_koi()

        tk.Button(win, text="CONFIRM TRANSFER", command=do_transfer).pack(pady=15)
        tk.Button(win, text="Cancel", command=win.destroy).pack()




    def record_koi_transfer(koi_id, from_org, to_org, price_xrp):

        memo = f"KOI|TRANSFER|{koi_id}|From {from_org} to {to_org}|{datetime.now().date()}"

        tx = send_xrp(
            from_secret=BUYER_SECRET,
            to_address=SELLER_ADDRESS,
            amount_xrp=price_xrp,
            memo_text=memo
        )

        execute("""
          INSERT INTO xrpl_transactions
          (koi_id, event_type, xrpl_hash, memo)
          VALUES (%s,'TRANSFER',%s,%s)
        """, (koi_id, tx, memo))

        execute("""
          INSERT INTO ownership_history
          (koi_id, from_org_id, to_org_id, transfer_date, xrpl_tx)
          VALUES (%s,%s,%s,CURDATE(),%s)
        """, (koi_id, from_org, to_org, tx))



        

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
        # Clear display area first
        self.clear_display()
        self.display_koi(self.current_koi)

        title = tk.Label(self.display_frame, text="Health Records", font=("Arial", 14, "bold"))
        title.pack(pady=5)

        # ---- Child Frame Container ----
        container = tk.Frame(self.display_frame)
        container.pack(fill="both", expand=True, padx=10, pady=5)

        # ---- Scrollable Canvas ----
        canvas = tk.Canvas(container, height=300)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas)

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # ---- Header Row ----
        headers = ["Date", "Size (cm)", "Weight (kg)", "Vet", "Treatment", "Notes", "Date Created"]
        for col, h in enumerate(headers):
            tk.Label(
                scroll_frame,
                text=h,
                font=("Arial", 10, "bold"),
                borderwidth=1,
                relief="solid",
                width=18
            ).grid(row=0, column=col, sticky="nsew")

        # ---- Fetch Records ----
        records = self.fetch_all(
            """
            SELECT record_date, size_cm, weight, vet_name, treatment, notes, date_created
            FROM koi_health_records
            WHERE koi_id=%s
            ORDER BY record_date DESC
            """,
            (self.current_koi_id,)
        )

        # ---- Data Rows ----
        for row_index, r in enumerate(records, start=1):
            values = [
                r["record_date"],
                r["size_cm"],
                r["weight"],
                r["vet_name"],
                r["treatment"],
                r["notes"],
                r["date_created"]
            ]
            for col, val in enumerate(values):
                tk.Label(
                    scroll_frame,
                    text=str(val),
                    borderwidth=1,
                    relief="solid",
                    width=18,
                    anchor="w"
                ).grid(row=row_index, column=col, sticky="nsew")

        # ---- Add Health Record Button (child of container, not display_frame) ----
        tk.Button(
            container,
            text="Add Health Record",
            command=self.add_health_record_popup,
            width=20,
            height=2  # ensures proper height
        ).pack(pady=10)



    def save_health_record(koi_id, size, weight, notes):

        memo = f"KOI|HEALTH|{koi_id}|Size:{size} Weight:{weight}|{datetime.now().date()}"

        tx = send_xrp(
            from_secret=BUYER_SECRET,
            to_address=SELLER_ADDRESS,
            amount_xrp=0,
            memo_text=memo
        )

        execute("""
          INSERT INTO koi_health_records
          (koi_id, record_date, size_cm, weight, notes, xrpl_tx)
          VALUES (%s, CURDATE(), %s, %s, %s, %s)
        """, (koi_id, size, weight, notes, tx))




    def show_pedigree(self):
        self.clear_display()
        self.display_koi(self.current_koi)

        title = tk.Label(self.display_frame, text="Pedigree Records", font=("Arial", 14, "bold"))
        title.pack(pady=5)

        # ---- Container ----
        container = tk.Frame(self.display_frame)
        container.pack(fill="both", expand=True, padx=10, pady=5)

        canvas = tk.Canvas(container, height=250)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas)

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # ---- Header Row ----
        headers = ["Status", "Father", "Mother", "Bloodline", "Breeder", "date_created"]

        for col, h in enumerate(headers):
            tk.Label(
                scroll_frame,
                text=h,
                font=("Arial", 10, "bold"),
                borderwidth=1,
                relief="solid",
                width=20
            ).grid(row=0, column=col, sticky="nsew")

        # ---- Fetch Records (Latest First) ----
        records = self.fetch_all(
            """
            SELECT pedigree_id, father_koi_code, mother_koi_code, bloodline, breeder, date_created
            FROM koi_pedigree
            WHERE koi_id=%s
            ORDER BY pedigree_id DESC
            """,
            (self.current_koi_id,)
        )

        # ---- Display Rows ----
        for row_index, r in enumerate(records, start=1):

            # First record = latest
            status = "CURRENT" if row_index == 1 else "OLD"

            values = [
                status,
                r["father_koi_code"],
                r["mother_koi_code"],
                r["bloodline"] if r["bloodline"] else "-",
                r["breeder"] if r["breeder"] else "-",
                r["date_created"] if r["date_created"] else "-"
            ]

            for col, val in enumerate(values):
                tk.Label(
                    scroll_frame,
                    text=str(val),
                    borderwidth=1,
                    relief="solid",
                    width=20,
                    anchor="w"
                ).grid(row=row_index, column=col, sticky="nsew")

        # ---- Add Health Record Button (child of container, not display_frame) ----
        tk.Button(
            container,
            text="Add / Update Pedigree",
            command=self.add_pedigree_popup,
            width=20,
            height=2  # ensures proper height
        ).pack(pady=10)


    def show_certificates(self):
        self.clear_display()
        self.display_koi(self.current_koi)

        title = tk.Label(self.display_frame, text="Certificates", font=("Arial", 14, "bold"))
        title.pack(pady=5)

        container = tk.Frame(self.display_frame)
        container.pack(fill="both", expand=True, padx=10, pady=5)

        canvas = tk.Canvas(container, height=250)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas)

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # ---- Header ----
        headers = ["Type", "Issued By", "Issue Date", "Document Path", "XRPL TX", "Date Created"]

        for col, h in enumerate(headers):
            tk.Label(
                scroll_frame,
                text=h,
                font=("Arial", 10, "bold"),
                borderwidth=1,
                relief="solid",
                width=18
            ).grid(row=0, column=col, sticky="nsew")

        # ---- Fetch Records (Latest First) ----
        records = self.fetch_all(
            """
            SELECT certificate_type, issued_by, issue_date, document_path, xrpl_tx, date_created
            FROM certificates
            WHERE koi_id=%s
            ORDER BY certificate_id DESC
            """,
            (self.current_koi_id,)
        )

        # ---- Display Rows ----
        for row_index, r in enumerate(records, start=1):

            values = [
                r["certificate_type"],
                r["issued_by"],
                r["issue_date"],
                r["document_path"],
                r["xrpl_tx"] if r["xrpl_tx"] else "-",
                r["date_created"]
            ]

            for col, val in enumerate(values):
                tk.Label(
                    scroll_frame,
                    text=str(val),
                    borderwidth=1,
                    relief="solid",
                    width=18,
                    anchor="w"
                ).grid(row=row_index, column=col, sticky="nsew")


        # ---- Add Health Record Button (child of container, not display_frame) ----
        tk.Button(
            container,
            text="Add Certificate",
            command=self.add_certificate_popup,
            width=20,
            height=2  # ensures proper height
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
        win.title("Add Pedigree Record")
        self.open_popups.append(win)
        self.center_popup(win, width=600, height=400)

        fields = {}

        for label in ["Father Code", "Mother Code", "Bloodline", "Breeder"]:
            tk.Label(win, text=label).pack()
            e = tk.Entry(win, width=40)
            e.pack()
            fields[label] = e

        def save():

            # ✅ DO NOT DELETE OLD RECORDS
            # ✅ Always INSERT new record

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

            # Optional XRPL log (do NOT say "Updated")
            self.log_xrpl("PEDIGREE", "Added new pedigree record")

            messagebox.showinfo("Success", "Pedigree record added!")
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


    def get_all_owners(self):
        return self.fetch_all(
            "SELECT org_id, org_name, xrpl_wallet, xrpl_secret FROM organizations ORDER BY org_name",
            ()
        )


    def is_valid_xrpl(self, address):
        import re
        pattern = r"^r[1-9A-HJ-NP-Za-km-z]{24,34}$"
        return bool(re.match(pattern, address))


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
