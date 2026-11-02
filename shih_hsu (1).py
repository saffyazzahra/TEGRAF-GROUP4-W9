"""
shih_hsu.py
Informatics ITS - Graph Theory class - Group ...

Planarity test based on the Shih-Hsu algorithm (PC-trees).

HOW TO RUN:  python shih_hsu.py   then type the edges of your graph.

IDEA IN SHORT
-------------
1. Split the graph into biconnected blocks (a graph is planar iff all blocks are).
2. For one block, run a DFS and number the vertices in DFS order (0 = root).
   Every non-tree edge is a BACK EDGE (x -> a) from a vertex x to an ancestor a.
3. Build a PC-tree:
     * 'P' node : a vertex whose neighbours may be permuted arbitrarily.
     * 'C' node : a cycle (a finished piece of the embedding). Its neighbours have
                  a FIXED circular order (they can only be reversed as a whole).
     * 'L' leaf : a pending back edge, labelled with the DFS number of its ancestor.
   Initially the tree is the DFS tree, and each back edge (x -> a) is a leaf
   hanging on x with label a.
4. Process vertices v = n-1, ..., 0 (children before parents):
     all leaves labelled v (the back edges that end in v) must end up
     CONSECUTIVE in the circular order of the tree's leaves, because together with
     v they close cycles whose other side must stay on the outer face.
       - If this cannot be arranged           -> the graph is NOT planar.
       - Otherwise the leaves labelled v are removed ("embedded") and the nodes
         that lie on the cycles are merged into ONE C-node.
5. If every vertex is processed without failure, the block is planar.

NOTE: the original paper does each reduction in amortised O(1) per step and gets
O(n) total. To keep the code readable we recompute labels with a plain DFS at each
step, so this version is O(n * m). The logic of the algorithm is the same.
"""

import sys

sys.setrecursionlimit(10000)  # the DFS below is recursive (easier to read)


# ----------------------------------------------------------------------
# Graph helpers
# ----------------------------------------------------------------------
def build_adjacency(n, edges):
    """
    Adjacency lists of the underlying SIMPLE graph.
    Self-loops and parallel edges never change planarity, so we drop them.
    """
    adj = [[] for _ in range(n)]
    seen = set()
    for u, v in edges:
        if u == v or (min(u, v), max(u, v)) in seen:
            continue
        seen.add((min(u, v), max(u, v)))
        adj[u].append(v)
        adj[v].append(u)
    return adj



# Biconnected components (DFS with an edge stack)
def biconnected_components(n, adj):
    """
    Returns a list of blocks; every block is a list of edges (u, v).
    A graph is planar  <=>  every one of its blocks is planar,
    which is why Shih-Hsu only has to handle biconnected graphs.
    """
    disc = [-1] * n      # DFS discovery time
    low = [0] * n        # lowest discovery time reachable via one back edge
    timer = [0]
    edge_stack = []
    blocks = []

    def dfs(u, parent):
        disc[u] = low[u] = timer[0]
        timer[0] += 1
        for w in adj[u]:
            if w == parent:
                continue
            if disc[w] == -1:                       # tree edge
                edge_stack.append((u, w))
                dfs(w, u)
                low[u] = min(low[u], low[w])
                if low[w] >= disc[u]:               # u separates w's subtree
                    block = []
                    while True:
                        e = edge_stack.pop()
                        block.append(e)
                        if e == (u, w):
                            break
                    blocks.append(block)
            elif disc[w] < disc[u]:                 # back edge going up
                edge_stack.append((u, w))
                low[u] = min(low[u], disc[w])

    for s in range(n):
        if disc[s] == -1:
            dfs(s, -1)
    return blocks

# Quick rejection (optional): a planar simple graph has at most 3n-6 edges.
USE_EULER_BOUND = True

# status of a node during one reduction
EMPTY, FULL, PARTIAL = 0, 1, 2


class PCNode:
    """A node of the PC-tree."""

    def __init__(self, kind, label=None):
        self.kind = kind      # 'P', 'C' or 'L'
        self.label = label    # only for leaves: DFS number of the ancestor
        self.nbrs = []        # neighbours (circular order matters for 'C')

    def replace(self, old, new):
        """Replace neighbour `old` by `new`, keeping its position in the list."""
        self.nbrs[self.nbrs.index(old)] = new


class PCTree:
    def __init__(self, n, tree_parent, back_edges):
        """
        n           : number of vertices of the block (DFS numbers 0..n-1)
        tree_parent : tree_parent[v] = DFS parent of v (None for the root)
        back_edges  : list of (x, a): back edge from x up to its ancestor a
        """
        self.nodes = set()                  # all internal (P / C) nodes
        self.leaves_by_label = {a: [] for a in range(n)}
        self.vertex_node = [self._new('P') for _ in range(n)]
        # vertex nodes whose turn has not come yet may never be deleted/merged
        self.protected = set(self.vertex_node)

        # DFS tree edges
        for v in range(1, n):
            self._link(self.vertex_node[v], self.vertex_node[tree_parent[v]])
        # one leaf per back edge, hanging on the lower endpoint
        for x, a in back_edges:
            leaf = PCNode('L', label=a)
            self.leaves_by_label[a].append(leaf)
            self._link(leaf, self.vertex_node[x])

    # ------------------------------------------------------------------
    # small helpers
    # ------------------------------------------------------------------
    def _new(self, kind):
        node = PCNode(kind)
        self.nodes.add(node)
        return node

    @staticmethod
    def _link(a, b):
        a.nbrs.append(b)
        b.nbrs.append(a)

    # ------------------------------------------------------------------
    # main loop
    # ------------------------------------------------------------------
    def run(self):
        """Process vertices in reverse DFS order. True = block is planar."""
        for v in range(len(self.vertex_node) - 1, -1, -1):
            if not self._embed_back_edges_into(v):
                return False
        return True

    def _embed_back_edges_into(self, v):
        """
        Embed every back edge that ends in v.

        The leaves labelled v lie in one or more "lobes": the parts of the tree
        hanging below the neighbours of v's node. v is a cut vertex between
        lobes, so every lobe is handled on its own:
          1. cut the lobe off from v and put a temporary leaf `w` in v's place
             (w stands for "the position of v on the cycle");
          2. reduce: the leaves labelled v together with w must be consecutive
             (otherwise some pending edge would be trapped inside a cycle);
          3. delete the leaves labelled v (their edges are drawn now) and
             re-attach w's neighbour to v.  The lobe has become one C node
             (the cycle) that is linked to v.
        """
        vnode = self.vertex_node[v]
        self.protected.discard(vnode)       # v's turn is happening now
        S = set(self.leaves_by_label[v])

        lobes = []
        for c in list(vnode.nbrs):
            beyond = self._leaves_beyond(c, vnode)
            hit = [leaf for leaf in beyond if leaf in S]
            if hit:
                lobes.append((c, beyond, hit))

        for c, beyond, hit in lobes:
            if c.kind == 'L':               # the cycle is already closed
                vnode.nbrs.remove(c)        # (merged triangle): just delete it
                continue
            w = PCNode('L')                 # temporary leaf standing for v
            w.nbrs = [c]
            c.replace(vnode, w)
            vnode.nbrs.remove(c)
            if not self._reduce(set(hit) | {w}, beyond + [w]):
                return False                # consecutiveness impossible
            for leaf in hit:                # the back edges are drawn: delete
                leaf.nbrs[0].nbrs.remove(leaf)
            u = w.nbrs[0]                   # w goes away, v takes its place
            u.replace(w, vnode)
            vnode.nbrs.append(u)

        self.leaves_by_label[v] = []
        self._cleanup()
        return True

    @staticmethod
    def _leaves_beyond(start, came_from):
        """All leaves in the part of the tree reached from `start` without
        going back through `came_from`."""
        found, stack = [], [(start, came_from)]
        while stack:
            node, par = stack.pop()
            if node.kind == 'L':
                found.append(node)
            for nb in node.nbrs:
                if nb is not par:
                    stack.append((nb, node))
        return found

    # ------------------------------------------------------------------
    # clean-up after deleting leaves
    # ------------------------------------------------------------------
    def _cleanup(self):
        """
        Remove useless nodes:
          * an internal node with <= 1 neighbour is a dead end (everything
            below it was embedded)  -> delete it;
          * an internal node with exactly 2 neighbours is just a path
            -> splice it out.
        Unprocessed vertex nodes are protected, because a later step needs them.
        """
        changed = True
        while changed:
            changed = False
            for node in list(self.nodes):
                if node in self.protected:
                    continue
                if len(node.nbrs) <= 1:
                    for nb in node.nbrs:
                        nb.nbrs.remove(node)
                    self.nodes.discard(node)
                    changed = True
                elif len(node.nbrs) == 2:
                    a, b = node.nbrs
                    a.replace(node, b)
                    b.replace(node, a)
                    self.nodes.discard(node)
                    changed = True

    # ------------------------------------------------------------------
    # the PC-tree reduction: make the leaves in S consecutive
    # ------------------------------------------------------------------
    def _reduce(self, S, leaves):
        """
        Rearrange the tree so that the leaves in S are consecutive in the
        circular order of `leaves` (all leaves of this tree). False = impossible.

        Trick: root the tree at an EMPTY leaf r (a leaf not in S). Then the
        circular problem becomes the usual "linear" one (like a PQ-tree).
        """
        empty_leaves = [l for l in leaves if l not in S]
        if not empty_leaves:
            return True                     # every leaf is in S: trivial
        root = empty_leaves[0]

        # ---- 1. root the tree, count S-leaves below every node --------
        parent, cnt, size = {root: None}, {}, {}

        def visit(node):
            if node.kind == 'L':
                cnt[node] = 1 if node in S else 0
                size[node] = 1
                return
            cnt[node] = size[node] = 0
            for nb in node.nbrs:
                if nb is not parent[node]:
                    parent[nb] = node
                    visit(nb)
                    cnt[node] += cnt[nb]
                    size[node] += size[nb]

        parent[root.nbrs[0]] = root
        visit(root.nbrs[0])
        cnt[root], size[root] = 0, 1

        def status(node):
            if cnt[node] == 0:
                return EMPTY
            return FULL if cnt[node] == size[node] else PARTIAL

        def children(node):
            """Children in order; for a C node the cycle is cut at the parent."""
            if node.kind == 'C':
                i = node.nbrs.index(parent[node])
                return node.nbrs[i + 1:] + node.nbrs[:i]
            return [c for c in node.nbrs if c is not parent[node]]

        # ---- 2. pertinent root R = lowest node containing all of S -----
        total = len(S)
        R = root.nbrs[0]
        while True:
            below = [c for c in children(R) if cnt[c] == total]
            if not below:
                break
            R = below[0]
        if status(R) == FULL:
            return True                     # S is exactly one full subtree

        old_parent = {}   # item -> the (dissolved) node it used to hang from

        def make_group(group, X):
            """Put several same-status children of X under one new P node."""
            if len(group) == 1:
                old_parent[group[0]] = X
                return group[0]
            g = self._new('P')
            g.nbrs = list(group) + [X]      # X is a placeholder for the parent
            for c in group:
                c.replace(X, g)
            old_parent[g] = X
            return g

        def linearize(X):
            """
            X is a PARTIAL node below R. Dissolve it into a list of items
            ordered from its EMPTY end to its FULL end.  (None = failure)
            """
            kids = children(X)
            self.nodes.discard(X)
            if X.kind == 'P':
                E = [c for c in kids if status(c) == EMPTY]
                F = [c for c in kids if status(c) == FULL]
                A = [c for c in kids if status(c) == PARTIAL]
                if len(A) > 1:
                    return None             # two partial children: impossible
                items = []
                if E:
                    items.append(make_group(E, X))
                if A:
                    sub = linearize(A[0])
                    if sub is None:
                        return None
                    items += sub
                if F:
                    items.append(make_group(F, X))
                return items
            # X is a C node: children must look like  EMPTY* PARTIAL? FULL*
            # (or the mirror image, in which case we reverse the cycle)
            for seq in (kids, kids[::-1]):
                if self._matches_e_a_f(seq, status):
                    items = []
                    for c in seq:
                        if status(c) == PARTIAL:
                            sub = linearize(c)
                            if sub is None:
                                return None
                            items += sub
                        else:
                            old_parent[c] = X
                            items.append(c)
                    return items
            return None

        # ---- 3. rebuild the tree around the pertinent root --------------
        kids = children(R)
        up = parent[R]                      # empty side of the tree

        if R.kind == 'P':
            E = [c for c in kids if status(c) == EMPTY]
            F = [c for c in kids if status(c) == FULL]
            A = [c for c in kids if status(c) == PARTIAL]
            if len(A) > 2:
                return False
            if not A:
                return True                 # full children can be put together
            # New C node: [partial1 (empty->full)] [full group] [partial2 reversed]
            # and R itself (now holding the empty children) closes the cycle.
            items = linearize(A[0])
            if items is None:
                return False
            if F:
                items.append(make_group(F, R))
            if len(A) == 2:
                other = linearize(A[1])
                if other is None:
                    return False
                items += other[::-1]
            Q = self._new('C')
            Q.nbrs = items + [R]
            for it in items:
                it.replace(old_parent[it], Q)
            R.nbrs = E + [up, Q]
            return True

        # R is a C node: non-empty children must form one block  A? F* A?
        idx = [i for i, c in enumerate(kids) if status(c) != EMPTY]
        i, j = idx[0], idx[-1]
        if idx != list(range(i, j + 1)):
            return False                    # a gap of empty nodes inside
        if any(status(kids[k]) != FULL for k in range(i + 1, j)):
            return False                    # a partial node in the middle
        new_kids = kids[:i]
        for k in range(i, j + 1):
            c = kids[k]
            if status(c) == PARTIAL:
                sub = linearize(c)
                if sub is None:
                    return False
                if k == j:                  # right end: empty side must face right
                    sub = sub[::-1]
                for it in sub:
                    it.replace(old_parent[it], R)
                new_kids += sub
            else:
                new_kids.append(c)
        new_kids += kids[j + 1:]
        R.nbrs = [up] + new_kids
        return True

    @staticmethod
    def _matches_e_a_f(seq, status):
        """Does the status list look like  EMPTY* PARTIAL? FULL* ?"""
        i, n = 0, len(seq)
        while i < n and status(seq[i]) == EMPTY:
            i += 1
        if i < n and status(seq[i]) == PARTIAL:
            i += 1
        while i < n and status(seq[i]) == FULL:
            i += 1
        return i == n


# ----------------------------------------------------------------------
# Test of ONE biconnected block
# ----------------------------------------------------------------------
def block_is_planar(block_edges):
    # relabel the block's vertices 0..k-1
    verts = sorted({x for e in block_edges for x in e})
    index = {v: i for i, v in enumerate(verts)}
    k = len(verts)
    if k <= 4:
        return True                         # K4 is planar -> any block <= 4 vertices
    adj = [[] for _ in range(k)]
    for u, v in block_edges:
        adj[index[u]].append(index[v])
        adj[index[v]].append(index[u])
    if USE_EULER_BOUND and len(block_edges) > 3 * k - 6:   # Euler: m <= 3n-6
        return False

    # DFS: dfn = DFS number, tree_parent, and the list of back edges
    dfn = [-1] * k
    tree_parent = [None] * k
    order = []

    def dfs(u):
        dfn[u] = len(order)
        order.append(u)
        for w in adj[u]:
            if dfn[w] == -1:
                tree_parent[w] = u
                dfs(w)

    dfs(0)
    # renumber everything by DFS number so that "ancestor" = "smaller number"
    parent_by_dfn = [None] + [dfn[tree_parent[order[d]]] for d in range(1, k)]
    back_edges = []
    for u, v in block_edges:
        a, b = dfn[index[u]], dfn[index[v]]
        if parent_by_dfn[max(a, b)] == min(a, b):
            continue                        # this is a tree edge
        back_edges.append((max(a, b), min(a, b)))   # (descendant, ancestor)
    # a tree edge could appear twice in adj only with parallel edges (removed)

    return PCTree(k, parent_by_dfn, back_edges).run()


# ----------------------------------------------------------------------
# Public function
# ----------------------------------------------------------------------
def is_planar(n, edges):
    """True if the graph (n vertices numbered 0..n-1, list of edges) is planar."""
    adj = build_adjacency(n, edges)
    return all(block_is_planar(b) for b in biconnected_components(n, adj))


# ----------------------------------------------------------------------
# Interactive input
# ----------------------------------------------------------------------
def read_graph():
    """Ask the user for the edges. Vertex names can be numbers or words."""
    while True:
        try:
            m = int(input("Enter total number of edges: ").strip())
            if m >= 0:
                break
        except ValueError:
            pass
        print("Please enter a non-negative integer.")

    print("Enter each edge as two space-separated vertex names (e.g. 0 1):")
    label_to_id, edges = {}, []
    for i in range(m):
        while True:
            parts = input(f"Edge {i + 1}: ").split()
            if len(parts) == 2:
                break
            print("Error: enter exactly two vertices separated by a space.")
        for name in parts:                      # give every name an id 0..n-1
            label_to_id.setdefault(name, len(label_to_id))
        edges.append((label_to_id[parts[0]], label_to_id[parts[1]]))
    return len(label_to_id), edges


def main():
    print("=== Planarity test: Shih-Hsu algorithm (PC-tree) ===")
    while True:
        n, edges = read_graph()
        if n == 0:
            print("No graph entered.")
        elif is_planar(n, edges):
            print(f"Graph with {n} vertices and {len(edges)} edges is PLANAR.")
        else:
            print(f"Graph with {n} vertices and {len(edges)} edges is NON-PLANAR.")
        if input("\nTest another graph? (y/n): ").strip().lower() != "y":
            break
        print()


if __name__ == "__main__":
    main()
