import tkinter as tk
from db import get_connection
from xml_service import export_koi_xml

class ExportPage:

    def __init__(self):

        self.win = tk.Toplevel()
        self.win.title("Export XML")

        tk.Label(self.win, text="Koi ID").pack()
        self.koi = tk.Entry(self.win)
        self.koi.pack()

        tk.Button(self.win, text="Export",
                  command=self.export).pack()

    def export(self):

        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        cur.execute("SELECT * FROM koi WHERE koi_id=%s",
                    (self.koi.get(),))

        koi = cur.fetchone()

        file = export_koi_xml(koi)

        tk.Label(self.win,
                 text=f"Exported: {file}").pack()
