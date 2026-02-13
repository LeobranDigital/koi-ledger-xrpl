import tkinter as tk
from tkinter import ttk, messagebox
from db import get_connection, execute

import re

# XRPL Libraries
from xrpl.clients import JsonRpcClient
from xrpl.wallet import Wallet
from xrpl.models.requests import AccountInfo


TESTNET_URL = "https://s.altnet.rippletest.net:51234/"


class OwnerManager:

    def __init__(self, root):
        self.root = root
        self.window = tk.Toplevel(root)
        self.window.title("Owner Management")
        self.window.geometry("800x500")
        
        self.generated_seed = None


        self.build_ui()
        self.load_owners()


    def build_ui(self):
        frame = tk.Frame(self.window)
        frame.pack(fill=tk.BOTH, expand=True)

        columns = ("ID", "Name", "Type", "Country", "Email", "Wallet")

        self.tree = ttk.Treeview(frame, columns=columns, show="headings")

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)

        self.tree.pack(fill=tk.BOTH, expand=True)

        btn_frame = tk.Frame(self.window)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Add Owner", command=self.add_owner).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Edit Owner", command=self.edit_owner).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Refresh", command=self.load_owners).pack(side=tk.LEFT, padx=5)


    def load_owners(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        cur.execute("""
            SELECT org_id, org_name, org_type, country, contact_email, xrpl_wallet
            FROM organizations
        """)

        for r in cur.fetchall():
            self.tree.insert("", tk.END, values=(
                r["org_id"],
                r["org_name"],
                r["org_type"],
                r["country"],
                r["contact_email"],
                r["xrpl_wallet"]
            ))

        cur.close()
        conn.close()


    def add_owner(self):
        OwnerForm(self.window, refresh_callback=self.load_owners)


    def edit_owner(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showerror("Error", "Select an owner first")
            return

        data = self.tree.item(sel[0])["values"]
        OwnerForm(self.window, owner_id=data[0], refresh_callback=self.load_owners)





class OwnerForm:

    OWNER_TYPES = ["BREEDER", "DEALER", "COLLECTOR", "AUCTION"]

    def __init__(self, parent, owner_id=None, refresh_callback=None):
        self.owner_id = owner_id
        self.refresh_callback = refresh_callback

        self.win = tk.Toplevel(parent)

        # Keep owner form on top of dashboard
        self.win.transient(parent)
        self.win.grab_set()
        self.win.lift()
        self.win.focus_force()

        self.win.title("Owner Details")
        self.win.geometry("450x560")

        self.entries = {}

        tk.Label(self.win, text="Organization Name").pack()
        e = tk.Entry(self.win, width=40)
        e.pack(pady=5)
        self.entries["Organization Name"] = e

        tk.Label(self.win, text="Owner Type").pack()
        self.type_var = tk.StringVar()
        type_combo = ttk.Combobox(
            self.win,
            textvariable=self.type_var,
            values=self.OWNER_TYPES,
            state="readonly",
            width=37
        )
        type_combo.pack(pady=5)
        self.entries["Owner Type"] = type_combo

        tk.Label(self.win, text="Country").pack()
        e = tk.Entry(self.win, width=40)
        e.pack(pady=5)
        self.entries["Country"] = e

        tk.Label(self.win, text="Email").pack()
        e = tk.Entry(self.win, width=40)
        e.pack(pady=5)
        self.entries["Email"] = e

        tk.Label(self.win, text="Phone").pack()
        e = tk.Entry(self.win, width=40)
        e.pack(pady=5)
        self.entries["Phone"] = e

        tk.Label(self.win, text="XRPL Wallet Address").pack()
        e = tk.Entry(self.win, width=40)
        e.pack(pady=5)
        self.entries["XRPL Wallet"] = e

        tk.Button(
            self.win,
            text="Fetch XRPL Wallet",
            command=self.fetch_wallet
        ).pack(pady=5)

        tk.Button(
            self.win,
            text="Verify Wallet on XRPL",
            command=self.verify_wallet
        ).pack(pady=5)

        tk.Button(self.win, text="Save Owner", command=self.save).pack(pady=15)

        if owner_id:
            self.load_owner()


    def validate_email(self, email):
        pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        return re.match(pattern, email)

    def validate_xrpl_wallet(self, address):
        if not address:
            return False
        pattern = r"^r[1-9A-HJ-NP-Za-km-z]{24,34}$"
        return re.match(pattern, address)

    def validate_phone(self, phone):
        if not phone:
            return True
        pattern = r"^[0-9\-\+\s]{7,20}$"
        return re.match(pattern, phone)


    def fetch_wallet(self):

        try:
            existing_wallet = self.entries["XRPL Wallet"].get().strip()

            if existing_wallet:
                confirm = messagebox.askyesno(
                    "Confirm Replace Wallet",
                    f"This owner already has an XRPL Wallet:\n\n{existing_wallet}\n\n"
                    "Are you SURE you want to generate and replace it with a new wallet?\n\n"
                    "This action cannot be undone."
                )

                if not confirm:
                    self.win.lift()
                    self.win.focus_force()
                    return

            new_wallet = Wallet.create()
            wallet_address = new_wallet.classic_address
            
            self.generated_seed = new_wallet.seed


            self.entries["XRPL Wallet"].delete(0, tk.END)
            self.entries["XRPL Wallet"].insert(0, wallet_address)

            if self.owner_id:

                execute("""
                    UPDATE organizations
                    SET xrpl_wallet=%s,
                        xrpl_secret=%s
                    WHERE org_id=%s

                """, (wallet_address, self.generated_seed, self.owner_id))

                messagebox.showinfo(
                    "Wallet Created & Saved",
                    f"New XRPL Wallet successfully assigned.\n\n"
                    f"Address:\n{wallet_address}\n\n"
                    f"SECRET KEY (SAVE THIS SAFELY!):\n{new_wallet.seed}\n\n"
                    "This secret key will NOT be shown again."
                )

                self.win.lift()
                self.win.focus_force()

                if self.refresh_callback:
                    self.refresh_callback()

            else:
                messagebox.showinfo(
                    "New XRPL Wallet Created",
                    f"Wallet generated successfully.\n\n"
                    f"Address:\n{wallet_address}\n\n"
                    "It will be saved when you press SAVE OWNER.\n\n"
                    f"SECRET KEY (SAVE THIS SAFELY!):\n{new_wallet.seed}"
                )

                self.win.lift()
                self.win.focus_force()

        except Exception as e:
            messagebox.showerror("XRPL Error", str(e))
            self.win.lift()
            self.win.focus_force()



    def verify_wallet(self):

        address = self.entries["XRPL Wallet"].get().strip()

        if not self.validate_xrpl_wallet(address):
            messagebox.showerror("Error", "Invalid XRPL wallet format")
            self.win.lift()
            self.win.focus_force()
            return

        try:
            client = JsonRpcClient(TESTNET_URL)

            req = AccountInfo(account=address)
            client.request(req)

            messagebox.showinfo(
                "Wallet Verified",
                "This XRPL wallet exists on the network."
            )

            # keep owner window on top
            self.win.lift()
            self.win.focus_force()

        except Exception:
            messagebox.showwarning(
                "Not Found",
                "Wallet not found on XRPL Testnet.\n\n"
                "It may be new and not activated yet."
            )

            self.win.lift()
            self.win.focus_force()



    def load_owner(self):
        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        cur.execute("SELECT * FROM organizations WHERE org_id=%s", (self.owner_id,))
        o = cur.fetchone()

        cur.close()
        conn.close()

        if not o:
            messagebox.showerror("Error", "Owner not found")
            return

        def safe_insert(field, value):
            widget = self.entries[field]
            if isinstance(widget, ttk.Combobox):
                widget.set(str(value or ""))
            else:
                widget.delete(0, tk.END)
                widget.insert(0, str(value or ""))

        safe_insert("Organization Name", o.get("org_name"))
        safe_insert("Owner Type", o.get("org_type"))
        safe_insert("Country", o.get("country"))
        safe_insert("Email", o.get("contact_email"))
        safe_insert("Phone", o.get("phone"))
        safe_insert("XRPL Wallet", o.get("xrpl_wallet"))


    def save(self):

        name = self.entries["Organization Name"].get().strip()
        typ = self.type_var.get().strip()
        country = self.entries["Country"].get().strip()
        email = self.entries["Email"].get().strip()
        phone = self.entries["Phone"].get().strip()
        wallet = self.entries["XRPL Wallet"].get().strip()

        if not name:
            messagebox.showerror("Validation Error", "Organization Name is required")
            return

        if typ not in self.OWNER_TYPES:
            messagebox.showerror("Validation Error", "Please select valid Owner Type")
            return

        if email and not self.validate_email(email):
            messagebox.showerror("Validation Error", "Invalid email format")
            return

        if wallet and not self.validate_xrpl_wallet(wallet):
            messagebox.showerror("Validation Error", "Invalid XRPL Wallet Address format")
            return

        if phone and not self.validate_phone(phone):
            messagebox.showerror("Validation Error", "Invalid phone format")
            return

        if self.owner_id:
            execute("""
                UPDATE organizations
                SET org_name=%s,
                    org_type=%s,
                    country=%s,
                    contact_email=%s,
                    phone=%s,
                    xrpl_wallet=%s,
                    xrpl_secret=COALESCE(%s, xrpl_secret)

                WHERE org_id=%s
            """, (name, typ, country, email, phone, wallet, self.generated_seed, self.owner_id))
        else:
            execute("""
                INSERT INTO organizations
                (org_name, org_type, country, contact_email, phone, xrpl_wallet, xrpl_secret)
                VALUES (%s,%s,%s,%s,%s,%s,%s)
            """, (name, typ, country, email, phone, wallet, self.generated_seed))

        messagebox.showinfo("Saved", "Owner saved successfully")

        self.win.destroy()

        if self.refresh_callback:
            self.refresh_callback()
