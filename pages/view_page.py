import tkinter as tk
from db import get_connection

class ViewPage:

    def __init__(self):

        self.win = tk.Toplevel()
        self.win.title("View Koi")

        tk.Label(self.win, text="Koi ID").pack()
        self.koi_id = tk.Entry(self.win)
        self.koi_id.pack()

        tk.Button(self.win, text="View",
                  command=self.view).pack()

    def view(self):

        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        cur.execute("SELECT * FROM koi WHERE koi_id=%s",
                    (self.koi_id.get(),))

        koi = cur.fetchone()

        tk.Label(self.win,
                 text=str(koi)).pack()
