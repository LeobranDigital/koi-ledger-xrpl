import cv2
from pyzbar.pyzbar import decode

def scan_qr_from_camera():

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        return None

    koi_id = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        decoded_objects = decode(frame)

        for obj in decoded_objects:
            data = obj.data.decode("utf-8")

            # Expecting format like QR:12
            if ":" in data:
                parts = data.split(":")
                koi_id = parts[-1]
            else:
                koi_id = data

            cap.release()
            cv2.destroyAllWindows()
            return koi_id

        cv2.putText(frame, "Show QR Code to Camera", (20, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        cv2.imshow("Scan Koi QR Code", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return None
