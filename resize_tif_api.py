from pathlib import Path
from PIL import Image

def resize_tif_by_width_mm(path_in, path_out, width_mm, dpi=300):
    """Resize one TIFF proportionally to a target width (in mm)."""
    img = Image.open(path_in)
    w_px, h_px = img.size
    target_w_px = int(width_mm / 25.4 * dpi)
    target_h_px = int(target_w_px * h_px / w_px)
    resized = img.resize((target_w_px, target_h_px), Image.LANCZOS)
    resized.save(path_out, dpi=(dpi, dpi))
    img.close()

# --- Configuration ---
input_dir = Path("pic_tif")
input_dir.mkdir(exist_ok=True)

output_dir = input_dir / "resize"
output_dir.mkdir(exist_ok=True)

target_width_mm = 123  # desired width in millimeters
dpi = 300              # print resolution

# --- Loop through all TIFF files ---
for tif_path in input_dir.glob("*.tif"):
    output_path = output_dir / tif_path.name
    resize_tif_by_width_mm(tif_path, output_path, target_width_mm, dpi)
    print(f"✅ Resized: {tif_path.name}")

