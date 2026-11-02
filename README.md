# Informatics ITS Graph Theory class Group 4
|Name|NRP|
|---|---|
|Naura Rizky Ameira|5025251001|
|Farras Al-Ghifari|5025251006|
|Nisrina Zahralilla|5025251013|
|Safiya Nadira Az-zahra|5025251268|

## de Fraysseix–Rosenstiehl Criterion 

- ## BRIEF ALGORITHM EXPLANATION

The de Fraysseix (DFR) algorithm determines if a graph can be drawn without any crossing lines by organizing it into a Depth-First Search (DFS) tree. It separates the connections into main tree pathways and loop-like back-edges, seeing whether these loops can be neatly sorted into two opposing sides without crossing.

To solve this, the algorithm builds a "conflict graph" where each loop becomes a node, and connections are drawn between any loops that overlap or conflict with each other. If this conflict graph can be cleanly split into two separate groups, then a valid layout exists and the graph is planar; otherwise, it's non-planar.

- ## RUNNING THE CODE

  - Input the number of edges in the desired graph
  - Input the adjacency list of each edge
 
- ## SAMPLE INPUTS

  - Planar Graph
    
    Edges: 6
  
    Edge 1: 0 1
    Edge 2: 0 2
    Edge 3: 0 3
    Edge 4: 1 2
    Edge 5: 1 3
    Edge 6: 2 3

    RESULT:
    ```
    The graph is PLANAR (Conflict graph is bipartite).
    ```

  - Non-planar Graph
      
    Edges: 9
    
    Edge 1: 0 3
    Edge 2: 0 4
    Edge 3: 0 5
    Edge 4: 1 3
    Edge 5: 1 4
    Edge 6: 1 5
    Edge 7: 2 3
    Edge 8: 2 4
    Edge 9: 2 5

    RESULT:
    ```
     The graph is NON-PLANAR (Conflict graph is not bipartite).
    ```


## Shih-Hsu Algorithm

- ## BRIEF ALGORITHM EXPLANATION

- ## RUNNING THE CODE

- ## SAMPLE INPUTS

## AI USAGE DISCLOSURE

- de Fraysseix–Rosenstiehl Criterion : https://share.gemini.google/r6mbxHnmqEIj
- Shih-Hsu Algorithm : 
