
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


# Calculates the amount of generation iterations there are in the family tree through the child and parent relationship
def max_gen_num(root_descendant, ancestry):

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
