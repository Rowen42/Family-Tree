import pandas as pd
import tkinter as tk
from graphviz import Digraph
from PIL import Image, ImageEnhance
import os
import base64
import mimetypes
from xml.etree import ElementTree as ET
import random
import string

# Create the main application window
root = tk.Tk()
root.title("Family Tree")
familytree = None
show_siblings = tk.IntVar(value=1)

# Generate a random 5 digit ID
def generate_random_id(existing_ids):
    while True:
        random_id = ''.join(random.choices(string.ascii_letters + string.digits, k=5))
        if random_id not in existing_ids:
            existing_ids.add(random_id)
            return random_id

# If a person does not have a randomly assigned ID in the 'ID' column, one will be assigned
def assign_ids(familytree):
    existing_ids = set(familytree['ID'].dropna())
    for index, row in familytree.iterrows():
        if pd.notna(row['Person']) and (pd.isna(row['ID'])) or row['ID'] == '':
            familytree.at[index, 'ID'] = generate_random_id(existing_ids)
    return familytree

# Function to identify the problematic byte
def identify_problematic_byte(filename):
    with open(filename, 'rb') as file:
        content = file.read()
        for i, byte in enumerate(content):
            try:
                bytes([byte]).decode('utf-8')
            except UnicodeDecodeError:
                print(f"Invalid byte found at position {i}: {byte}")
                return i
    return None


# Function to find the exact cell with the invalid character
def find_position_in_csv(filename, byte_position):
    with open(filename, 'rb') as file:
        content = file.read(byte_position + 1)
        row = content[:byte_position].count(b'\n') + 1
        row_start = content.rfind(b'\n', 0, byte_position) + 1
        column = content[row_start:byte_position].count(b',') + 1
    return row, column


# Function to find the exact cell with the invalid character
def find_invalid_character_cell(filename, error_position):
    row, column = find_position_in_csv(filename, error_position)
    print(f"Invalid character found in row {row}, column {column}")
    return row, column


# Function to count the number of people in the family tree
def count_people(familytree):
    filtered_tree = familytree[(familytree['ID'].notna()) & (familytree['ID'] != '')]
    filtered_tree = filtered_tree[(filtered_tree['Gender'] != 'N')]
    unique_people = filtered_tree['ID'].nunique()
    return unique_people


# Prints the percentage of the progress through the generations
def tree_progress(current_step, total_steps):
    percentage_completed = (current_step / total_steps) * 100
    print(f"{percentage_completed: .2f}%")


# Identifies the root descendant and the child of that root descendant
def find_root_descendant_and_children(ancestry):
    root_descendant = ancestry['ID'].iloc[0]
    children = ancestry[ancestry['Child'] == root_descendant]['Child'].tolist()
    return root_descendant, children


# Calculates the amount of generation iterations there are in the family tree
def calculate_max_gen_using_children(root_descendant, ancestry):
    max_generations = 0
    stack = [(root_descendant, 2)]
    visited = set()
    while stack:
        person, generation = stack.pop()

        if person not in visited:
            visited.add(person)
            max_generations = max(max_generations, generation)
            children = ancestry[ancestry['Child'] == person]['ID'].tolist()

            for child in reversed(children):
                if child not in visited and child != '':
                    stack.append((child, generation + 1))

    return max_generations+1


# Define the function to load and process the family tree
def button_clicked(filename):
    global familytree

    if filename:
        error_position = identify_problematic_byte(filename)
        if error_position is not None:
            find_invalid_character_cell(filename, error_position)
        else:
            familytree = pd.read_csv(filename, encoding='utf-8')

            familytree = assign_ids(familytree)
            familytree.to_csv(filename, index=False)

            root.destroy()
            process_family_tree()

# Create buttons to choose which family tree file you want to run.
def create_buttons():
    csv_files = [file for file in os.listdir() if file.endswith('.csv')]
    button_height = 50
    base_height = 200
    window_height = base_height + len(csv_files) * button_height
    window_width = 300
    root.geometry(f"{window_width}x{window_height}")

    for filename in csv_files:
        button_label = filename.replace('_Family_Tree.csv', '').replace('.csv', '')
        button = tk.Button(root, text=f"{button_label} Family Tree", bg="hotpink", fg="black", height=3, width=15,
                           command=lambda file=filename: button_clicked(file))
        button.pack(pady=10)


# Attaches information of each person to the nodes
def personal_details(row):
    g = row['Gender']
    if g != 'N':
        newline = '&#13;&#10;'
        details = []

        fields = [
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
                details.append(f"{field}: {value}")

        det = newline.join(details)
    elif g == 'N':
        det = ' '
    return det


# Determines the colours of each node
def node_colours(row, direct, temp_image_paths):
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

    return sh, col, fillcol, img_path

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
def embed_images_in_svg(svg_filename):
    # Ensure the SVG file exists
    if not os.path.exists(svg_filename):
        raise FileNotFoundError(f"SVG file {svg_filename} not found.")

    # Register namespaces for parsing
    namespaces = {
        'svg': "http://www.w3.org/2000/svg",
        'xlink': "http://www.w3.org/1999/xlink"
    }
    ET.register_namespace('xlink', namespaces['xlink'])

    # Parse the SVG file
    tree = ET.parse(svg_filename)
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
    tree.write(svg_filename, encoding='utf-8', xml_declaration=True)


def create_node(dot, node_id, label, tooltip, font, shape, style, color, fillcolor, image=None):
    if image:
        dot.node(
            node_id,
            label,
            tooltip=tooltip,
            fontname=font,
            shape=shape,
            style=style,
            color=color,
            fillcolor=fillcolor,
            image=image,
            labelloc="t",
            imagepos="bc",
            height='0.8'
        )
    else:
        dot.node(
            node_id,
            label,
            tooltip=tooltip,
            fontname=font,
            shape=shape,
            style=style,
            color=color,
            fillcolor=fillcolor
        )


def create_edge(dot, node1, node2, arrowhead, style, color, constraint='true', ordering=None):
    dot.edge(
        node1,
        node2,
        arrowhead=arrowhead,
        style=style,
        color=color,
        constraint=constraint,
        ordering=ordering
    )


def create_rank_subgraph(dot, nodes, edges, rank='same'):
    with dot.subgraph() as subs:
        subs.attr(rank=rank)
        for node in nodes:
            create_node(subs, *node)
        for edge in edges:
            create_edge(subs, *edge)


# The function to process the family tree
def process_family_tree():
    if familytree is not None:
        print("Creating Family Tree...")
        unique_people = count_people(familytree)
        print(f"Total number of people in the family tree: {unique_people}")
        ancestry = familytree.fillna('')
        earl_ans = ancestry.loc[ancestry['Child'] == 'First Descendent', 'ID'].iloc[0]
        ancestry.loc[:, 'recorded_ind'] = 0  # Use .loc to set values

        incomp = [earl_ans]
        comp = []
        temp_image_paths = []

        dot = Digraph(comment='Ancestry')
        dot.attr(rankdir="TB")
        node_nm = []

        # Initializing first node
        initial_row = ancestry.loc[ancestry['ID'] == earl_ans].iloc[0]
        det = personal_details(initial_row)
        sh, col, fillcol, img = node_colours(initial_row, 1, temp_image_paths)
        font = 'Comic Sans MS'
        create_node(dot, earl_ans, initial_row['Person'], det, font, sh, "filled, bold", col, fillcol, img)
        node_nm.append(earl_ans)
        ancestry.loc[ancestry['ID'] == earl_ans, 'recorded_ind'] = 1

        # Find the root descendants and linking it to their children
        root_descendant, children = find_root_descendant_and_children(ancestry)
        # max_iter the total number of generations (double + 1 of the number of family generations)
        max_iter = calculate_max_gen_using_children(root_descendant, ancestry)
        num_gen = (max_iter-1) // 2
        print(f"Number generations {num_gen}")
        gen_count = 0

        for i in range(max_iter):
            temp = ancestry[ancestry['recorded_ind'] == 0].copy()  # Create a copy to avoid warnings

            if temp.empty:  # Break loop when all individuals have been recorded
                break
            else:
                temp['this_gen_ind'] = temp.apply(
                    lambda x: 1 if x['Child'] in incomp or x['Parent'] in incomp else 0, axis=1
                )

                # Parent Relationship (used to be child but I swapped now)
                if show_siblings.get():
                    this_gen = temp[temp['this_gen_ind'] == 1]
                    if not this_gen.empty:
                        for j in range(len(this_gen)):
                            row = this_gen.iloc[j]
                            per1 = row['ID']
                            parents = row['Parent']
                            det = personal_details(row)
                            sh, col, fillcol, img = node_colours(row, 2, temp_image_paths)
                            if parents and not ancestry[ancestry['ID'] == parents].empty:
                                create_node(dot, per1, row['Person'], det, font, sh, "filled, bold", col, fillcol, img)
                                node_nm.append(per1)
                                create_edge(dot, parents, per1, arrowhead='none', style="filled", color="black", constraint='true')

                # Spouse Relationship
                this_gen = temp[temp['this_gen_ind'] == 1]
                if not this_gen.empty:
                    for j in range(len(this_gen)):
                        row = this_gen.iloc[j]
                        per1 = row['ID']
                        spouse = row['Spouse']
                        det = personal_details(row)
                        sh, col, fillcol, img = node_colours(row, 1, temp_image_paths)
                        with dot.subgraph() as subs:
                            if not familytree.loc[familytree['ID'] == spouse].empty:
                                if not familytree.loc[familytree['ID'] == spouse].empty:
                                    nodes = [(per1, row['Person'], det, font, sh, "filled, bold", col, col, img)]
                                    edges = [(per1, spouse, 'none', "solid", "black:deeppink:black", 'true')]
                                    create_rank_subgraph(dot, nodes, edges)

                # Child Relationship
                this_gen = temp[temp['this_gen_ind'] == 1]
                if not this_gen.empty:
                    for j in range(len(this_gen)):
                        row = this_gen.iloc[j]
                        per1 = row['ID']
                        child = row['Child']
                        det = personal_details(row)
                        sh, col, fillcol, img = node_colours(row, 1, temp_image_paths)
                        if child and not ancestry[ancestry['ID'] == child].empty:
                            create_node(dot, per1, row['Person'], det, font, sh, "filled, bold", col, fillcol, img)
                            node_nm.append(per1)
                            create_edge(dot, per1, child, arrowhead='none', style="filled", color="purple:magenta",
                                        constraint='true')

                # Sibling Relationship Order
                        # Sibling Relationship
                        if show_siblings.get():
                            this_gen = temp[temp['this_gen_ind'] == 1]
                            for _, row in this_gen.iterrows():
                                per1 = row['ID']
                                sibf = row['NextF']
                                sibm = row['NextM']

                                # Siblings of a Female
                                if not familytree.loc[familytree['ID'] == sibf].empty:
                                    edges = [(per1, sibf, "none", "invis", "invis", 'true')]
                                    create_rank_subgraph(dot, [], edges)

                                # Siblings of a Male
                                if not familytree.loc[familytree['ID'] == sibm].empty:
                                    edges = [(sibm, per1, "none", "invis", "invis", 'true')]
                                    create_rank_subgraph(dot, [], edges)

                gen_count = gen_count + 1
                tree_progress(gen_count, max_iter)
                comp.extend(incomp)
                incomp = list(temp.loc[temp['this_gen_ind'] == 1, 'ID'])
                ancestry.loc[:, 'recorded_ind'] = ancestry.apply(
                    lambda x: 1 if (x['ID'] in incomp) | (x['ID'] in comp) else 0, axis=1
                )

        print("Opening Family Tree...")
        dot.format = 'svg'
        svg_filename = 'Family_Tree'
        dot.render(svg_filename, format='svg', view=True)
        embed_images_in_svg('Family_Tree.svg')

        print('Family Tree Completed')
        for img_path in temp_image_paths:
            if os.path.exists(img_path):
                os.remove(img_path)
    else:
        print("No family tree loaded.")

# Create buttons for selecting family tree so you could be working on multiple family trees at the same time
create_buttons()

show_siblings_checkbox = tk.Checkbutton(root, text="Show Siblings", variable=show_siblings)
show_siblings_checkbox.pack(pady=10)

root.mainloop()
