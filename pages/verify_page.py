import tkinter as tk

class VerifyPage:

    def __init__(self):

        self.win = tk.Toplevel()
        self.win.title("XRPL Verify")

        tk.Label(self.win, text="Transaction Hash").pack()

        self.tx = tk.Entry(self.win)
        self.tx.pack()

        tk.Button(self.win, text="Verify").pack()

        tk.Label(self.win,
                 text="(Demo Verification)").pack()
