import subprocess
import os
from pathlib import Path
from PIL import Image

def main():
    root = Path(__file__).resolve().parent.parent
    svg_path = root / "assets" / "logos" / "jisr-logo-3-geometric-infinity.svg"
    temp_html = root / "scripts" / "render_logo.html"
    master_png = root / "assets" / "logos" / "jisr-logo-3-512.png"

    # 1. Create clean HTML wrapper with zero margin
    html_content = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  html, body {{ width: 512px; height: 512px; overflow: hidden; background: transparent; }}
  img {{ width: 512px; height: 512px; display: block; }}
</style>
</head>
<body>
  <img src="{svg_path.as_uri()}" width="512" height="512">
</body>
</html>"""
    temp_html.parent.mkdir(parents=True, exist_ok=True)
    temp_html.write_text(html_content, encoding="utf-8")

    # 2. Render 512x512 PNG via Chrome headless
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    cmd = [
        chrome_path,
        "--headless",
        "--disable-gpu",
        "--default-background-color=00000000",
        "--window-size=512,512",
        f"--screenshot={master_png}",
        temp_html.as_uri()
    ]
    print(f"Rendering master PNG via Chrome headless to {master_png}...")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print("Chrome error:", res.stderr)
        return

    if not master_png.exists():
        print("Failed to generate master PNG")
        return

    print("Master PNG generated successfully:", master_png.stat().st_size, "bytes")

    # 3. Use PIL Lanczos resampling to create all Android mipmap launcher icons
    img = Image.open(master_png).convert("RGBA")
    
    # Crop to exact 512x512 if necessary
    if img.size != (512, 512):
        img = img.resize((512, 512), Image.Resampling.LANCZOS)
        img.save(master_png)

    # Copy to root and mobile assets
    img.save(root / "mobile" / "assets" / "icon.png")

    mipmap_dirs = {
        "mipmap-mdpi": 48,
        "mipmap-hdpi": 72,
        "mipmap-xhdpi": 96,
        "mipmap-xxhdpi": 144,
        "mipmap-xxxhdpi": 192,
    }

    res_dir = root / "mobile" / "android" / "app" / "src" / "main" / "res"
    for folder, size in mipmap_dirs.items():
        out_path = res_dir / folder / "ic_launcher.png"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        resized = img.resize((size, size), Image.Resampling.LANCZOS)
        resized.save(out_path, format="PNG")
        print(f"Generated {folder}/ic_launcher.png ({size}x{size})")

    if temp_html.exists():
        temp_html.unlink()
    print("All Android app icons generated successfully!")

if __name__ == "__main__":
    main()
