import pandas as pd
from PIL import Image, ImageEnhance
import os
import base64
import mimetypes
from xml.etree import ElementTree as ET


# Attaches information of each person to the nodes
def personal_details(row):
    g = row['Gender']
    det = ''
    if g != 'N':
        newline = '&#13;&#10;'
        details = []

        fields = [
            'Generation',
            'Birth',
            'Death',
            'Marriage',
            'Children',
            'Address',
            'Occupation',
            'Buried',
            'Notes'
        ]

        for field in fields:
            value = row[field]

            if not pd.isna(value) and value:

                if field == 'Generation':
                    value = int(row[field]) if pd.api.types.is_number(row[field]) else row[field]
                details.append(f"{field}: {value}")

        det = newline.join(details)

    elif g == 'N':
        det = ' '

    return det


# Determines the colours of each node
def node_colours(row, direct, temp_image_paths, include_images_flag):

    g = row['Gender']
    sh = 'rect'
    col = "gray"
    fillcol = "lightgray"

    if g == 'M':
        sh = 'rect'
        col = "blue"
        if direct == 1:
            fillcol = "deepskyblue"
        elif direct == 2:
            fillcol = "paleturquoise"

    elif g == 'F':
        sh = 'oval'
        col = "deeppink"
        if direct == 1:
            fillcol = "hotpink"
        elif direct == 2:
            fillcol = "lightpink"

    elif g == 'N':
        sh = 'point'
        col = "black"
        fillcol = "invis"

    elif g == 'MH':
        sh = 'rect'
        col = "darkorchid"
        fillcol = "paleturquoise"

    elif g == 'FH':
        sh = 'oval'
        col = "darkorchid"
        fillcol = "lightpink"

    birth = row.get('Birth', None)
    death = row.get('Death', None)

    if include_images_flag == 1:

        extensions = ['png', 'jpg', 'jpeg']
        image_path = None

        for ext in extensions:
            temp_path = f'images/{row["Person"]}.{ext}'

            if os.path.exists(temp_path):
                image_path = temp_path
                break

        img_path = None

        if image_path:
            resized_image = resize_image(image_path)

            if resized_image is None:
                print(f"Could not resize image for {row['Person']}. Using default.")
                img_path = None

            else:
                os.makedirs('images_temp', exist_ok=True)
                img_path = f"images_temp/temp_resized_image_{row['Person']}.png"
                resized_image.save(img_path)  # Save the resized image temporarily
                temp_image_paths.append(img_path)

    else:
        img_path = None

    return sh, col, fillcol, birth, death, img_path


# Resizes image to correct dimensions to fit below the nodes
def resize_image(image_path, size=(40, 40)):

    try:
        img = Image.open(image_path)
        img = img.resize(size, Image.Resampling.BICUBIC)
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(1.5)

        return img

    except Exception as e:
        print(f"Error resizing image: {e}")

        return None


# Function to attach images directly in SVG
def embed_images_in_svg(filename):
    # Ensure the SVG file exists
    if not os.path.exists(filename):
        raise FileNotFoundError(f"SVG file {filename} not found.")

    # Register namespaces for parsing
    namespaces = {
        'svg': "http://www.w3.org/2000/svg",
        'xlink': "http://www.w3.org/1999/xlink"
    }
    ET.register_namespace('xlink', namespaces['xlink'])

    # Parse the SVG file
    tree = ET.parse(filename)
    root = tree.getroot()

    # Iterate through all <image> tags
    for image in root.findall(".//svg:image", namespaces):
        href_attr = f"{{{namespaces['xlink']}}}href"
        href = image.attrib.get(href_attr)

        if href and os.path.exists(href):  # Ensure the linked file exists
            try:
                # Read and encode the image file
                with open(href, 'rb') as img_file:
                    img_data = img_file.read()
                    base64_data = base64.b64encode(img_data).decode('utf-8')

                # Determine MIME type (default to 'image/png' if unknown)
                mime_type, _ = mimetypes.guess_type(href)
                mime_type = mime_type or "image/png"

                # Replace href with data URI
                data_uri = f"data: {mime_type}; base64, {base64_data}"
                image.set(href_attr, data_uri)
            except Exception as e:
                print(f"Failed to embed image {href}: {e}")

    # Save the updated SVG with embedded images
    tree.write(filename, encoding='utf-8', xml_declaration=True)
