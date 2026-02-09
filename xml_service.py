import xml.etree.ElementTree as ET

def export_koi_xml(koi):
    root = ET.Element("Koi")

    for key, value in koi.items():
        ET.SubElement(root, key).text = str(value)

    file_name = f"koi_{koi['koi_id']}.xml"
    tree = ET.ElementTree(root)
    tree.write(file_name)

    return file_name
