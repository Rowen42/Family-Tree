def create_node(dot, node_id, name, tooltip, font, shape, style, color, fillcolor, birth, death, image=None):

    label = f"""<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0"><TR><TD><B>{name}</B></TD></TR>"""
    if birth or death:
        label += f"""<TR><TD><FONT POINT-SIZE="10">{birth} - {death}</FONT></TD></TR>"""
    label += """
        </TABLE>
    >"""

    if image:
        dot.node(
            node_id,
            label=label,
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


def create_edge(dot, node1, node2, arrowhead, style, color, constraint='true'):

    dot.edge(
        node1,
        node2,
        arrowhead=arrowhead,
        style=style,
        color=color,
        constraint=constraint,
    )


def create_rank_subgraph(dot, nodes, edges, rank='same'):

    with dot.subgraph() as subs:
        subs.attr(rank=rank)

        for node in nodes:
            create_node(subs, *node)
        for edge in edges:
            create_edge(subs, *edge)
