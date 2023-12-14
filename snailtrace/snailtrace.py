import subprocess
import os

import httpx
from PIL import Image

def ensure_assets_dir(cwd=None):
    assets_path = os.path.join(cwd or os.getcwd(), "assets")
    if not os.path.isdir(assets_path):
        os.mkdir(assets_path)
    return os.path.realpath(assets_path)

def fetch_image(url: str, force=False) -> str:
    try:
        filename = url.split("/")[-1]
        assets_path = ensure_assets_dir()
        filepath = os.path.realpath(os.path.join(assets_path, filename))
        if os.path.isfile(filepath) and not force:
            print(f"Target file {filepath} exists. Pass force=True to ignore.")
            return filepath
        image_response = httpx.get(url, timeout=None).raise_for_status()
        with open(filepath, "wb") as fp:
            fp.write(image_response.content)
        return filepath
    except Exception as e:
        print("Error while downloading image:", e)
        return ""

def png_to_pbm(input_image_path):
    with Image.open(input_image_path) as img:
        if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3]) # 3 is the index of the alpha channel
            img = background

        img = img.convert('RGB')
        output_path = input_image_path.rsplit('.', 1)[0] + '.pbm'
        img.save(output_path, 'PPM')
        return output_path

def convert_to_svg(input_image_path, output_svg_path):
    image_path = input_image_path if input_image_path.endswith(".pbm") else png_to_pbm(input_image_path)
    
    command = ['potrace', image_path, '-s', '-o', output_svg_path]
    try:
        subprocess.run(command, check=True)
        print(f"Conversion successful! SVG saved as {output_svg_path}")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred during conversion: {e}")


def main():
    image_url = "https://i.imgur.com/AE1oJD2.png"
    input_image_path = fetch_image(image_url, force=True)
    svg_filename = f"{os.path.splitext(os.path.basename(input_image_path))[0]}.svg"
    output_svg_path = os.path.join(ensure_assets_dir(), svg_filename)

    convert_to_svg(input_image_path, output_svg_path)


if __name__ == "__main__":
    main()
