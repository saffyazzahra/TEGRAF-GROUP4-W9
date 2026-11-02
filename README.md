# Informatics ITS Graph Theory class Group 4
|Name|NRP|
|---|---|
|Naura Rizky Ameira|5025251001|
|Farras Al-Ghifari|5025251006|
|Nisrina Zahralilla|5025251013|
|Safiya Nadira Az-zahra|5025251268|

## Left-Right de Fraysseix–Rosenstiehl Criterion 

- ### BRIEF ALGORITHM EXPLANATION

The algorithm uses the Left-Right planarity test of Brandes, which is built on the de Fraysseix-Rosenstiehl criterion. The idea is to walk through the graph with a DFS, which creates a tree, and then look at the leftover edges that jump back up to an earlier node (back edges). If the graph is planar, every back edge can be drawn either to the left or to the right of the tree without crossing another one. Before starting, the code removes self-loops and duplicate edges. It also rejects any graph with more than 3n-6 edges (Eulers formula), because a planar graph can never have that many.

The algorithm runs the DFS twice. The first pass measures how far up the tree each edge can reach, and uses that to put the edges in an order where small inner loops are handled before the bigger loops around them. The second pass goes through the edges in that order and keeps a stack of “these edges must be on opposite sides” rules. Whenever two back edges would cross, the rule forces them onto different sides. If some edge ends up forced onto both sides at once, there is no way to avoid a crossing, so the graph is non-planar. If every edge gets a side without a contradiction, the graph is planar.

- ### RUNNING THE CODE

  - Input the number of edges in the desired graph
  - Input the adjacency list of each edge
 
- ### SAMPLE INPUTS

  - Planar Graph
    
   Edges: `8`

    ```    
    Edge 1: 0 1
    Edge 2: 1 2
    Edge 3: 2 3
    Edge 4: 3 4
    Edge 5: 4 5
    Edge 6: 0 3
    Edge 7: 1 4
    Edge 8: 2 5
    ```

  RESULT:
    ```
    The graph is PLANAR (left-right constraints are consistent).
    ```

  - Non-planar Graph
      
    Edges: `10`

    ```    
    Edge 1: 0 1
    Edge 2: 0 2
    Edge 3: 0 3
    Edge 4: 0 5
    Edge 5: 1 2
    Edge 6: 1 3
    Edge 7: 1 5
    Edge 8: 2 4
    Edge 9: 3 4
    Edge 10: 4 5
    ```

  RESULT:
    ```
    The graph is NON-PLANAR (left-right constraints conflict).
    ```


## Shih-Hsu Algorithm

- ### BRIEF ALGORITHM EXPLANATION

The Shih–Hsu (SH) algorithm determines whether a graph is planar by checking whether it can be drawn without crossing edges. First, the graph is divided into biconnected components (blocks), and each block is processed separately using Depth-First Search (DFS). The DFS identifies the tree edges and back edges, which connect a vertex to one of its ancestors.

Next, the algorithm builds a PC-tree to manage the possible arrangements of edges. It consists of P-nodes (freely arranged branches), C-nodes (branches with a fixed circular order), and L-leaves (representing back edges). The vertices are then processed in reverse DFS order, starting from the children and moving toward the root.

At each vertex, the back edges ending at that vertex must be arranged consecutively in the PC-tree. If this arrangement is impossible, the graph is non-planar. Otherwise, the corresponding nodes are merged into a C-node, and the process continues. If all vertices are processed successfully, the graph is planar.

- ### RUNNING THE CODE

  - Input the number of edges in the desired graph
  - Input the adjacency list of each edge

- ### SAMPLE INPUTS

- Planar Graph
    
    Edges: `6`
    ```
    Edge 1: 0 1
    Edge 2: 0 2
    Edge 3: 0 3
    Edge 4: 1 2
    Edge 5: 1 3
    Edge 6: 2 3
    ```

    RESULT:
    ```
    Graph with 4 vertices and 6 edges is PLANAR.
    ```

  - Non-planar Graph
      
    Edges: `9`

    ```    
    Edge 1: 0 3
    Edge 2: 0 4
    Edge 3: 0 5
    Edge 4: 1 3
    Edge 5: 1 4
    Edge 6: 1 5
    Edge 7: 2 3
    Edge 8: 2 4
    Edge 9: 2 5
    ```

    RESULT:
    ```
    Graph with 6 vertices and 9 edges is NON-PLANAR.
    ```

## AI USAGE DISCLOSURE

- de Fraysseix–Rosenstiehl Criterion : https://share.gemini.google/r6mbxHnmqEIj
- Shih-Hsu Algorithm : https://claude.ai/share/30b20437-9705-493e-bba9-1dc1ced0db21
