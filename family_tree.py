from graphviz import Digraph
import os
from tree_stats import (count_people, tree_progress, find_root_descendant_and_children, max_gen_num)
from visualization import embed_images_in_svg
from relationships import (first_descendant, parent_relationship, spouse_relationship, child_relationship,
                           sibling_relationship)


# The function to process the family tree
def process_family_tree(familytree, show_siblings, include_images):

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

        font = 'Comic Sans MS'

        first_descendant(dot, ancestry, earl_ans, temp_image_paths, include_images, font, node_nm)

        # Find the root descendants and linking it to their children
        root_descendant, children = find_root_descendant_and_children(ancestry)
        # max_iter the total number of generations (double + 1 of the number of family generations)
        max_iter = max_gen_num(root_descendant, ancestry)
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

                parent_relationship(dot, ancestry, temp, temp_image_paths, include_images, font, node_nm, show_siblings)
                spouse_relationship(dot, familytree, temp, temp_image_paths, include_images, font)
                child_relationship(dot, ancestry, temp, temp_image_paths, include_images, font, node_nm)
                sibling_relationship(dot, familytree, temp, show_siblings)

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
        dot.render(svg_filename, format='svg', view=True, cleanup=True)

        if include_images.get() == 1:
            embed_images_in_svg('Family_Tree.svg')

        print('Family Tree Completed')

        for img_path in temp_image_paths:
            if os.path.exists(img_path):
                os.remove(img_path)

    else:
        print("No family tree loaded.")
