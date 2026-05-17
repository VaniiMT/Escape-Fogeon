import networkx as nx
import random          

# Constantes que definen la configuración de la mazmorra
MIN_WEIGHT = 3         
MAX_WEIGHT = 12        
NODE_COUNT = 100   
GRID_SIZE = 10      

class GrafoMazmorra:
    """Clase que representa una mazmorra como un grafo donde cada nodo es una habitación"""
    
    def __init__(self):
        """Constructor: inicializa la mazmorra y la genera automáticamente"""
        self.num_nodes = NODE_COUNT                    
        self.grid_size = GRID_SIZE                     
        self.graph = nx.Graph()                       
        self.positions = {}                            #Diccionario para coordenadas (x,y) de cada nodo
        self.key_nodes = []                            #Lista llaves (3 nodos)
        self.restore_nodes = []                        #Lista X (2 nodos)
        self.start_node = 0                           
        self.exit_node = None                          
        self.generate_dungeon()                   
    
    def generate_dungeon(self):
        """Genera la estructura completa de la mazmorra"""
        
        # PASO 1: Asignar coordenadas a cada nodo (disposición visual)
        for i in range(self.num_nodes):                # Itera sobre cada habitación (0 a 99)
            row, col = i // self.grid_size, i % self.grid_size  # Calcula fila y columna en cuadrícula 10x10
            # Calcula posición x (horizontal): de 0.05 a 0.95 del ancho
            x = 0.05 + (col / (self.grid_size - 1)) * 0.9
            # Calcula posición y (vertical): de 0.05 a 0.95 del alto (invertido)
            y = 0.95 - (row / (self.grid_size - 1)) * 0.9
            self.positions[i] = (x, y)                 # Guarda la coordenada (x,y) para el nodo i
        
        # PASO 2: Crear conexiones entre habitaciones vecinas
        edges = []                                      #almacenar las conexiones
        for i in range(self.num_nodes):             
            row, col = i // self.grid_size, i % self.grid_size  #Obtiene posición en cuadrícula
            #Columna
            if col < self.grid_size - 1:
                edges.append((i, i + 1, random.randint(MIN_WEIGHT, MAX_WEIGHT))) #Agrega conexión con peso aleatorio entre MIN y MAX
            #Fila
            if row < self.grid_size - 1:
                edges.append((i, i + self.grid_size, random.randint(MIN_WEIGHT, MAX_WEIGHT)))
        self.graph.add_weighted_edges_from(edges)
        
        available = list(range(1, self.num_nodes))     #Lista de nodos disponibles (excluyendo el 0)
        
        #Selecciona 3 nodos aleatorios para las llaves
        self.key_nodes = random.sample(available, 3)
        
        #Nodos restantes
        remaining = [n for n in available if n not in self.key_nodes]
        
        #Selecciona 2 nodos aleatorios para restauración
        self.restore_nodes = random.sample(remaining, min(2, len(remaining)))
        
        #Candidatos para salida
        exit_candidates = [n for n in remaining if n not in self.restore_nodes]
        
        #Selecciona un nodo aleatorio como salida
        self.exit_node = random.choice(exit_candidates)
    
    def get_neighbors(self, node):
        """Devuelve la lista de habitaciones vecinas a la habitación dada"""
        return list(self.graph.neighbors(node))        #Convierte el iterador de vecinos a lista
    
    def get_edge_weight(self, u, v):
        """Devuelve el peso (costo/dificultad) de la conexión entre dos habitaciones"""
        return self.graph[u][v]['weight']