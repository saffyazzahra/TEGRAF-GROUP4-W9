from collections import defaultdict
import sys

# increase recursion depth for deep DFS trees
sys.setrecursionlimit(20000)

# one side of conflict pair,, back edges that must share same side
# low/high are the lowest and highest back edges (by lowpoint) in run
class Interval:
    def __init__(self, low=None, high=None):
        self.low = low
        self.high = high

    def empty(self): # no back edges in this side
        return self.low is None and self.high is None

    def copy(self):
        return Interval(self.low, self.high)

# back edges in left must be on opposite side of back edges in right
class ConflictPair:
    def __init__(self, left=None, right=None):
        self.left = left if left is not None else Interval()
        self.right = right if right is not None else Interval()

    def swap(self): # flip which side is left and right
        self.left, self.right = self.right, self.left


def check_planarity_dfr(graph, all_nodes=None):
    if not graph:
        return True
    if all_nodes is None:
        all_nodes = list(graph.keys())

    # remove self-loops and parallel edges,, auto nonplanar
    adj = {n: set() for n in all_nodes}
    for u, neighbors in graph.items():
        for v in neighbors:
            if u != v:
                adj.setdefault(u, set()).add(v)
                adj.setdefault(v, set()).add(u)

    n = len(adj)
    m = sum(len(s) for s in adj.values()) // 2
    if n >= 3 and m > 3 * n - 6: # planar graphs cant have more than 3n-6 edges,, eulers formula
        return False

    height = {v: None for v in adj} # depth of each node in dfs tree
    parent_edge = {} # tree edge that leads into each node
    lowpt = {} # lowest height reachable from an edge using one back edge
    lowpt2 = {} # second lowest height reachable
    nesting_depth = {} # key used to order edges so inner cycles come first
    out_edges = defaultdict(list) # edges oriented away from each node
    oriented = set() # edges already given a direction

    # dfs that orients every edge and computes lowpoints,, builds spanning tree
    def orient(v):
        e = parent_edge[v]
        for w in adj[v]:
            if (v, w) in oriented or (w, v) in oriented: # edge already handled
                continue
            vw = (v, w)
            oriented.add(vw)
            out_edges[v].append(w)
            lowpt[vw] = height[v]
            lowpt2[vw] = height[v]
            if height[w] is None: # tree edge
                parent_edge[w] = vw
                height[w] = height[v] + 1
                orient(w)
            else: # back edge,, goes up to an ancestor
                lowpt[vw] = height[w]

            # nesting order,, smaller lowpoint first,, chordal edges slightly later
            nesting_depth[vw] = 2 * lowpt[vw]
            if lowpt2[vw] < height[v]:
                nesting_depth[vw] += 1

            # pass lowpoints of this edge up to parent edge e
            if e is not None:
                if lowpt[vw] < lowpt[e]:
                    lowpt2[e] = min(lowpt[e], lowpt2[vw])
                    lowpt[e] = lowpt[vw]
                elif lowpt[vw] > lowpt[e]:
                    lowpt2[e] = min(lowpt2[e], lowpt[vw])
                else:
                    lowpt2[e] = min(lowpt2[e], lowpt2[vw])

    roots = []
    for node in adj: # loop all nodes so disconnected graphs covered
        if height[node] is None:
            height[node] = 0
            parent_edge[node] = None
            roots.append(node)
            orient(node)

    # visit edges of each node in nesting order
    ordered = {v: sorted(out_edges[v], key=lambda w: nesting_depth[(v, w)]) for v in adj}

    # dfs tries to split back edges into a left and right side
    S = [] # stack of conflict pairs
    stack_bottom = {} # top of stack when we started an edge
    lowpt_edge = {} # back edge that gives lowpoint of an edge
    ref = {} # links edges that are forced onto same side

    def top():
        return S[-1] if S else None

    # a side conflicts with edge b if highest back edge reaches lower than b
    def conflicting(interval, b):
        return (not interval.empty()) and lowpt[interval.high] > lowpt[b]

    # lowest return height of a conflict pair
    def lowest(P):
        if P.left.empty():
            return lowpt[P.right.low]
        if P.right.empty():
            return lowpt[P.left.low]
        return min(lowpt[P.left.low], lowpt[P.right.low])

    # pushes new back edges onto stack,, checks if edge forces conflicting sides,, returns False if nonplanar
    def add_constraints(ei, e):
        P = ConflictPair()

        # merge return edges of ei into the right side of P
        while True:
            Q = S.pop()
            if not Q.left.empty():
                Q.swap()
            if not Q.left.empty(): # both sides filled,, cannot place,, nonplanar
                return False
            if lowpt[Q.right.low] > lowpt[e]:
                if P.right.empty():
                    P.right = Q.right.copy()
                else:
                    ref[P.right.low] = Q.right.high
                P.right.low = Q.right.low
            else: # same side as lowpoint edge of e
                ref[Q.right.low] = lowpt_edge[e]
            if top() is stack_bottom[ei]:
                break

        # merge conflicting return edges of earlier siblings into left side of P
        while conflicting(top().left, ei) or conflicting(top().right, ei):
            Q = S.pop()
            if conflicting(Q.right, ei):
                Q.swap()
            if conflicting(Q.right, ei): # conflicts on both sides,, nonplanar
                return False
            ref[P.right.low] = Q.right.high
            if Q.right.low is not None:
                P.right.low = Q.right.low
            if P.left.empty():
                P.left = Q.left.copy()
            else:
                ref[P.left.low] = Q.left.high
            P.left.low = Q.left.low

        if not (P.left.empty() and P.right.empty()):
            S.append(P)
        return True

    # drop back edges that end at u since they are fully resolved
    def remove_back_edges(u):
        while S and lowest(top()) == height[u]:
            S.pop()
        if S:
            P = S.pop()
            while P.left.high is not None and P.left.high[1] == u: # trim left
                P.left.high = ref.get(P.left.high)
            if P.left.high is None and P.left.low is not None:
                ref[P.left.low] = P.right.low
                P.left.low = None
            while P.right.high is not None and P.right.high[1] == u: # trim right
                P.right.high = ref.get(P.right.high)
            if P.right.high is None and P.right.low is not None:
                ref[P.right.low] = P.left.low
                P.right.low = None
            S.append(P)

    def test(v): # goes thru edges of v in nesting order
        e = parent_edge[v]
        for w in ordered[v]:
            ei = (v, w)
            stack_bottom[ei] = top()
            if ei == parent_edge[w]: # tree edge
                if not test(w):
                    return False
            else: # back edge
                lowpt_edge[ei] = ei
                S.append(ConflictPair(right=Interval(ei, ei)))

            # integrate the new return edges of ei
            if lowpt[ei] < height[v]:
                if w == ordered[v][0]: # first edge just passes its lowpoint up
                    lowpt_edge[e] = lowpt_edge[ei]
                else:
                    if not add_constraints(ei, e):
                        return False

        # remove back edges returning to the parent
        if e is not None:
            u = e[0]
            remove_back_edges(u)
            # side of e follows the side of its highest return edge
            if lowpt[e] < height[u]:
                hl = top().left.high
                hr = top().right.high
                if hl is not None and (hr is None or lowpt[hl] > lowpt[hr]):
                    ref[e] = hl
                else:
                    ref[e] = hr
        return True

    for root in roots: # every component must pass on its own
        S.clear()
        if not test(root):
            return False
    return True # all constraints satisfiable -> planar

# input
def main():
    try:
        num_edges = int(input("Enter total number of edges: "))
        print("Enter each edge as two space-separated values (e.g., 0 1):")
        
        graph = defaultdict(list)
        nodes = set()
        
        for i in range(num_edges):
            while True:
                line = input(f"Edge {i+1}: ").strip()
                if not line:
                    continue
                parts = line.split()
                if len(parts) != 2:
                    print("Error: Enter exactly two nodes separated by a space.")
                    continue
                
                # parse nodes as integers,, change to string parsing if graph uses string names
                try:
                    u, v = int(parts[0]), int(parts[1])
                except ValueError:
                    u, v = parts[0], parts[1]
                
                graph[u].append(v)
                graph[v].append(u) # undirected graph connection
                nodes.add(u)
                nodes.add(v)
                break
        
        if not nodes:
            print("No graph entered.")
            return
            
        is_planar = check_planarity_dfr(dict(graph), list(nodes))
        
        if is_planar:
            print("The graph is PLANAR (left-right constraints are consistent).")
        else:
            print("The graph is NON-PLANAR (left-right constraints conflict).")
            
    except ValueError:
        print("Invalid input. Please enter a valid integer for the number of edges.")

if __name__ == "__main__":
    main()
