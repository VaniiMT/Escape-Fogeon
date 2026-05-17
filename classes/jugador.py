import time      
import random    

# Constantes del juego
STAMINA_REGEN_RATE = 2     
FALL_COOLDOWN = 15          
FALL_DAMAGE = 10           

class Jugador:
    """Clase que representa al jugador en la mazmorra"""
    
    def __init__(self, graph, start_node):
        """Constructor: inicializa al jugador en el nodo de inicio"""
        self.graph = graph                     
        self.position = start_node              
        self.stamina = 150                      
        self.max_stamina = 150                  
        self.visited = {start_node}             # Conjunto de nodos ya visitados (set para evitar duplicados)
        self.keys_collected = []                #Lista de llaves que ha recolectado el jugador
        self.restore_nodes_used = []            #Lista de nodos de restauración ya usados
        self.last_fall_time = time.time()       #Marca de tiempo del último evento de caída
        self.last_regen = time.time()           #Marca de tiempo de la última regeneración
        self.keys_required = 3                  #Nº de llaves necesarias para escapar
    
    def mover(self, new_pos):
        """Intenta mover al jugador a una nueva posición.
        Retorna True si el movimiento fue exitoso, False en caso contrario."""
        #Verifica si es un nodo vecino al actual
        if new_pos not in self.graph.get_neighbors(self.position):
            return False
        
        #Calcula el costo: 0 si ya visitó el nodo, sino usa el peso del grafo
        costo = 0 if new_pos in self.visited else self.graph.get_edge_weight(self.position, new_pos)
        
        #Verifica si tiene suficiente stamina para pagar el costo
        if self.stamina >= costo:
            self.stamina -= costo               #Reduce la stamina según el costo
            self.position = new_pos             #Actualiza la posición
            self.visited.add(new_pos)           #Marca el nodo como visitado
            return True                       
        
        return False                           
    
    def regenerar(self):
        """Regenera stamina con el tiempo.
        Debe llamarse frecuentemente (ej: cada frame o cada iteración del juego)"""
        #Calcula cuánto tiempo ha pasado desde la última regeneración
        diff = time.time() - self.last_regen
        
        #Si pasó al menos X segundos, regenera stamina
        if diff >= 0.1:
            #Incrementa stamina sin superar el máximo
            self.stamina = min(self.max_stamina, self.stamina + STAMINA_REGEN_RATE)
            self.last_regen = time.time()       # Actualiza la marca de tiempo
    
    def check_key_nodes(self, key_nodes):
        """Verifica si el jugador está en un nodo que contiene una llave no recolectada.
        Retorna True si recolectó una llave, False en caso contrario."""
        #Si la posición actual está en la lista de nodos con llaves y no fue recolectada
        if self.position in key_nodes and self.position not in self.keys_collected:
            self.keys_collected.append(self.position)  #Agrega la llave a la colección
            return True                               
        
        return False                                   
    
    def check_restore_nodes(self, restore_nodes):
        """Verifica si el jugador está en un nodo de restauración no usado.
        Retorna True si se restauró la stamina, False en caso contrario. """
        #Si la posición actual es un nodo de restauración y no ha sido usado
        if self.position in restore_nodes and self.position not in self.restore_nodes_used:
            self.stamina = self.max_stamina             #Restaura la stamina al máximo
            self.restore_nodes_used.append(self.position)  #Marca el nodo como usado
            return True                                 
        
        return False                                  
    
    def fall_event(self):
        """Simula un evento de caída aleatoria con cooldown.
        Retorna True si ocurrió una caída, False en caso contrario."""
        #Verifica si pasó suficiente tiempo desde la última caída Y si hay 15% de probabilidad
        if time.time() - self.last_fall_time >= FALL_COOLDOWN and random.random() < 0.15:
            self.max_stamina -= FALL_DAMAGE            #Reduce la stamina máxima permanentemente
            self.stamina = min(self.stamina, self.max_stamina)  #Ajusta stamina actual si es mayor
            self.last_fall_time = time.time()          #Actualiza el tiempo de la última caída
            return True                                
        
        return False                                 
    
    def can_escape(self):
        """Verifica si el jugador tiene todas las llaves necesarias para escapar.
        Retorna True si puede escapar, False en caso contrario."""
        #Compara la cantidad de llaves recolectadas con las requeridas
        return len(self.keys_collected) == self.keys_required