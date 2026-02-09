import tkinter as tk
from db import execute
from xrpl_service import send_xrpl_memo

class TransferPage:

    def __init__(self):

        self.win = tk.Toplevel()
        self.win.title("Transfer Ownership")

        tk.Label(self.win, text="Koi ID").pack()
        self.koi = tk.Entry(self.win)
        self.koi.pack()

        tk.Label(self.win, text="New Owner").pack()
        self.owner = tk.Entry(self.win)
        self.owner.pack()

        tk.Button(self.win, text="Transfer",
                  command=self.transfer).pack()

    def transfer(self):

        execute(
            "UPDATE koi SET current_owner=%s WHERE koi_id=%s",
            (self.owner.get(), self.koi.get())
        )

        send_xrpl_memo(f"TRANSFER:{self.koi.get()}->{self.owner.get()}")

        tk.Label(self.win, text="Ownership Transferred").pack()
