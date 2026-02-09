import tkinter as tk
from PIL import Image, ImageTk

def show_splash(duration=4000):
    splash = tk.Tk()
    splash.overrideredirect(True)  # remove title bar

    # Load image
    img = Image.open("images/koi.png")
    photo = ImageTk.PhotoImage(img)

    width = img.width
    height = img.height

    # Center on screen
    screen_w = splash.winfo_screenwidth()
    screen_h = splash.winfo_screenheight()
    x = (screen_w // 2) - (width // 2)
    y = (screen_h // 2) - (height // 2)

    splash.geometry(f"{width}x{height}+{x}+{y}")

    label = tk.Label(splash, image=photo)
    label.image = photo
    label.pack()

    # Close splash after duration
    splash.after(duration, splash.destroy)
    splash.mainloop()
