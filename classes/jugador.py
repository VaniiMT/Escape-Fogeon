import time
import random

STAMINA_REGEN_RATE = 2
FALL_COOLDOWN = 15
FALL_DAMAGE = 10

class Jugador:
    def __init__(self, graph, start_node):
        self.graph = graph
        self.position = start_node
        self.stamina = 150
        self.max_stamina = 150
        self.visited = {start_node}
        self.keys_collected = []
        self.restore_nodes_used = []
        self.last_fall_time = time.time()
        self.last_regen = time.time()
        self.keys_required = 3
    
    def mover(self, new_pos):
        if new_pos not in self.graph.get_neighbors(self.position):
            return False
        costo = 0 if new_pos in self.visited else self.graph.get_edge_weight(self.position, new_pos)
        if self.stamina >= costo:
            self.stamina -= costo
            self.position = new_pos
            self.visited.add(new_pos)
            return True
        return False
    
    def regenerar(self):
        diff = time.time() - self.last_regen
        if diff >= 0.1:
            self.stamina = min(self.max_stamina, self.stamina + STAMINA_REGEN_RATE)
            self.last_regen = time.time()
    
    def check_key_nodes(self, key_nodes):
        if self.position in key_nodes and self.position not in self.keys_collected:
            self.keys_collected.append(self.position)
            return True
        return False
    
    def check_restore_nodes(self, restore_nodes):
        if self.position in restore_nodes and self.position not in self.restore_nodes_used:
            self.stamina = self.max_stamina
            self.restore_nodes_used.append(self.position)
            return True
        return False
    
    def fall_event(self):
        if time.time() - self.last_fall_time >= FALL_COOLDOWN and random.random() < 0.15:
            self.max_stamina -= FALL_DAMAGE
            self.stamina = min(self.stamina, self.max_stamina)
            self.last_fall_time = time.time()
            return True
        return False
    
    def can_escape(self):
        return len(self.keys_collected) == self.keys_required