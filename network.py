import argparse as ap
import networkx as nx
import csv
import sys

# Parse command line arguments
parser = ap.ArgumentParser(description = 'Simplified network in python')
parser.add_argument('-f', '--file', required=True, help='reads the specified CSV file as input for the network')
args = parser.parse_args()

def readcsv(file):
    with open(file, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        nodesAndEdges = []
        for row in reader:
            if row:                 # check that list isn't empty
                if "#" not in row[0]:   # check that the line isn't a comment
                    nodesAndEdges.append(row)    # TODO: remove comments from row
    return nodesAndEdges

def format_edges(raw_edges):
    edges = []
    for edge in raw_edges:
        edges.append((edge[0], edge[1], {'weight': int(edge[2])}))
    return edges

def print_routing_tables(graph):
    print "Routing tables for the graph:", "\n"
    for node in graph.nodes:
        print "\t", node, ': ', graph.nodes[node]['routing_table'].routing_table

def print_routing_table(graph, node):
    routing_table = graph.nodes[node]['routing_table'].routing_table
    print "Routing table for %s:" % node
    for node in routing_table:
        print "\t", node, "\t", routing_table[node]


class RoutingTable:

    def __init__(self, graph, node):
        self.name = node
        self.routing_table = {adj_node:graph.adj[node][adj_node]['weight'] for adj_node in graph.adj[node]} # add adjacent nodes to the routing table
        non_adjacent_nodes = list(set(graph.nodes) - set(graph.adj[node]) - set(node)) 
        self.routing_table.update({non_adj_node: float('inf') for non_adj_node in non_adjacent_nodes}) # add non-adjacent nodes to the routing table
        self.routing_table[node] = 0

def usage():
    print "Usage: <command> <argument(s)>"
    print "\thelp or ?                   displays this help menu"
    print "\ttrace N1 N2 N3/all          returns the routing table for the given nodes"
    print "\troute N1 N2                 finds the best route between two given nodes"
    print "\tcost src dest cost/fail     changes the cost of an edge"
    print "\texchange 2/stability        compute routing tables for any number of exchanges of until stability is achieved"
    print "\tsplit-horizon               engage split-horizon to combat slow convergence" 
    print
    print "Examples: "
    print "\ttrace all"
    print "\tcost N1 N2 fail"
    print "\texchange 5"

def get_input():
    user_input = raw_input("> ")
    command = user_input.split(" ")[0]
    args = user_input.split(" ")[1:]
    return command, args

# Returns False if the arguments are empty or invalid
def check_args(graph, args, command, expected=None, min=None):
    if min != None and len(args) < min:
        print "%s requires at least  %s arguments - type help for an example" % (command, min)
        return False
    elif expected != None and len(args) != expected:
        print "%s requires %s arguments - type help for an example" % (command, expected)
        return False
    for arg in args:
        if arg not in graph.nodes:
            print "%s is not a node in the graph - all arguments must be nodes!" % arg
            return False
    return True
    
def print_path(path):
    for node in path[:-1]:
        print node, " -> ",
    print path[-1]

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
    G.nodes[node]['routing_table'] = RoutingTable(G, node)

print nx.shortest_path(G, "N1", "N3", weight="weight")

# Start the loop periodic exchanges
AVAILABLE_COMMANDS = ["help","?","exit","quit","stop"]
print "To exit, press ctrl + c or enter exit"
command, args = get_input()

while command not in ["exit","quit","stop","q"]:
#while any(command in available_command for available_command in AVAILABLE_COMMANDS): # check if the input contains a command
    if command in ["help","?"]:
        usage()
        command, args = get_input()
    elif command == "trace":
        if check_args(G, args, command, min=1) or (args[0] == "all"):
            if args[0] == "all":
                for node in G.nodes:
                    print_routing_table(G, node)
                    print
            else:
                for arg in args:
                    print_routing_table(G, arg)
                    print
        command, args = get_input()
    elif command == "route": 
        if check_args(G, args, command, expected=2):
            src = args[0]
            dest = args[1]
            path = nx.shortest_path(G, src, dest, weight="weight")
            print "Shortest path between %s and %s is: " % (src, dest)
            print_path(path)
        command, args = get_input()
    elif command == "cost": continue
    elif command == "exchange": continue
    elif command == "split_horizon": continue
    else:
        if len(command.replace(' ','')) > 0: # command isn't enter or whitespace
            print "%s is not a valid command, type help to display the list of commands" % command
        command, args = get_input()

