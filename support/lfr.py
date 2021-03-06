# Richard Darst, May 2012

import numpy
import os
from os.path import join
import shutil
import subprocess
import tempfile
import textwrap
import threading
lock = threading.Lock()

import networkx
import scipy.stats

import pcd.util
import pcd.nxutil
from pcd.nxutil import setCmtyAssignments


#scipy.stats.powerlaw
#def powlaw(a):
#    return scipy.stats.powerlaw(a).rvs()
#def A(gamma, beta, N, avg_deg, mu):
#    g = networkx.Graph()
#    for n in range(N):
#        g.add_node(n)
#        g.node[n]['k'] = powlaw(gamma)
#
#    print g.summary()
#    print sum(d['k'] for n,d in g.nodes(1))


progdir = '/home/richard/research/cd/code-dl/lfr_benchmarks/new'
tmpbase = "."

from pcd.support.algorithms import _get_file
# _get_file implements a search path to locate binaries.

def read_file(fname):
    for line in open(fname):
        line = line.strip().split()
        yield tuple(pcd.util.leval(x) for x in line)
def makeargs(dict):
    args = [ ]
    for k,v in dict.items():
        args.extend(['-'+k, str(v)])
    return args



def benchmark(N, k, maxk, gamma, beta, mu,
              minc=None, maxc=None, pause=False):
    """Unweighted, Undirected, Non-overlapping benchmark graph.

    This is the graph supporting Lancichenetti, Fortunato, Radicci,
    PRE 78 046110 (2008).

    Arguments are:

    N     # number of nodes
    k     # average degree
    maxk  # maximum degree
    gamma # exponent for the degree distribution
    beta  # exponent for the community size distribution
    mu    # mixing parameter
    minc  # minimum for the community sizes (optional)
    maxc  # maximum for the community sizes (optional)

    Example parameters:
    N=1000, k=15, maxk=100, gamma=2, beta=1, mu=.1
    """

    if minc is None: minc = ""
    if maxc is None: maxc = ""

    params = textwrap.dedent("""\
    %(N)s
    %(k)s
    %(maxk)s
    %(gamma)s
    %(beta)s
    %(mu)s
    %(minc)s
    %(maxc)s
    """%locals())

    prog = _get_file('lfr_benchmarks/new/benchmark_2_2/benchmark')
    kwargs = { }
    args = [ prog ] + makeargs(kwargs)
    print "Arguments are: ", " ".join(args)

    with pcd.util.tmpdir_context(chdir=True, prefix='tmp-lfrbenchmark', dir=tmpbase) as tmpdir:
        open('parameters.dat', 'w').write(params)

        retcode = subprocess.call(args)
        assert retcode == 0

        g = networkx.Graph()
        for n, c in read_file('community.dat'):
            g.add_node(n-1, cmty=c-1)
        for n1, n2 in read_file('network.dat'):
            g.add_edge(n1-1, n2-1)
        g.graph['statistics'] = open('statistics.dat').read()
        #g.graph['stats'] = stats(g)

        if pause:
            import fitz.interact ; fitz.interact.interact()
    return g


def binary(pause=False, **kwargs):
    """Binary networks with overlapping nodes.

    -N              [number of nodes]
    -k              [average degree]
    -maxk           [maximum degree]
    -mu             [mixing parameter]
    -t1             [minus exponent for the degree sequence]
    -t2             [minus exponent for the community size distribution]
    -minc           [minimum for the community sizes]
    -maxc           [maximum for the community sizes]
    -on             [number of overlapping nodes]
    -om             [number of memberships of the overlapping nodes]
    -C              [average clustering coefficient]


    -N, -k, -maxk, -mu have to be specified. For the others, the
    program can use default values:
    t1=2, t2=1, on=0, om=0, minc and maxc will be chosen close to the
    degree sequence extremes.
    If you set a parameter twice, the latter one will be taken.
    """
    prog = _get_file('lfr_benchmarks/new/binary_networks/benchmark')
    args = [ prog ] + makeargs(kwargs)
    print "Arguments are: ", " ".join(args)

    with pcd.util.tmpdir_context(chdir=True, prefix="tmp-lfrbenchmark", dir=tmpbase):
        retcode = subprocess.call(args)
        assert retcode == 0

        g = networkx.Graph()
        #for n, c in read_file('community.dat'):
        #    g.add_node(n-1, cmty=c-1)
        for x in read_file('community.dat'):
            n, cmtys = x[0], x[1:]
            cmtys = [c-1 for c in cmtys]
            g.add_node(n-1, cmtys=cmtys)
        for n1, n2 in read_file('network.dat'):
            g.add_edge(n1-1, n2-1)
        g.graph['statistics'] = open('statistics.dat').read()
        #g.graph['stats'] = stats(g)
        if pause:
            import fitz.interact ; fitz.interact.interact()
    return g

def weighted(pause=False, **kwargs):
    """Undirected weighted networks with overlapping nodes.
,
    This program is an implementation of the algorithm described in
    the paper\"Directed, weighted and overlapping benchmark graphs for
    community detection algorithms\", written by Andrea Lancichinetti
    and Santo Fortunato. In particular, this program is to produce
    undirected weighted networks with overlapping nodes.  Each
    feedback is very welcome. If you have found a bug or have
    problems, or want to give advises, please contact us:


    -N              [number of nodes]
    -k              [average degree]
    -maxk           [maximum degree]
    -mut            [mixing parameter for the topology]
    -muw            [mixing parameter for the weights]
    -beta           [exponent for the weight distribution]
    -t1             [minus exponent for the degree sequence]
    -t2             [minus exponent for the community size distribution]
    -minc           [minimum for the community sizes]
    -maxc           [maximum for the community sizes]
    -on             [number of overlapping nodes]
    -om             [number of memberships of the overlapping nodes]
    -C              [average clustering coefficient]


    -N, -k, -maxk, -muw have to be specified. For the others, the
    program can use default values:

    t1=2, t2=1, on=0, om=0, beta=1.5, mut=muw, minc and maxc will be
    chosen close to the degree sequence extremes.  If you set a
    parameter twice, the latter one will be taken.

    To have a random network use:
    -rand
    Using this option will set muw=0, mut=0, and minc=maxc=N, i.e.
    there will be one only community.
    Use option -sup (-inf) if you want to produce a benchmark whose
    distribution of the ratio of external degree/total degree is
    superiorly (inferiorly) bounded by the mixing parameter.

    The flag -C is not mandatory. If you use it, the program will
    perform a number of rewiring steps to increase the average cluster
    coefficient up to the wished value.  Since other constraints must
    be fulfilled, if the wished value will not be reached after a
    certain time, the program will stop (displaying a warning).

    Example1:
    ./benchmark -N 1000 -k 15 -maxk 50 -muw 0.1 -minc 20 -maxc 50
    Example2:
    ./benchmark -f flags.dat -t1 3
    """
    prog = _get_file('lfr_benchmarks/new/weighted_networks/benchmark')
    args = [ prog ] + makeargs(kwargs)
    print "Arguments are: ", " ".join(args)

    with pcd.util.tmpdir_context(chdir=True, prefix='tmp-lfrbenchmark', dir=tmpbase):
        retcode = subprocess.call(args)
        assert retcode == 0

        g = networkx.Graph()
        for x in read_file('community.dat'):
            n, cmtys = x[0], x[1:]
            cmtys = [c-1 for c in cmtys]
            g.add_node(n-1, cmtys=cmtys)
        for n1, n2, weight in read_file('network.dat'):
            g.add_edge(n1-1, n2-1, weight=weight)
        g.graph['statistics'] = open('statistics.dat').read()
        #g.graph['stats'] = stats(g)
        if pause:
            import fitz.interact ; fitz.interact.interact()
    return g


def hierarchical(pause=False, **kwargs):
    """Binary networks with overlapping nodes and hierarchies

    This program is an implementation of the algorithm described in
    the paper'Direc ted, weighted and overlapping benchmark graphs for
    community detection algorithm s', written by Andrea Lancichinetti
    and Santo Fortunato. In particular, this program is to produce
    binary networks with overlapping nodes and hierarchies.

    -N              [number of nodes]
    -k              [average degree]
    -maxk           [maximum degree]
    -t1             [minus exponent for the degree sequence]
    -t2             [minus exponent for the community size distribution]
    -minc           [minimum for the micro community sizes]
    -maxc           [maximum for the micro community sizes]
    -on             [number of overlapping nodes]
    -om             [number of memberships of the overlapping nodes]
    -minC           [minimum for the macro community size]
    -maxC           [maximum for the macro community size]
    -mu1            [mixing parameter for the macro communities (see Readme file)]
    -mu2            [mixing parameter for the micro communities (see Readme file)]

    Example2:
    ./hbenchmark -f flags.dat
    ./hbenchmark -N 10000 -k 20 -maxk 50 -mu2 0.3 -minc 20 -maxc 50 -minC 100 -maxC 1000 -mu1 0.1
    """
    prog = _get_file('lfr_benchmarks/new/hierarchical_bench2_2/hbenchmark')
    args = [ prog ] + makeargs(kwargs)
    print "Arguments are: ", " ".join(args)

    with tmpdir_context(chdir=True, prefix="tmp-lfrbenchmark", dir=tmpbase):
        retcode = subprocess.call(args)
        assert retcode == 0

        g = networkx.Graph()
        for n, c in read_file('community_first_level.dat'):
            g.add_node(n-1, microC=c-1)
        for n, c in read_file('community_second_level.dat'):
            g.add_node(n-1, macroC=c-1)
        for n1, n2 in read_file('network.dat'):
            g.add_edge(n1-1, n2-1)
        g.graph['stats'] = stats(g)
        if pause:
            import fitz.interact ; fitz.interact.interact()
    return g


def stats(g):
    cmtys = { }
    for node, data in g.node.iteritems():
        for c in pcd.nxutil._iterCmtys(data):
            cmtys.setdefault(c, set())
            cmtys[c].add(node)
    import collections
    cmtysizes = collections.defaultdict(int)
    for c, members in cmtys.iteritems():
        cmtysizes[len(members)] += 1
    return {
        "q":len(cmtys),
        "n_mean":numpy.mean([len(ns) for ns in cmtys.itervalues()]),
        "n_std":numpy.std([len(ns) for ns in cmtys.itervalues()]),
        "cmtysizes":tuple(sorted(cmtysizes.iteritems())),
        }


if __name__ == "__main__":
    #A(1, 1, 100, 10, 1)

    g = hierarchical_graph(
        N=10000, k=10, maxk=100,
        mu1=.3, mu2=.4,
        minC=500, maxC=2000,
        minc=10, maxc=100,
        )
    print networkx.info(g)

    g = binary_graph(
        N=1000, k=15, maxk=50, mu=.1,
        )
    print networkx.info(g)



    g = benchmark()
    networkx.write_gml(g, "graph.gml")
