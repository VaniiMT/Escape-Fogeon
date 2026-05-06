import time
import networkx as nx

MONSTER_MOVE_DELAY = 1.2
MONSTER_SPAWN_DELAY = 12

class Monstruo:
    def __init__(self, graph, start_node, player):
        self.graph = graph
        self.position = start_node
        self.stamina = 100
        self.player = player
        self.last_move = time.time()
        self.last_regen = time.time()
        self.active = False
    
    def activar(self):
        self.active = True
    
    def camino_dijkstra(self):
        if not self.active:
            return []
        try:
            return nx.dijkstra_path(self.graph.graph, self.position, self.player.position, weight='weight')[1:]
        except:
            return []
    
    def mover(self):
        if not self.active or time.time() - self.last_move < MONSTER_MOVE_DELAY:
            return
        path = self.camino_dijkstra()
        if path:
            target = path[0]
            costo = self.graph.get_edge_weight(self.position, target)
            if self.stamina >= costo:
                self.stamina -= costo
                self.position = target
                self.last_move = time.time()
    
    def regenerar(self):
        if not self.active:
            return
        diff = time.time() - self.last_regen
        if diff >= 0.1:
            self.stamina = min(100, self.stamina + 1 * diff)
            self.last_regen = time.time()
    
    def atrapo(self):
        return self.active and self.position == self.player.position