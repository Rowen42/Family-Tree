import pandas as pd
import tkinter as tk
from graphviz import Digraph

# Create the main application window
root = tk.Tk()
root.title("Family Tree")
root.geometry("300x400")
familytree = None
show_siblings = tk.BooleanVar()

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
    filtered_tree = familytree[(familytree['Person'].notna()) & (familytree['Person'] != '')]
    filtered_tree = filtered_tree[(filtered_tree['Gender'] != 'N')]
    unique_people = filtered_tree['Person'].nunique()
    return unique_people

# Prints the percentage of the progress through the generations
def tree_progress(current_step, total_steps):
    percentage_completed = (current_step/ total_steps) * 100
    print(f"{percentage_completed:.2f}%")

# Identifies the root descendant and the child of that root descendant
def find_root_descendant_and_children(ancestry):
    root_descendant = ancestry['Person'].iloc[0]
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
            children = ancestry[ancestry['Child'] == person]['Person'].tolist()

            for child in reversed(children):
                if child not in visited and child != '':
                    stack.append((child, generation + 1))

    return (max_generations+1)

# Define the function to load and process the family tree
def button_clicked(button_name):
    global familytree
    filename = None
    if button_name == "MyTree":
        filename = ('My_Family_Tree.csv')

    if filename:
        error_position = identify_problematic_byte(filename)
        if error_position is not None:
            find_invalid_character_cell(filename, error_position)
        else:
            familytree = pd.read_csv(filename, encoding='utf-8')
            root.destroy()
            process_family_tree()

# Attaches information of each person to the nodes
def Personal_Details(row):
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
def Node_Colours(row, Direct):
    g = row['Gender']
    sh = 'rect'
    col = "gray"
    fillcol = "lightgray"

    if g == 'M':
        sh = 'rect'
        col = "blue"
        if Direct == 1:
            fillcol = "deepskyblue"
        elif Direct == 2:
            fillcol = "paleturquoise"
    elif g == 'F':
        sh = 'oval'
        col = "deeppink"
        if Direct == 1:
            fillcol = "hotpink"
        elif Direct == 2:
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

    return sh, col, fillcol


# Define the function to process the family tree
def process_family_tree():
    if familytree is not None:
        print("Creating Family Tree...")
        unique_people = count_people(familytree)
        print(f"Total number of people in the family tree: {unique_people}")
        ancestry = familytree.fillna('')
        earl_ans = ancestry.loc[ancestry['Child'] == 'First Descendent', 'Person'].iloc[0]
        ancestry.loc[:, 'recorded_ind'] = 0  # Use .loc to set values

        incomp = [earl_ans]
        comp = []

        dot = Digraph(comment = 'Ancestry')
        node_nm = []

        # Initializing first node
        initial_row = ancestry.loc[ancestry['Person'] == earl_ans].iloc[0]
        det = Personal_Details(initial_row)
        sh, col, fillcol = Node_Colours(initial_row, 1)
        Font = 'Comic Sans MS'
        dot.node(earl_ans, earl_ans, tooltip=det, fontname=Font, shape=sh, style="filled, bold", color=col, fillcolor=fillcol)
        node_nm.append(earl_ans)

        ancestry.loc[ancestry['Person'] == earl_ans, 'recorded_ind'] = 1

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
                temp['this_gen_ind'] = temp.apply(lambda x: 1 if x['Child'] in incomp or x['Parent'] in incomp else 0, axis=1)

                # Parent Relationship (used to be child but I swapped now)
                if show_siblings.get():
                    this_gen = temp[temp['this_gen_ind'] == 1]
                    if not this_gen.empty:
                        for j in range(len(this_gen)):
                            row = this_gen.iloc[j]
                            per1 = row['Person']
                            parents = row['Parent']
                            det = Personal_Details(row)
                            sh, col, fillcol = Node_Colours(row, 2)
                            if parents and not ancestry[ancestry['Person'] == parents].empty:
                                dot.node(per1, per1, tooltip=det, fontname = Font, shape=sh, style="filled, bold", color=col, fillcolor=fillcol)
                                node_nm.append(per1)
                                dot.edge(parents, per1, ordering='left', arrowhead='none', style="filled", color="black", fillcolor="black")

                # Spouse Relationship
                this_gen = temp[temp['this_gen_ind'] == 1]
                if not this_gen.empty:
                    for j in range(len(this_gen)):
                        row = this_gen.iloc[j]
                        per1 = row['Person']
                        spouse = row['Spouse']
                        det = Personal_Details(row)
                        sh, col, fillcol= Node_Colours(row, 1)
                        with dot.subgraph() as subs:
                            if not familytree.loc[familytree['Person'] == spouse].empty:
                                subs.attr(rank='same')
                                subs.node(per1, per1, ordering='out', tooltip=det, fontname = Font, shape=sh, style="filled, bold", color=col, fillcolor=col)
                                node_nm.append(per1)
                                subs.edge(per1, spouse, arrowhead="none", color="black:deeppink:black", constraint='true')

                # Child Relationship
                this_gen = temp[temp['this_gen_ind'] == 1]
                if not this_gen.empty:
                    for j in range(len(this_gen)):
                        row = this_gen.iloc[j]
                        per1 = row['Person']
                        child = row['Child']
                        det = Personal_Details(row)
                        sh, col, fillcol= Node_Colours(row, 1)
                        if child and not ancestry[ancestry['Person'] == child].empty:
                            dot.node(per1, per1, tooltip=det, fontname = Font, shape=sh, style="filled, bold", color=col, fillcolor=fillcol)
                            node_nm.append(per1)
                            dot.edge(per1, child, arrowhead='none', color="purple:magenta", fillcolor="darkmagenta")


                # Sibling Relationship Order (Siblings of Female and Male Person1 attach from different directionsso does not overlap)
                #Sibling of a Female Direct Ancestor
                    if show_siblings.get():
                        this_gen = temp[temp['this_gen_ind'] == 1]
                        if not this_gen.empty:
                            for j in range(len(this_gen)):
                                row = this_gen.iloc[j]
                                per1 = row['Person']
                                sibf = row['NextF']
                                if not familytree.loc[familytree['Person'] == sibf].empty:
                                    with dot.subgraph() as subs:
                                        subs.attr(rank='same')
                                        node_nm.append(per1)
                                        subs.edge(per1, sibf,arrowhead="none", color="invis", constraint='true')
                        #Sibling of a Male Direct Ancestor
                        this_gen = temp[temp['this_gen_ind'] == 1]
                        if not this_gen.empty:
                            for j in range(len(this_gen)):
                                row = this_gen.iloc[j]
                                per1 = row['Person']
                                sibm = row['NextM']
                                if not familytree.loc[familytree['Person'] == sibm].empty:
                                    with dot.subgraph() as subs:
                                        subs.attr(rank='same')
                                        node_nm.append(per1)
                                        subs.edge(sibm, per1, arrowhead="none", color="invis", constraint='true')


                gen_count = gen_count + 1
                tree_progress(gen_count, max_iter)
                comp.extend(incomp)
                incomp = list(temp.loc[temp['this_gen_ind'] == 1, 'Person'])
                ancestry.loc[:, 'recorded_ind'] = ancestry.apply(lambda x: 1 if (x['Person'] in incomp) | (x['Person'] in comp) else 0, axis=1)

        print("Opening Family Tree...")
        dot.format = 'png'
        dot.render('Family_Tree', view=True)
        dot.format = 'svg'
        dot.render('Family_Tree', view=True)
        print('Family Tree Completed')
    else:
        print("No family tree loaded.")

# Create buttons for selecting family tree so you could be working on multiple family trees at the same time
button_options = {
    "MyTree": {"text": "My Family Tree", "bg": "hotpink", "fg": "black"}
}

for button_name, options in button_options.items():
    button = tk.Button(root, text=options["text"], bg=options["bg"], fg=options["fg"], height=3, width=15,
                       command=lambda name=button_name: button_clicked(name))
    button.pack(pady=10)


show_siblings_checkbox = tk.Checkbutton(root, text="Show Siblings", variable=show_siblings)
show_siblings_checkbox.pack(pady=10)

root.mainloop()