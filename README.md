# pyRoute - Distance Vector Routing in Python

## Requirements 
* [Python 2.7](https://www.python.org/downloads/)
* [pip](https://pip.pypa.io/en/stable/installing/) is pre-installed with Python 2.7.9 and higher
* `pip install argparse, networkx`

## Installation & Running the project
* `git clone git@github.com:ppartarr/DistanceVectorRouting.git`
* `python network.py -f nodes.csv` 
  * [nodes.csv](https://github.com/ppartarr/DistanceVectorRouting/blob/master/nodes.csv) is a file specifying a set of nodes and a set of links with costs. Feel free to make your own and import that instead.

## Usage
Once in the command line interface type `help` to see the available commands
![Using help in the command line interface](https://github.com/ppartarr/DistanceVectorRouting/blob/master/img/DistanceVectorRouting.png)

## Requirements
Considering a simplified point-to-point network description consisting of a set of nodes and a set of links with costs. Every node has a routing tabke with 3 columns: destination, source and outgoing link.

The idea is the read in a human-readable network description and simulate the distance-vector routing algorithm with periodic exchanges (i.e. regular intervals at which all nodes exchange vectors simultaneously) updating all node routing tables over any selected number of iterations.

A user should be able to:
* compute routing tables for any preset number of exchanges
* preset any link to change cost or fail after any chosen exchange (assume for simplicity that neighbours notice cost change immediatly)
* view the best route between any source & destination after any iteration
* trace the routing table of any set of nodes for any specified number of iterations
* engage **split-horizon** on request to help combat slow-convergence



