from visualization import personal_details, node_colours
from node_creation import create_node, create_edge, create_rank_subgraph


# Initializing node of the first descendant (lowest person on the tree)
def first_descendant(dot, ancestry, earl_ans, temp_image_paths, include_images, font, node_nm):

    initial_row = ancestry.loc[ancestry['ID'] == earl_ans].iloc[0]

    det = personal_details(initial_row)
    sh, col, fillcol, birth, death, img = node_colours(initial_row, 1, temp_image_paths, include_images.get())

    create_node(dot, earl_ans, initial_row['Person'], det, font, sh, "filled, bold", col, fillcol, birth, death, img)
    node_nm.append(earl_ans)

    ancestry.loc[ancestry['ID'] == earl_ans, 'recorded_ind'] = 1


# Parent Relationship where the parents of siblings are connected to the siblings
def parent_relationship(dot, ancestry, temp, temp_image_paths, include_images, font, node_nm, show_siblings):

    if show_siblings.get():

        this_gen = temp[temp['this_gen_ind'] == 1]

        if not this_gen.empty:
            for j in range(len(this_gen)):

                row = this_gen.iloc[j]
                per1 = row['ID']
                parents = row['Parent']

                det = personal_details(row)
                sh, col, fillcol, birth, death, img = node_colours(row, 2, temp_image_paths, include_images.get())

                if parents and not ancestry[ancestry['ID'] == parents].empty:
                    create_node(dot, per1, row['Person'], det, font, sh, "filled, bold", col, fillcol, birth, death,
                                img)
                    node_nm.append(per1)
                    create_edge(dot, parents, per1, arrowhead='none', style="filled", color="black", constraint='true')


# Spouse Relationship connects husband and wife or if they were unmarried the parents are connected together
def spouse_relationship(dot, familytree, temp, temp_image_paths, include_images, font):

    this_gen = temp[temp['this_gen_ind'] == 1]

    if not this_gen.empty:
        for j in range(len(this_gen)):
            row = this_gen.iloc[j]
            per1 = row['ID']
            spouse = row['Spouse']

            det = personal_details(row)
            sh, col, fillcol, birth, death, img = node_colours(row, 1, temp_image_paths, include_images.get())

            if not familytree.loc[familytree['ID'] == spouse].empty:
                nodes = [(per1, row['Person'], det, font, sh, "filled, bold", col, col, birth, death, img)]
                edges = [(per1, spouse, 'none', "solid", "black:deeppink:black", 'true')]
                create_rank_subgraph(dot, nodes, edges)


# Child Relationship where direct ancestors are connected to their parents
def child_relationship(dot, ancestry, temp, temp_image_paths, include_images, font, node_nm):

    this_gen = temp[temp['this_gen_ind'] == 1]

    if not this_gen.empty:
        for j in range(len(this_gen)):
            row = this_gen.iloc[j]
            per1 = row['ID']
            child = row['Child']

            det = personal_details(row)
            sh, col, fillcol, birth, death, img = node_colours(row, 1, temp_image_paths,
                                                               include_images.get())

            if child and not ancestry[ancestry['ID'] == child].empty:
                create_node(dot, per1, row['Person'], det, font, sh, "filled, bold", col, fillcol,
                            birth, death, img)
                node_nm.append(per1)
                create_edge(dot, per1, child, arrowhead='none', style="filled",
                            color="purple:magenta",
                            constraint='true')


# Sibling Relationship
def sibling_relationship(dot, familytree, temp, show_siblings):

    if show_siblings.get():

        this_gen = temp[temp['this_gen_ind'] == 1]

        for _, row in this_gen.iterrows():
            per1 = row['ID']
            sibf = row['NextF']
            sibm = row['NextM']

            # Siblings of a Female direct ancestor
            if not familytree.loc[familytree['ID'] == sibf].empty:
                edges = [(per1, sibf, "none", "invis", "invis", 'true')]
                create_rank_subgraph(dot, [], edges)

            # Siblings of a Male direct ancestor
            if not familytree.loc[familytree['ID'] == sibm].empty:
                edges = [(sibm, per1, "none", "invis", "invis", 'true')]
                create_rank_subgraph(dot, [], edges)
