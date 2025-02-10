import os
import tkinter as tk


# Create buttons to choose which family tree file you want to run.
def create_buttons(root, callback):

    csv_files = [file for file in os.listdir() if file.endswith('.csv')]

    button_height = 50
    base_height = 350
    window_height = base_height + len(csv_files) * button_height
    window_width = 350
    root.geometry(f"{window_width}x{window_height}")

    for filename in csv_files:
        button_label = filename.replace('_Family_Tree.csv', '').replace('.csv', '')
        button = tk.Button(root, text=f"{button_label} Family Tree", bg="hotpink", fg="black", height=3, width=15,
                           command=lambda file=filename: callback(file))
        button.pack(pady=10)
