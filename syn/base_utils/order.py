from collections import defaultdict

#-------------------------------------------------------------------------------
# Order Relations


class LE(object):
    def __init__(self, A, B):
        self.A = A
        self.B = B


#-------------------------------------------------------------------------------
# Utilities

def _nodes(relations):
    ret = set()
    for rel in relations:
        ret.add(rel.A)
        ret.add(rel.B)
    return ret

def _incoming(relations):
    ret = defaultdict(set)
    for rel in relations:
        ret[rel.B].add(rel.A)
    return ret

def _outgoing(relations):
    ret = defaultdict(set)
    for rel in relations:
        ret[rel.A].add(rel.B)
    return ret

def _is_free(node, edges):
    return not edges[node]

def _free_nodes(nodes, edges):
    return {node for node in nodes if _is_free(node, edges)}

#-------------------------------------------------------------------------------
# Topological Sort

def topological_sorting(nodes, relations):
    '''An implementation of Kahn's algorithm.
    '''
    ret = []
    nodes = set(nodes) | _nodes(relations)
    inc = _incoming(relations)
    out = _outgoing(relations)
    free = _free_nodes(nodes, inc)

    while free:
        n = free.pop()
        ret.append(n)
        
        out_n = list(out[n])
        for m in out_n:
            out[n].remove(m)
            inc[m].remove(n)
            if _is_free(m, inc):
                free.add(m)

    if not all(_is_free(node, inc) and _is_free(node, out) for node in nodes):
        raise ValueError("Cycle detected")
    return ret

#-------------------------------------------------------------------------------
# __all__

__all__ = ('LE',
           'topological_sorting',)

#-------------------------------------------------------------------------------
