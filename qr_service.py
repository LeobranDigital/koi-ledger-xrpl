# qr_service.py
import qrcode
from PIL import Image

def generate_qr_image(koi_id, text=None):
    """
    Generates a QR code as a PIL Image object for the given koi_id.
    Optionally, you can include text to encode other info (like REGISTER:Name)
    """
    if text is None:
        text = f"KOI:{koi_id}"

    qr = qrcode.QRCode(
        version=2,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    return img
