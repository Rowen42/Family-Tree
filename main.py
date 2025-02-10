import pandas as pd
import tkinter as tk
import os
from id_generation import assign_ids
from file_operations import identify_problematic_byte, find_invalid_character_cell
from family_tree import process_family_tree
from ui_helpers import create_buttons
from queries import query_person_info

# Create the main application window
root = tk.Tk()
root.title("Family Tree")
familytree = None

show_siblings = tk.IntVar(value=1)
include_images = tk.IntVar(value=0)
assign_ids_only = tk.IntVar(value=0)
query_person = tk.IntVar(value=0)

if os.path.exists("Family_Tree.svg"):
    os.remove("Family_Tree.svg")


# Define the function to load and process the family tree
def button_clicked(filename):
    global familytree

    if filename:
        error_position = identify_problematic_byte(filename)

        if error_position is not None:
            find_invalid_character_cell(filename, error_position)
        else:
            familytree = pd.read_csv(filename, encoding='utf-8')

            if assign_ids_only.get() == 1:
                print("Assign IDs Only mode enabled")
                familytree = assign_ids(familytree)
                # familytree = get_rid_of_numbers(familytree)
                familytree.to_csv(filename, index=False)
                root.destroy()
                return

            if query_person.get() == 1:
                query_person_info(familytree)
                return

            root.destroy()
            process_family_tree(familytree, show_siblings, include_images)


# Create buttons for selecting family tree, so you could be working on multiple family trees at the same time
create_buttons(root, button_clicked)

show_siblings_checkbox = tk.Checkbutton(root, text="Show Siblings", variable=show_siblings)
show_siblings_checkbox.pack(pady=10)

assign_ids_only_checkbox = tk.Checkbutton(root, text="Assign IDs", variable=assign_ids_only)
assign_ids_only_checkbox.pack(pady=10)

query_checkbox = tk.Checkbutton(root, text="Query Family Member", variable=query_person)
query_checkbox.pack(pady=10)

include_images_checkbox = tk.Checkbutton(root, text="Include Images", variable=include_images)
include_images_checkbox.pack(pady=10)

root.mainloop()
