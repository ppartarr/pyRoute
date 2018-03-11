import argparse as ap
import networkx as nx
import csv
import sys

# Constants
SPLIT_HORIZON = False

# Parse command line arguments
parser = ap.ArgumentParser(description = 'Simplified network in python')
parser.add_argument('-f', '--file', required=True, help='reads the specified CSV file as input for the network')
args = parser.parse_args()

# returns the data in the CSV file
def readcsv(file):
    with open(file, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        nodesAndEdges = []
        for row in reader:
            if row:                 # check that list isn't empty
                if "#" not in row[0]:   # check that the line isn't a comment
                    nodesAndEdges.append(row)    # TODO: remove comments from row
    return nodesAndEdges

# Formats edges according to the graph edge required form: a tuple with a weight i.e. (src, dest, {'weight':5})
def format_edges(raw_edges):
    edges = []
    for edge in raw_edges:
        edges.append((edge[0], edge[1], {'weight': float(edge[2])}))
    return edges

# Displays the routing table for a given node
def print_routing_table(node):
    routing_table = G.nodes[node]['routing_table'].routing_table
    print "Routing table for %s:" % node
    for node in routing_table:
        print "\t", node, "\t", routing_table[node]


class RoutingTable:

    def __init__(self, node):
        self.name = node
        self.routing_table = {adj_node:G.adj[node][adj_node]['weight'] for adj_node in G.adj[node]} # add adjacent nodes to the routing table
        non_adjacent_nodes = list(set(G.nodes) - set(G.adj[node]) - set(node)) 
        self.routing_table.update({non_adj_node: float('inf') for non_adj_node in non_adjacent_nodes}) # add non-adjacent nodes to the routing table
        self.routing_table[node] = 0
    
    def update_edge(self, dest, cost):
        self.routing_table.update({dest: cost})

# Prints the help menu
def usage():
    print "Usage: <command> <argument(s)>"
    print "\thelp or ?                   displays this help menu"
    print "\ttrace N1 N2 N3/all          returns the routing table for the given nodes"
    print "\troute N1 N2                 finds the best route between two given nodes"
    print "\tcost src dest 4/fail        changes the cost of an edge"
    print "\texchange 2/stable           compute routing tables for any number of exchanges of until stability is achieved"
    print "\tsplit-horizon               engage split-horizon to combat slow convergence" 
    print
    print "Examples: "
    print "\ttrace all"
    print "\tcost N1 N2 fail"
    print "\texchange 5"

# Returns the user input divided into a command and arguments
def get_input():
    user_input = raw_input("> ")
    command = user_input.split(" ")[0]
    args = user_input.split(" ")[1:]
    return command, args

# Returns False if the arguments are empty or invalid
def check_args(args, command, expected=None, minimum=None, nodes=None, keyword=None, keyword_pos=None):
    if minimum != None and len(args) < minimum:                                                         # check that there is at least min arguments
        print "%s requires at least  %s arguments - type help for an example" % (command, minimum)
        return False
    if expected != None and len(args) != expected:                                              # check that the expected number of arguments are present
        print "%s requires %s arguments - type help for an example" % (command, expected)
        return False
    if keyword != None:                                                                         # check for a keyword and it's position
        if not validate_keyword(args, command, keyword, keyword_pos):
            print "Invalid argument"
            return False
    if nodes != None:                                                                           # check that all nodes given by the user are nodes in the graph
        for node in nodes:
            if node not in G.nodes:
                print "%s is not a node in the graph - all arguments must be nodes!" % node
                return False
    return True

# checks if a keyword is being correctly used
def validate_keyword(args, command, keyword, keyword_pos):
    return is_number(args[keyword_pos]) or is_node(args[keyword_pos]) or args[keyword_pos] == keyword

def is_number(var):
    try:
        float(var)
    except ValueError:
        return False
    return True

def is_node(var):
    return var in G 

# Prints the path between two nodes
def print_path(path):
    for node in path[:-1]:
        print node, " -> ",
    print path[-1]

def update_routing_table(src, dest, cost):
    # TODO: add error checking (can't update link to self, or to non-adjacent node)
    G.nodes[src]['routing_table'].update_edge(dest, cost)
    G.nodes[dest]['routing_table'].update_edge(src, cost)

# Every node sends it's routing table to neighbour and updates it's own using Bellman Ford
def bellman_ford():
    for src in G.nodes:
        for adj_node in G.adj[src]:
            adj_node_routing_table = G.nodes[adj_node]['routing_table'].routing_table
            src_distance_to_adj = G.nodes[src]['routing_table'].routing_table[adj_node]
            for dest in adj_node_routing_table:                                            # n is a node in the adjacent nodes' routing table
                src_distance_to_dest = G.nodes[src]['routing_table'].routing_table[dest]
                adj_distance_to_dest = adj_node_routing_table[dest]

                new_distance = min(src_distance_to_adj + adj_distance_to_dest, src_distance_to_dest) # calculate new minimum distance
                G.nodes[src]['routing_table'].update_edge(dest, new_distance) 
    negative_weight_check()
           
def split_horizon():
    for src in G.nodes:
        for adj_node in G.adj[src]:
            adj_node_routing_table = G.nodes[adj_node]['routing_table'].routing_table
            src_distance_to_adj = G.nodes[src]['routing_table'].routing_table[adj_node]
            for dest in adj_node_routing_table:                                            # n is a node in the adjacent nodes' routing table
                # Only advertise adjacent nodes
                if dest not in G.adj[src]:
                    src_distance_to_dest = G.nodes[src]['routing_table'].routing_table[dest]
                    adj_distance_to_dest = adj_node_routing_table[dest]

                    new_distance = min(src_distance_to_adj + adj_distance_to_dest, src_distance_to_dest) # calculate new minimum distance
                    G.nodes[src]['routing_table'].update_edge(dest, new_distance) 
    negative_weight_check()

def negative_weight_check():
    for edge in G.edges:
        if G[edge[0]][edge[1]]['weight'] < 0:
            print "Error: graph contains a negative edge between %s and %s" % (edge[0], edge[1])
            sys.exit(0)
 

nodesAndEdges = readcsv(args.file)
nodes = nodesAndEdges[0]
raw_edges = nodesAndEdges[1:]
edges = format_edges(raw_edges)

# Define graph, nodes and links
G = nx.Graph()
G.add_nodes_from(nodes)
G.add_edges_from(edges)

# Initialise routing table for every node
for node in G.nodes:
    G.nodes[node]['routing_table'] = RoutingTable(node)

# Start the interpreter and match user input to the commands
print "To exit, press ctrl + c or enter exit"
command, args = get_input()

while command not in ["exit","quit","stop","q"]:
    if command in ["help","?"]:
        usage()
        command, args = get_input()
    elif command == "trace":
        if check_args(args, command, minimum=1, nodes=args[1:], keyword="all", keyword_pos=0):
            if args[0] == "all":
                for node in G.nodes:
                    print_routing_table(node)
                    print
            else:
                for arg in args:
                    print_routing_table(arg)
                    print
        command, args = get_input()
    elif command == "route": 
        if check_args(args, command, expected=2, nodes=args):
            src = args[0]
            dest = args[1]
            # TODO: change this to find the shortest path based on the routing_table
            try: 
                path = nx.shortest_path(G, src, dest, weight="weight")
                print "Shortest path between %s and %s is: " % (src, dest)
                print_path(path)
            except nx.NetworkXNoPath:
                print "There is no path between %s and %s" % (src, dest)
        command, args = get_input()
    elif command == "cost": 
        if check_args(args, command, nodes=args[:-1], expected=3, keyword="fail", keyword_pos=2):
            src = args[0]
            dest = args[1]
            cost = args[2]
            # remove edge if it exists
            if (src, dest) in G.edges:
                G.remove_edge(src, dest)
            if cost == "fail":
                cost = 'inf'
            update_routing_table(src, dest, float(cost))
            G.add_edges_from([(src, dest, {'weight':float(cost)})])
            print G.edges.items()
        command, args = get_input()
    elif command == "exchange": 
        if check_args(args, command, expected=1, keyword="stable", keyword_pos=0):
            iterations = int(args[0]) if args[0] != "stable" else len(G.nodes) - 1    # specifies the number of iterations
            for i in range(iterations):                                               # it takes |V| - 1 iterations for stability where |V| is the number of vertices
                split_horizon() if SPLIT_HORIZON else bellman_ford() 
        command, args = get_input()
    elif command == "split-horizon": 
        SPLIT_HORIZON = not SPLIT_HORIZON                                             # toggle split horizon
        print "Split horizon has been %s" % 'enabled' if SPLIT_HORIZON else 'disabled'
        command, args = get_input()
    else:
        if len(command.replace(' ','')) > 0: # command isn't enter or whitespace
            print "%s is not a valid command, type help to display the list of commands" % command
        command, args = get_input()

