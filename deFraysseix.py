from collections import defaultdict

def check_planarity_dfr(graph, all_nodes=None):
    if not graph:
        return True
    if all_nodes is None:
        all_nodes = list(graph.keys())
    start_node = all_nodes[0]

    # perform DFS to get discovery order (pre-order) and identify chords
    visited = {}
    dfs_order = [] # exact order of discovery of nodes in DFS
    chords = [] # list of edges that skip or loop back in dfs tree
    
    def dfs(u, parent=None): # numbers each node in discover order
        visited[u] = len(dfs_order)
        dfs_order.append(u)
        for v in graph.get(u, []):
            if v == parent:
                continue
            if v not in visited:
                dfs(v, u)
            elif visited[v] < visited[u]: # if already visited, recognise as chord
                # back-edge (chord)
                chords.append((v, u)) # stored as low/high vertex based on pre-order

    for node in all_nodes:
        if node not in visited:
            dfs(node)

    # compares 2 nodes to see if overlap or crosses
    def do_interlace(c1, c2): # mathematically,, if one chord's endpoints are nested inside other interval while other extend out, crosses
        u1, v1 = c1
        u2, v2 = c2
        u1, v1 = min(visited[u1], visited[v1]), max(visited[u1], visited[v1])
        u2, v2 = min(visited[u2], visited[v2]), max(visited[u2], visited[v2])
        return (u1 < u2 < v1 < v2) or (u2 < u1 < v2 < v1)

    conflict_graph = {chord: [] for chord in chords} # makes the graph of chords where edges represent crossing chords
    for i in range(len(chords)):
        for j in range(i + 1, len(chords)):
            if do_interlace(chords[i], chords[j]): # if chords cross, add edge in conflict graph,, cannot be colored same,, not bipartite
                conflict_graph[chords[i]].append(chords[j])
                conflict_graph[chords[j]].append(chords[i])

    # check if conflict graph is bipartite
    color = {} # using 0 and 1 for color rep
    for chord in chords: # if 2 connected chords have same color,, crosses,, nonplanar
        if chord not in color:
            color[chord] = 0
            queue = [chord]
            while queue:
                curr = queue.pop(0)
                for neighbor in conflict_graph[curr]:
                    if neighbor not in color:
                        color[neighbor] = 1 - color[curr]
                        queue.append(neighbor)
                    elif color[neighbor] == color[curr]:
                        return False # conflict found,, not bipartite -> not planar
                        
    return True # bipartite -> planar

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
            
        start_node = list(nodes)[0]
        is_planar = check_planarity_dfr(dict(graph), list(nodes))
        
        if is_planar:
            print("The graph is PLANAR (Conflict graph is bipartite).")
        else:
            print("The graph is NON-PLANAR (Conflict graph is not bipartite).")
            
    except ValueError:
        print("Invalid input. Please enter a valid integer for the number of edges.")

if __name__ == "__main__":
    main()