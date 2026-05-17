import time                   
import networkx as nx          

#Constantes de tiempo para el monstruo
MONSTER_MOVE_DELAY = 1.2       
MONSTER_SPAWN_DELAY = 12      

class Monstruo:
    def __init__(self, graph, start_node, player):
        self.graph = graph                    
        self.position = start_node          
        self.stamina = 100                   
        self.player = player                  #Referencia al objeto del jugador
        self.last_move = time.time()          
        self.last_regen = time.time()        
        self.active = False                   
    
    def activar(self):
        """Activa al monstruo después de cierto tiempo"""
        self.active = True                  
    
    def camino_dijkstra(self):
        if not self.active:
            return []
        
        origen = self.position
        destino = self.player.position #Nodo donde está el jugador
        
        dist = {nodo: float('inf') for nodo in range(100)} #Guardará la distancia mínima conocida entre los nodos
        
        #La distancia del origen hacia sí mismo es 0 (estamos parados ahí)
        dist[origen] = 0
        prev = {} #Guarda cuál fue el nodo anterior en el camino más corto
        visitados = set() #Guarda los nodos que ya visitamos. Sabemos distancia definitiva para estos.
    
        #Mientras no hayamos visitado todos los nodos (máximo 100 iteraciones)
        while len(visitados) < 100:
            
            #1. Encontrar el nodo NO visitado con MENOR distancia
            actual = None  #Empezamos sin nodo seleccionado
            
            #Revisamos TODOS los nodos del 0 al 99
            for nodo in range(100):
                if nodo not in visitados: 
                    '''Si es el primer nodo no visitado que vemos, o si tiene
                    #menor distancia que el que teníamos guardado, lo elegimos'''
                    if actual is None or dist[nodo] < dist[actual]:
                        actual = nodo
            
            #3.   Procesar el nodo actual
            #Marcar este nodo como visitado
            visitados.add(actual)
            
            #4 Relajar los vecinos (actualizar distancias) -----
            #Revisamos todos los vecinos del nodo actual
            for vecino in self.graph.get_neighbors(actual):
                if vecino in visitados: #Si el vecino ya fue visitado, su distancia ya es definitiva, lo saltamos
                    continue
                
                #Obtenemos el peso de arista al vecino
                peso = self.graph.get_edge_weight(actual, vecino)
                
                '''Calculamos la nueva distancia: lo que nos costó llegar a actual
                más lo que cuesta al vecino'''
                nueva_dist = dist[actual] + peso
                
                '''Si esta nueva distancia es MEJOR que la que tenía
                guardada anteriormente, la actualizamos'''
                if nueva_dist < dist[vecino]:
                    dist[vecino] = nueva_dist      # Guardamos la nueva distancia
                    prev[vecino] = actual         
        
        #Reconstruimos el camino desde el destino hacia atrás hasta el origen
        camino = [destino]    #Empezamos con una lista que solo contiene el destino
        
        # Mientras el último nodo de la lista NO sea el origen
        while camino[-1] != origen:
            '''Buscamos en "prev" cuál es el nodo anterior a ese último nodo
               Y lo agregamos al final de la lista'''
            '''Ejemplo: si camino = [4] y prev[4] = 1, ahora camino = [4, 1]'''
            camino.append(prev[camino[-1]])
        
        #Ahora 'camino' está al revés: destino, ..., origen
        '''Ejemplo: [4, 2, 1, 0] cuando queremos [0, 1, 2, 4]'''
        camino.reverse()
        
        '''Devolvemos el camino desde la posición 1 (omitimos el origen porque
        el monstruo ya está ahí, no necesita moverse a donde ya está)'''
        #Si el camino solo tiene el origen (len=1), devolvemos lista vacía
        return camino[1:] if len(camino) > 1 else []
    
    def mover(self):
        """Mueve al monstruo un paso hacia el jugador si es posible.
        Solo se mueve si:
        1. Está activo
        2. Pasó suficiente tiempo desde el último movimiento
        3. Tiene suficiente stamina """
        # Verificar si puede moverse (activo y tiempo de espera cumplido)
        if not self.active or time.time() - self.last_move < MONSTER_MOVE_DELAY:
            return
        #Obtener el siguiente nodo en el camino hacia el jugador
        path = self.camino_dijkstra()
        
        if path:                             
            target = path[0]                   #Primer nodo a mover (el más cercano)
            #Calcular costo de moverse a ese nodo
            costo = self.graph.get_edge_weight(self.position, target)
            
            #Si tiene suficiente stamina para moverse
            if self.stamina >= costo:
                self.stamina -= costo          #Gasta stamina
                self.position = target         #Actualiza posición
                self.last_move = time.time()   #Actualiza tiempo del último movimiento
    
    def regenerar(self):
        """Regenera stamina del monstruo con el tiempo"""
        if not self.active:                  
            return
        #Calcular tiempo transcurrido desde la última regeneración
        diff = time.time() - self.last_regen
        #Si pasó al menos 0.1 segundos
        if diff >= 0.1:
            self.stamina = min(100, self.stamina + 1 * diff)
            self.last_regen = time.time()      #
    def atrapo(self):
        return self.active and self.position == self.player.position