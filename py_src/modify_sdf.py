import xml.etree.ElementTree as ET
import colorsys
import os


def generate_modified_sdf(
    sdf_path: str, scale_factor: float, hsv_tuple: tuple = None
) -> str:
    """
    Parses an SDF file, injects scaling to geometry and poses,
    adds HSV-to-RGB color to the visual blocks, and fixes relative URIs.
    Returns the modified SDF as a string.
    """
    tree = ET.parse(sdf_path)
    root = tree.getroot()

    model_dir = os.path.dirname(os.path.abspath(sdf_path))

    for uri in root.findall(".//mesh/uri"):
        uri_text = uri.text.strip()
        if not uri_text.startswith(("file://", "model://", "https://", "/")):
            # inject the absolute file path so Gazebo finds it in memory
            uri.text = f"file://{os.path.join(model_dir, uri_text)}"

    if scale_factor != 1.0:
        for pose in root.findall(".//pose"):
            vals = pose.text.strip().split()
            if len(vals) >= 3:
                vals[0] = str(float(vals[0]) * scale_factor)  # X
                vals[1] = str(float(vals[1]) * scale_factor)  # Y
                vals[2] = str(float(vals[2]) * scale_factor)  # Z
                pose.text = " ".join(vals)

        for scale in root.findall(".//mesh/scale"):
            vals = scale.text.strip().split()
            scale.text = " ".join([str(float(v) * scale_factor) for v in vals])

        for size in root.findall(".//box/size"):
            vals = size.text.strip().split()
            size.text = " ".join([str(float(v) * scale_factor) for v in vals])

        for radius in root.findall(".//sphere/radius"):
            radius.text = str(float(radius.text) * scale_factor)

    if hsv_tuple is not None:
        h, s, v = hsv_tuple
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        rgba_str = f"{r:.3f} {g:.3f} {b:.3f} 1.0"

        for visual in root.findall(".//visual"):
            material = visual.find("material")
            if material is None:
                material = ET.SubElement(visual, "material")

            ambient = material.find("ambient")
            if ambient is None:
                ambient = ET.SubElement(material, "ambient")
            ambient.text = rgba_str

            diffuse = material.find("diffuse")
            if diffuse is None:
                diffuse = ET.SubElement(material, "diffuse")
            diffuse.text = rgba_str

    return ET.tostring(root, encoding="unicode")
