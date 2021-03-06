# Richard Darst, September 2011

import numpy
import random
import networkx.algorithms

import pcd.models
import pcd.graphs
import pcd.util
pcd.util.logNumber = 100

gamma = .4

g = pcd.graphs.polopa_tribes(weightAllied=-1, weightHostile=2)
G = pcd.models.Graph.fromNetworkX(g, defaultweight=1, diagonalweight=0)

G._greedy(gamma=gamma)
G._greedy(gamma=gamma)
G._greedy(gamma=gamma)
G.remap()
#G.viz()
print G.q
subG = G.supernodeGraph(gamma=gamma, multiplier=1000)

G2 = G.copy()
G2.minimize(gamma=gamma)


print
print subG.imatrix
print subG._greedy(gamma=gamma)
print subG._greedy(gamma=gamma)
print subG.minimize(gamma=gamma)

G.loadFromSupernodeGraph(subG)
