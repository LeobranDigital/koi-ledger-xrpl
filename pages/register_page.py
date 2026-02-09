import tkinter as tk
from db import execute
from xrpl_service import send_xrpl_memo
from qr_service import generate_qr

class RegisterPage:

    def __init__(self):

        self.win = tk.Toplevel()
        self.win.title("Register Koi")

        tk.Label(self.win, text="Name").pack()
        self.name = tk.Entry(self.win)
        self.name.pack()

        tk.Label(self.win, text="Variety").pack()
        self.variety = tk.Entry(self.win)
        self.variety.pack()

        tk.Label(self.win, text="Owner").pack()
        self.owner = tk.Entry(self.win)
        self.owner.pack()

        tk.Button(self.win, text="Register",
                  command=self.save).pack()

    def save(self):

        execute(
            "INSERT INTO koi (name, variety, current_owner) VALUES (%s,%s,%s)",
            (self.name.get(), self.variety.get(), self.owner.get())
        )

        memo = f"REGISTER:{self.name.get()}"

        tx = send_xrpl_memo(memo)

        generate_qr(self.name.get(), tx)

        tk.Label(self.win, text="Registered on XRPL!").pack()
