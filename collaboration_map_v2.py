from graphviz import Digraph, Graph
from nltk.tokenize import RegexpTokenizer
#from convert_transcript import convert_transcript

tokenizer = RegexpTokenizer('\s+', gaps=True)

def format_turn_html(turn):
    """Generate html code for a turn

    Args:
        turn (str): raw text for a turn

    Returns:
        str: string formatted in html, with a set max width
    """
    row_length = 40
    if len(turn) < row_length:
        return turn
    else:
        words = tokenizer.tokenize(turn)
        current_length = 0
        output_string = ''
        for i in range(len(words)):
            if current_length + len(words[i]) > row_length:
                output_string = output_string + '<BR/>'
                current_length = 0
            output_string = output_string + ' ' + words[i]
            current_length += len(words[i])
    return output_string
        


def create_collaboration_map(data):
    """Generate collaboration map

    Args:
        data ([type]): each item in the list is a dictionary containing turn numnber, raw text, reference, collaboration code

    Returns:
        Graph: graphviz Graph object with the complete collaboration map
    """

    collaboration_colors_map = {'challenge':'mediumseagreen','new':'tomato', 'extension':'DeepSkyBlue2', 'agree': 'white', 'Non':'white', '': 'white', 'teacher':'yellow'}
    dot = Graph(name='collaboration_map_graph', format='png')
    # get number of new ideas
    number_new = sum([1 for a in data if a['Collaboration'] == 'new'])
    # add one in case there are turns before the first "new" turn
    if data[0]['Collaboration'] != 'new':
        number_new += 1
    
    # create subgraph of invisible nodes for alignment of "new" turns
    init_graph = Graph(name='init_nodes', node_attr={'rank': 'same'})
    init_graph.attr(rank='same')
    init_nodes = []
    for i in range(number_new):
        init_graph.node('init' + str(i), str(i), style='invis')
        init_nodes.append('init' + str(i))
        if len(init_nodes) > 1:
            init_graph.edge('init' + str(i), init_nodes[-2], style='invis')
    dot.subgraph(init_graph)
    
    clusters = []
    node_to_graph = {} # for each node, contains the graph it is assigned to
    init_index = number_new-1
    c = Graph(name='cluster' + str(len(clusters)), node_attr={'shape': 'box'})
    current_graph = c
    temp_nodes_to_add = []
    for i in range(len(data)):
        if data[i]['Collaboration'] == 'new':
            # save previous cluster and create new cluster

            if len(temp_nodes_to_add) > 0:
                for a in temp_nodes_to_add[::-1]:
                    current_graph.node(a[0], shape='none', style='rounded',
                                            label=a[1])
                    node_to_graph[a[0]] = current_graph
                temp_nodes_to_add= []

            clusters.append(c)
            c = Graph(name='cluster' + str(len(clusters)), node_attr={'shape': 'box'})
            current_graph = c
            
        
        turn_color = collaboration_colors_map[data[i]['Collaboration']]
        if data[i]['Student'] == 'teacher':
            student_label = 'TEACHER'
            turn_color = collaboration_colors_map['teacher']
        else:
            student_label = 'STUDENT ' + data[i]['Student']
        
        # create heading with turn number, speaker id, collaboration code
        row_style = '<TR><TD CELLPADDING="6" BGCOLOR="' + turn_color + '" PORT="p1">'
        student_label = 'TURN ' + data[i]['TurnNum'] + ' - ' + student_label + '<BR/>'
        if data[i]['Collaboration'] != '':
            student_label = student_label + data[i]['Collaboration'].upper() + '<BR/>'
        
        # create the complete html code for the current node
        node_label = '<<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0">' + row_style + student_label + '</TD></TR><HR/>' + row_style + format_turn_html(data[i]['RawText']) + '<BR/>' + '</TD></TR></TABLE>>'

        # check if the reference turn falls in the current subgraph
        if data[i]['Reference'] != '' and data[i]['Reference'] in node_to_graph and node_to_graph[data[i]['Reference']] != current_graph:
            # reference not in current_graph
            node_to_graph[data[i]['Reference']].node(data[i]['TurnNum'], shape='none', style='rounded',
                                    label=node_label)
            node_to_graph[data[i]['TurnNum']] = node_to_graph[data[i]['Reference']]
        
        else:
            # reference is in current graph
            # if it's a "non" node, add it later (for left->right order)
            if data[i]['Collaboration'] not in ['', 'Non'] and data[i]['Student'] != 'teacher':
                current_graph.node(data[i]['TurnNum'], shape='none', style='rounded',
                                        label=node_label)
                node_to_graph[data[i]['TurnNum']] = current_graph
            else:
                temp_nodes_to_add.append([data[i]['TurnNum'], node_label])

        # add edge to target node
        if data[i]['TurnNum'] != '' and data[i]['Reference'] != '' and data[i]['Reference'] != 'Non':
            # check if the reference turn falls in the current subgraph
            if data[i]['Reference'] != '' and data[i]['Reference'] in node_to_graph and node_to_graph[data[i]['Reference']] != current_graph:
                node_to_graph[data[i]['Reference']].edge(data[i]['TurnNum'], data[i]['Reference'])
            else:
                current_graph.edge(data[i]['TurnNum'], data[i]['Reference'])
        
        # add edges for alignment
        if i == 0 and data[i]['Collaboration'] != 'new':
            current_graph.edge(data[i]['TurnNum'], 'init'+str(init_index), style='invis')
            # print('Linking first node to init{}'.format(init_index))
            init_index -= 1
            # print('init_index = {}'.format(init_index))
        if data[i]['Collaboration'] == 'new':
            current_graph.edge(data[i]['TurnNum'], 'init'+str(init_index), style='invis')
            # print('Linking node {} to init{}'.format(data[i]['TurnNum'], init_index))
            init_index -= 1
            # print('init_index = {}'.format(init_index))



    clusters.append(current_graph)
    for i in list(range(len(clusters))):#[::-1]:
        dot.subgraph(clusters[i])
    dot.attr(rankdir='BT')
    return dot



# the following is for getting around the error that graphviz randomly throws sometimes, you can use it as reference
# for a in discussions:
#     print(a)
#     out = convert_transcript(a)
#     tmp = create_collaboration_map(out['turnList'])
#     done = False
#     while not done:
#         try:
#             tmp.render('images/' + a.strip('.xlsx') + '_collaboration_map')
#             done = True
#         except:
#             print('Error, retrying ' + a)

