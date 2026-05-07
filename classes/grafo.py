import networkx as nx
import random

MIN_WEIGHT = 3
MAX_WEIGHT = 12
NODE_COUNT = 100
GRID_SIZE = 10

class GrafoMazmorra:
    def __init__(self):
        self.num_nodes = NODE_COUNT
        self.grid_size = GRID_SIZE
        self.graph = nx.Graph()
        self.positions = {}
        self.key_nodes = []
        self.restore_nodes = []
        self.start_node = 0
        self.exit_node = None
        self.generate_dungeon()
    
    def generate_dungeon(self):
        for i in range(self.num_nodes):
            row, col = i // self.grid_size, i % self.grid_size
            x = 0.05 + (col / (self.grid_size - 1)) * 0.9
            y = 0.95 - (row / (self.grid_size - 1)) * 0.9
            self.positions[i] = (x, y)
        
        edges = []
        for i in range(self.num_nodes):
            row, col = i // self.grid_size, i % self.grid_size
            if col < self.grid_size - 1:
                edges.append((i, i + 1, random.randint(MIN_WEIGHT, MAX_WEIGHT)))
            if row < self.grid_size - 1:
                edges.append((i, i + self.grid_size, random.randint(MIN_WEIGHT, MAX_WEIGHT)))
        
        self.graph.add_weighted_edges_from(edges)
        
        available = list(range(1, self.num_nodes))
        self.key_nodes = random.sample(available, 3)
        remaining = [n for n in available if n not in self.key_nodes]
        self.restore_nodes = random.sample(remaining, min(2, len(remaining)))
        exit_candidates = [n for n in remaining if n not in self.restore_nodes]
        self.exit_node = random.choice(exit_candidates)
    
    def get_neighbors(self, node): 
        return list(self.graph.neighbors(node))
    
    def get_edge_weight(self, u, v): 
        return self.graph[u][v]["weight"]