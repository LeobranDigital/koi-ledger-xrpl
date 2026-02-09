import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from db import execute, get_connection
from datetime import datetime
from PIL import Image, ImageTk
import cv2
import os
import uuid
from xrpl_utils import jpy_to_xrp, send_xrp

BUYER_SECRET = "sEdVwTzP8iEwgPzLw5USK9LEZh6svFD"
SELLER_ADDRESS = "r3YW6YUyyby1R3qGiKbnf71V8qXfA5xGvS"

xrpl_tx_result = None
paid_currency = None

PHOTO_DIR = "koi_photos"
os.makedirs(PHOTO_DIR, exist_ok=True)


def generate_standard_id():
    conn = get_connection()
    cur = conn.cursor()

    # Just insert empty row to get auto-increment
    cur.execute("INSERT INTO koi_id_sequence () VALUES ()")
    seq_id = cur.lastrowid
    conn.commit()

    today = datetime.now().strftime("%Y%m%d")
    standard_id = f"KOI-JPN-01-{today}-{str(seq_id).zfill(4)}"

    cur.close()
    conn.close()

    return standard_id

def get_value(x):
    if isinstance(x, tk.StringVar) or isinstance(x, tk.IntVar):
        return x.get()
    elif isinstance(x, tk.Entry) or isinstance(x, ttk.Combobox):
        return x.get()
    else:
        # assume string or number already
        return x


def capture_photo_from_camera():
    cam = cv2.VideoCapture(0)
    ret, frame = cam.read()
    cam.release()

    if ret:
        filename = f"{PHOTO_DIR}/{uuid.uuid4()}.jpg"
        cv2.imwrite(filename, frame)
        return filename
    return None


def open_registration_window(root, prefill_code="", after_register_callback=None):

    win = tk.Toplevel(root)
    win.title("New Koi Registration")
    win.geometry("1000x750")

    win.transient(root)
    win.grab_set()
    win.focus_force()

    notebook = ttk.Notebook(win)
    notebook.pack(fill="both", expand=True)

    # ---------- GENERAL INFO TAB ----------
    tab1 = ttk.Frame(notebook)
    notebook.add(tab1, text="General Info")

    labels = [
        "User Provided Code",
        "Name",
        "Variety",
        "Gender",
        "Birth Date (YYYY-MM-DD)",
        "Breeder Name",
        "Size (cm)",
        "Weight (kg)",
        "Color Pattern",
        "Body Type",
        "Skin Quality",
        "Pattern Score",
        "Current Owner ID",
        "Pond Location"
    ]

    entries = {}

    body_types = ["STANDARD", "Long", "Short", "Jumbo"]
    skin_qualities = ["Excellent", "GOOD", "Average", "Poor"]

    for i, text in enumerate(labels):
        tk.Label(tab1, text=text).grid(row=i, column=0, padx=10, pady=5, sticky="e")

        if text == "Body Type":
            cb = ttk.Combobox(tab1, values=body_types, width=37)
            cb.current(0)
            cb.grid(row=i, column=1, padx=10, pady=5)
            entries[text] = cb

        elif text == "Skin Quality":
            cb = ttk.Combobox(tab1, values=skin_qualities, width=37)
            cb.current(1)
            cb.grid(row=i, column=1, padx=10, pady=5)
            entries[text] = cb

        elif text == "Pattern Score":
            e = tk.Entry(tab1, width=40)
            e.insert(0, "0")
            e.grid(row=i, column=1, padx=10, pady=5)
            entries[text] = e

        else:
            e = tk.Entry(tab1, width=40)
            e.grid(row=i, column=1, padx=10, pady=5)
            entries[text] = e

    entries["User Provided Code"].insert(0, prefill_code)

    # ---------- PURCHASE SECTION ----------

    currencies = ["JPY", "XRP"]

    tk.Label(tab1, text="Purchase Price").grid(row=len(labels), column=0, sticky="e", padx=10, pady=5)

    price_frame = tk.Frame(tab1)
    price_frame.grid(row=len(labels), column=1, padx=10, pady=5, sticky="w")

    purchase_currency = ttk.Combobox(price_frame, values=currencies, width=6)
    purchase_currency.current(0)
    purchase_currency.pack(side="left")

    purchase_entry = tk.Entry(price_frame, width=20)
    purchase_entry.pack(side="left", padx=5)

    xrp_label = tk.Label(price_frame, text="= 0 XRP")
    xrp_label.pack(side="left", padx=10)

    def update_xrp_label(event=None):
        try:
            jpy = float(purchase_entry.get())
            xrp = jpy_to_xrp(jpy)
            xrp_label.config(text=f"= {xrp} XRP")
        except:
            xrp_label.config(text="= 0 XRP")

    purchase_entry.bind("<KeyRelease>", update_xrp_label)

    entries["Purchase Price"] = (purchase_entry, purchase_currency)

    # ---------- PAY XRP BUTTON ----------

    xrpl_tx_result = None
    paid_currency = None

    def pay_xrp_action():
        nonlocal xrpl_tx_result, paid_currency

        try:
            jpy = float(purchase_entry.get())
            amount_xrp = jpy_to_xrp(jpy)

            tx_hash = send_xrp(
                from_secret=BUYER_SECRET,
                to_address=SELLER_ADDRESS,
                amount_xrp=amount_xrp
            )

            xrpl_tx_result = tx_hash
            paid_currency = "XRP"

            messagebox.showinfo(
                "XRP Payment Success",
                f"Paid {amount_xrp} XRP\nTransaction Hash:\n{tx_hash}"
            )

        except Exception as e:
            messagebox.showerror("Payment Error", str(e))


    tk.Button(price_frame, text="PAY XRP", command=pay_xrp_action).pack(side="left", padx=10)

    # ---------- CURRENT VALUE ----------

    tk.Label(tab1, text="Current Value").grid(row=len(labels)+1, column=0, sticky="e", padx=10, pady=5)

    value_frame = tk.Frame(tab1)
    value_frame.grid(row=len(labels)+1, column=1, padx=10, pady=5, sticky="w")

    value_currency = ttk.Combobox(value_frame, values=currencies, width=6)
    value_currency.current(0)
    value_currency.pack(side="left")

    value_entry = tk.Entry(value_frame, width=20)
    value_entry.pack(side="left", padx=5)

    entries["Current Value"] = (value_entry, value_currency)

    # ---------- PEDIGREE TAB ----------

    tab2 = ttk.Frame(notebook)
    notebook.add(tab2, text="Pedigree")

    pedigree = {}

    for i, text in enumerate(["Father Code", "Mother Code", "Bloodline"]):
        tk.Label(tab2, text=text).grid(row=i, column=0, padx=10, pady=10)
        e = tk.Entry(tab2, width=40)
        e.grid(row=i, column=1, padx=10, pady=10)
        pedigree[text] = e

    # ---------- PHOTOS TAB ----------

    tab3 = ttk.Frame(notebook)
    notebook.add(tab3, text="Photos")

    photos = []

    photo_list = tk.Listbox(tab3, width=80)
    photo_list.pack(pady=10)

    def upload_photo():
        f = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.png")])
        if f:
            photos.append((datetime.today().date(), f, tk.StringVar(), tk.IntVar()))
            photo_list.insert(tk.END, f)

    def capture_photo():
        f = capture_photo_from_camera()
        if f:
            photos.append((datetime.today().date(), f, tk.StringVar(), tk.IntVar()))
            photo_list.insert(tk.END, f)

    tk.Button(tab3, text="Upload Photo", command=upload_photo).pack(pady=5)
    tk.Button(tab3, text="Capture From Camera", command=capture_photo).pack(pady=5)

    # ---------- SAVE FUNCTION ----------

    def save():
        try:
            std_id = generate_standard_id()

            v = {}
            for k, e in entries.items():
                if isinstance(e, tuple):
                    entry_widget, combo_widget = e
                    v[k] = (entry_widget.get(), combo_widget.get())
                else:
                    v[k] = e.get()

            required = ["Name", "Variety", "Current Owner ID"]
            for field in required:
                if not v.get(field):
                    messagebox.showerror("Error", f"{field} is required")
                    return

            purchase_amount, purchase_curr = v["Purchase Price"]
            current_amount, current_curr = v["Current Value"]

            # OVERRIDE currency if XRP payment already done
            xrpl_tx = xrpl_tx_result

            if xrpl_tx:
                purchase_curr = "XRP"

            conn = get_connection()
            cur = conn.cursor(dictionary=True)

            cur.execute("""
                INSERT INTO koi (
                    standard_koi_id, koi_code, name, variety, gender,
                    birth_date, breeder_name, size_cm, weight_kg, color_pattern,
                    body_type, skin_quality, pattern_quality_score, current_owner_id,
                    pond_location, purchase_price, purchase_currency,
                    current_value, current_currency, xrpl_registration_tx, status
                ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'ACTIVE')
            """, (
                std_id,
                v.get("User Provided Code"),
                v.get("Name"),
                v.get("Variety"),
                v.get("Gender"),
                v.get("Birth Date (YYYY-MM-DD)"),
                v.get("Breeder Name"),
                v.get("Size (cm)"),
                v.get("Weight (kg)"),
                v.get("Color Pattern"),
                v.get("Body Type"),
                v.get("Skin Quality"),
                v.get("Pattern Score"),
                v.get("Current Owner ID"),
                v.get("Pond Location"),
                purchase_amount,
                purchase_curr,
                current_amount,
                current_curr,
                xrpl_tx
            ))

            conn.commit()

            cur.execute("SELECT LAST_INSERT_ID() as id")
            koi_id = cur.fetchone()["id"]

            # Save transaction ONLY if XRP was actually paid
            if xrpl_tx:
                cur.execute("""
                    INSERT INTO xrpl_transactions
                    (koi_id, event_type, xrpl_hash, memo)
                    VALUES (%s, %s, %s, %s)
                """, (koi_id, 'REGISTRATION', xrpl_tx, f'Paid {purchase_amount} XRP for Koi'))
                conn.commit()

            cur.close()
            conn.close()

            messagebox.showinfo(
                "Success",
                f"Koi Registered!\nStandard ID: {std_id}\nTX: {xrpl_tx}"
            )

            win.destroy()

            if after_register_callback:
                after_register_callback(std_id)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to register koi:\n{e}")



    tk.Button(win, text="REGISTER KOI", command=save).pack(pady=10)

