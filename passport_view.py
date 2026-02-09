import tkinter as tk
from PIL import Image, ImageTk, ImageGrab
import qrcode
from barcode import Code128
from barcode.writer import ImageWriter
import io
from datetime import datetime
from reportlab.pdfgen import canvas as pdfcanvas
from reportlab.lib.pagesizes import letter
import os
from db import get_connection  # assuming you have get_connection from your main.py

import tempfile


# ------------------------
# Helper: Convert Passport Frame to Image
# ------------------------
def passport_to_image(passport_frame):
    # Update GUI to ensure everything is drawn
    passport_frame.update()
    x = passport_frame.winfo_rootx()
    y = passport_frame.winfo_rooty()
    w = passport_frame.winfo_width()
    h = passport_frame.winfo_height()
    img = ImageGrab.grab(bbox=(x, y, x + w, y + h))
    return img
    
# ------------------------
# Utility functions
# ------------------------
def calculate_age(birth_date):
    try:
        birth = datetime.strptime(str(birth_date), "%Y-%m-%d")
        today = datetime.today()
        years = today.year - birth.year
        months = today.month - birth.month
        if months < 0:
            years -= 1
            months += 12
        return f"{years} years {months} months"
    except:
        return "Unknown"

def generate_barcode(koi_id):
    rv = io.BytesIO()
    barcode = Code128(str(koi_id), writer=ImageWriter())
    barcode.write(rv)
    rv.seek(0)
    return Image.open(rv)

def generate_qr(koi):
    data = f"""
    KOI PASSPORT
    ID: {koi.get('koi_id')}
    Name: {koi.get('name')}
    Variety: {koi.get('variety')}
    Owner: {koi.get('current_owner_id')}
    """
    qr = qrcode.make(data)
    return qr

def capture_passport(canvas):
    """
    Capture only the passport area from the Tkinter canvas.
    'canvas' is your passport Canvas widget.
    Returns a PIL Image of the passport.
    """
    # Get canvas position on the screen
    x_root = canvas.winfo_rootx()
    y_root = canvas.winfo_rooty()
    width = canvas.winfo_width()
    height = canvas.winfo_height()

    # Adjust for inner passport frame size if needed
    # For example, if your passport is inside a frame with padding,
    # subtract padding from x_root/y_root or width/height

    bbox = (x_root, y_root, x_root + width, y_root + height)
    img = ImageGrab.grab(bbox=bbox)
    return img
    
def format_mrz_line1(koi):
    # Line 1: document type, country, variety, name
    doc_type = "KP"  # Koi Passport
    country = "JPN"
    variety = koi.get("variety", "").upper()
    name = koi.get("name", "").upper()
    
    # Combine with << separators
    line = f"{doc_type}<" + f"{country}<<" + f"{variety}<<" + f"{name}"
    
    # Fill remaining space with '<' to make exactly 44 chars
    if len(line) < 44:
        line += "<" * (44 - len(line))
    else:
        line = line[:44]  # truncate if too long
    
    return line

def format_mrz_line2(koi):
    # Line 2: Koi ID, country code, birth date
    koi_id = str(koi.get("koi_id")).upper()
    country = "JPN"
    birth_date = str(koi.get("birth_date")).replace("-", "")
    
    line = koi_id + country + birth_date
    
    if len(line) < 44:
        line += "<" * (44 - len(line))
    else:
        line = line[:44]
    
    return line

    
    
# ------------------------
# Passport Rendering
# ------------------------
def render_passport(frame, koi):
    for w in frame.winfo_children():
        w.destroy()

    outer = tk.Frame(frame, bg="gray")
    outer.pack(expand=True)

    passport = tk.Frame(outer, bg="#F5EAD6", bd=2, relief="solid")
    passport.pack(padx=5, pady=5)

    canvas = tk.Canvas(passport, width=860, height=420, bg="#F5EAD6", highlightthickness=0)
    canvas.pack()

    # Outer border
    canvas.create_rectangle(10, 10, 850, 410, outline="black", width=2)

    # ---- PASSPORT TITLE ABOVE PHOTO (LEFT SIDE) ----
    canvas.create_text(140, 40, text="旅券", font=("Times", 18, "bold"), fill="#8B0000")
    canvas.create_text(140, 65, text="KOI PASSPORT", font=("Times", 18, "bold"), fill="#8B0000")

    # ---- Top Right Fields (same row) ----
    canvas.create_text(280, 50, text="種類 / Type", font=("Arial", 9), anchor="w")
    canvas.create_text(280, 75, text="KP", font=("Arial", 11, "bold"), anchor="w")

    canvas.create_text(360, 50, text="発行国 / Issuing Country", font=("Arial", 9), anchor="w")
    canvas.create_text(360, 75, text="JAPAN", font=("Arial", 11, "bold"), anchor="w")

    canvas.create_text(520, 50, text="旅券番号 / Passport No", font=("Arial", 9), anchor="w")
    canvas.create_text(520, 75, text=f"K-{koi.get('koi_id')}", font=("Arial", 11, "bold"), anchor="w")


    # ---- PHOTO LEFT ----


    # ---- PHOTO LEFT ----
    photo_x1, photo_y1 = 40, 90
    photo_x2, photo_y2 = 240, 290
    canvas.create_rectangle(photo_x1, photo_y1, photo_x2, photo_y2, outline="black")

    # Determine photo path
    photo_path = None

    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT photo_path 
            FROM koi_photos 
            WHERE koi_id=%s 
            ORDER BY main_photo DESC, record_date DESC 
            LIMIT 1
        """, (koi.get("koi_id"),))
        row = cur.fetchone()
        if row and row["photo_path"]:
            photo_path = row["photo_path"]
        cur.close()
        conn.close()
    except Exception as e:
        print("Error fetching koi photo:", e)

    # Fallback if no photo found
    if not photo_path or not os.path.exists(photo_path):
        photo_path = "koi_photos/No_Koi.png"

    try:
        img = Image.open(photo_path)
        img = img.resize((photo_x2 - photo_x1 - 20, photo_y2 - photo_y1 - 20))  # fit inside box
        img_tk = ImageTk.PhotoImage(img)
        canvas.image = img_tk  # keep reference
        canvas.create_image((photo_x1 + photo_x2)//2, (photo_y1 + photo_y2)//2, image=img_tk)
    except Exception as e:
        canvas.create_text((photo_x1 + photo_x2)//2, (photo_y1 + photo_y2)//2, text="ERROR LOADING PHOTO")

    canvas.create_text((photo_x1 + photo_x2)//2, photo_y2 + 15, text="画像 / FISH PHOTO", font=("Arial", 9))


    # ---- QR TOP RIGHT (Transparent BG) ----
    try:
        qr = generate_qr(koi).convert("RGBA")
        qr = qr.resize((80, 80))
        qr_img = ImageTk.PhotoImage(qr)
        canvas.qr = qr_img
        canvas.create_image(780, 80, image=qr_img)
    except:
        canvas.create_text(780, 80, text="QR ERROR")

    # ---- BARCODE BELOW QR (Transparent BG) ----
    try:
        barcode = generate_barcode(koi.get("koi_id")).convert("RGBA")
        barcode = barcode.resize((120, 40))
        bc_img = ImageTk.PhotoImage(barcode)
        canvas.bc = bc_img
        canvas.create_image(780, 150, image=bc_img)
    except:
        canvas.create_text(780, 150, text="BARCODE ERROR")

    # ---- INFORMATION AREA ----
    x = 280
    y = 100
    gap = 38

    def draw(jp, en, value):
        nonlocal y
        canvas.create_text(x, y, text=f"{jp} / {en}", anchor="w", font=("Arial", 9))
        canvas.create_text(x, y + 18, text=str(value), anchor="w", font=("Arial", 12, "bold"))
        y += gap

    draw("姓", "Surname", koi.get("breeder_name"))
    draw("名", "Given Name", koi.get("name"))

    canvas.create_text(x, y, text="国籍 / Nationality", anchor="w", font=("Arial", 9))
    canvas.create_text(x, y + 18, text="KOI", anchor="w", font=("Arial", 12, "bold"))

    canvas.create_text(x + 240, y, text="生年月日 / Date of Birth", anchor="w", font=("Arial", 9))
    canvas.create_text(x + 240, y + 18, text=koi.get("birth_date"), anchor="w", font=("Arial", 12, "bold"))

    y += gap

    canvas.create_text(x, y, text="性別 / Sex", anchor="w", font=("Arial", 9))
    canvas.create_text(x, y + 18, text=koi.get("gender"), anchor="w", font=("Arial", 12, "bold"))

    canvas.create_text(x + 240, y, text="登録地 / Registered Domicile", anchor="w", font=("Arial", 9))
    canvas.create_text(x + 240, y + 18, text=koi.get("current_owner_id"), anchor="w", font=("Arial", 12, "bold"))

    y += gap

    canvas.create_text(x, y, text="発行日 / Date of Issue", anchor="w", font=("Arial", 9))
    canvas.create_text(x, y + 18, text=koi.get("created_at"), anchor="w", font=("Arial", 12, "bold"))

    canvas.create_text(x + 240, y, text="署名 / Signature", anchor="w", font=("Arial", 9))
    canvas.create_text(x + 240, y + 18, text="DIGITAL", anchor="w", font=("Arial", 12, "bold"))

    y += gap
    draw("発行機関", "Authority", "KOI LEDGER REGISTRY")

    # ---- MRZ (MVR) AT BOTTOM – FULL WIDTH ----
    # mrz1 = f"KP<JPN<<{koi.get('variety','').upper()}<<{koi.get('name','').upper()}<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"
    # mrz2 = f"{koi.get('koi_id')}JPN{str(koi.get('birth_date')).replace('-','')}<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"
    
    mrz1 = format_mrz_line1(koi)
    mrz2 = format_mrz_line2(koi)

    canvas.create_text(40, 350, text=mrz1, anchor="w", font=("Courier", 16))
    canvas.create_text(40, 375, text=mrz2, anchor="w", font=("Courier", 16))

    # ---- ACTION BUTTONS BELOW BORDER ----
    btn_frame = tk.Frame(passport, bg="#F5EAD6")
    btn_frame.place(x=10, y=390)  # Just below bottom border

    def print_passport():
        img = passport_to_image(passport)
        img.show()  # You can integrate with printer API here

    def save_pdf():
        img = passport_to_image(passport)
        pdf_file = f"KoiPassport_{koi.get('koi_id')}.pdf"
        img_path = os.path.join(tempfile.gettempdir(), "temp_passport.png")
        img.save(img_path)

        c = pdfcanvas.Canvas(pdf_file, pagesize=letter)
        # Resize to fit page width
        page_width, page_height = letter
        c.drawImage(img_path, 50, 300, width=page_width-100, preserveAspectRatio=True, mask='auto')
        c.save()
        tk.messagebox.showinfo("PDF Saved", f"{pdf_file} created!")

    def share_passport():
        img = passport_to_image(passport)
        save_path = f"KoiPassport_{koi.get('koi_id')}.png"
        img.save(save_path)
        tk.messagebox.showinfo("Share", f"Passport saved as {save_path}.\nYou can now share it.")

    tk.Button(btn_frame, text="Print Passport", command=print_passport).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Save as PDF", command=save_pdf).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Share Passport", command=share_passport).pack(side=tk.LEFT, padx=5)
