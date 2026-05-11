import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time
import os
import imageio
import networkx as nx

from .grafo import GrafoMazmorra
from .jugador import Jugador
from .monstruo import Monstruo, MONSTER_SPAWN_DELAY

NODE_RADIUS = 0.06
KEY_NODE_COUNT = 3

class Juego:
    def __init__(self, video_path=None):
        self.root = tk.Tk()
        self.root.title("ESCAPE DE LA MAZMORRA")
        
        self.video_path = video_path or r"C:\Users\imeso\OneDrive\Desktop\FiveNightsAtFreddy's-FoxyJumpscare(Green.mp4"
        
        self.ui()
        self.state_game()
        self.root.mainloop()
    
    def ui(self):
        main_frame = tk.Frame(self.root, bg='#0a0a2a')
        main_frame.pack()
        
        #Mapa
        self.frame_mapa = tk.Frame(main_frame, bg='#0a0a2a')
        self.frame_mapa.pack(side=tk.LEFT)
        
        self.fig = plt.Figure(figsize=(10, 8), facecolor='#1a1a2e')
        self.canvas = FigureCanvasTkAgg(self.fig, self.frame_mapa)
        self.canvas.get_tk_widget().pack()
        self.ax = self.fig.add_subplot()
        
        # Controles
        self.frame_controls = tk.Frame(main_frame, width=350, bg='#0a0a2a') 
        self.frame_controls.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0)) 
        
        
        self.create_controls()
        self.create_stats()
    
    def create_controls(self):
        frame_mov = tk.Frame(self.frame_controls, bg='#0a0a2a')
        frame_mov.pack(pady=20)
        
        buttons = [ ("↑", 0, 1, "up"), ("←", 1, 0, "left"), ("↓", 1, 1, "down"), ("→", 1, 2, "right")]
        for text, row, col, cmd in buttons:
            tk.Button(frame_mov, text=text, width=10, height=4, command=lambda d=cmd: self.mover(d), bg='#00FF44').grid(row=row, column=col, padx=5, pady=5)
        
        #Reiniciar y salir
        tk.Button(self.frame_controls, text="REINICIAR", command=self.reiniciar, bg='#FF6600', fg='white', width=15).pack(pady=10)
        tk.Button(self.frame_controls, text="SALIR", command=self.salir, bg='#FF0000', fg='white', width=15).pack(pady=10)
        
        instrucciones = """INSTRUCCIONES:
• Nodos muestran COSTO de stamina
• Nodos verdes = ya visitados (costo 0)
• Recolecta 3 LLAVES doradas
• Nodos MORADOS restauran stamina
• El MONSTRUO usa DIJKSTRA
• Llega a la SALIDA azul"""
        tk.Label(self.frame_controls, text=instrucciones, font=("Arial", 10), bg='#0a0a2a', fg='#88ccff', justify=tk.LEFT).pack(pady=20)
        
    def reiniciar(self):
        self.init_game()
    
    def salir(self):
        self.root.quit()
        self.root.destroy()
    
    def create_stats(self):
        self.stats_frame = tk.Frame(self.frame_controls, bg='#0a0a2a')
        self.stats_frame.pack(fill=tk.BOTH, expand=True)
        
        self.stats = {}
        labels = ["Posicion:", "Stamina:", "Llaves:", "Monstruo:", "Max Stamina:"]
        for i, label in enumerate(labels):
            tk.Label(self.stats_frame, text=label, font=("Arial", 11, "bold"),
                    bg='#0a0a2a', fg="white").grid(row=i, column=0, sticky="w", pady=5, padx=10)
            self.stats[label] = tk.Label(self.stats_frame, text='-', font=("Arial", 11),
                                         bg='#0a0a2a', fg='#88ccff')
            self.stats[label].grid(row=i, column=1, sticky="w", pady=5, padx=10)
    
    def state_game(self):
        self.mazmorra = GrafoMazmorra()
        self.jugador = Jugador(self.mazmorra, self.mazmorra.start_node)
        self.monstruo = Monstruo(self.mazmorra, self.mazmorra.start_node, self.jugador)
        self.game_over = False
        self.monstruo_activo = False
        self.tiempo_inicio = time.time()
        self.dibujar_mapa()
        self.actualizar_juego()
    
    def actualizar_stats(self):
        self.stats["Posicion:"].config(text=f"Nodo {self.jugador.position}")
        self.stats["Stamina:"].config(text=f"{int(self.jugador.stamina)}/{self.jugador.max_stamina}")
        self.stats["Llaves:"].config(text=f"{len(self.jugador.keys_collected)}/{KEY_NODE_COUNT}")
        self.stats["Max Stamina:"].config(text=f"{self.jugador.max_stamina}")
        
        if self.monstruo.active:
            try:
                dist = nx.dijkstra_path_length(self.mazmorra.graph, self.jugador.position, self.monstruo.position, weight='weight')
                if dist < 30: estado = "PELIGROSO"
                else: estado = "SEGURO"
                self.stats["Monstruo:"].config(text=f"{int(dist)} - {estado}")
            except:
                self.stats["Monstruo:"].config(text="ACTIVO")
        else:
            restante = max(0, MONSTER_SPAWN_DELAY - (time.time() - self.tiempo_inicio))
            self.stats["Monstruo:"].config(text=f"Aparece en {restante}s")
    
    def mover(self, direccion):
        if self.game_over:
            return
        
        actual = self.mazmorra.positions[self.jugador.position]
        vecinos = self.mazmorra.get_neighbors(self.jugador.position)
        #Buscar el vecino más cercano en la dirección deseada
        mejor_vecino = None
        mejor_distancia = float('inf')
        
        for v in vecinos:
            x, y = self.mazmorra.positions[v]
            dx = x - actual[0]
            dy = y - actual[1]
            
            if direccion == "left" and dx < 0:
                distancia = abs(dx)
            elif direccion == "right" and dx > 0:
                distancia = abs(dx)
            elif direccion == "up" and dy > 0:
                distancia = abs(dy)
            elif direccion == "down" and dy < 0:
                distancia = abs(dy)
            else:
                continue
            #Elegir el vecino más cercano en esa dirección
            if distancia < mejor_distancia:
                mejor_distancia = distancia
                mejor_vecino = v
        
        if mejor_vecino and self.jugador.mover(mejor_vecino):
            self.dibujar_mapa()
    
    def nodos_visibles(self):
        actual = self.jugador.position
        visibles = set(self.mazmorra.get_neighbors(actual))
        visibles.add(actual)
        if self.monstruo.active:
            visibles.add(self.monstruo.position)
        for key in self.mazmorra.key_nodes:
            if key in self.jugador.visited:
                visibles.add(key)
        for restore in self.mazmorra.restore_nodes:
            if restore in self.jugador.visited:
                visibles.add(restore)
        
        aristas = []
        for u in visibles:
            for v in self.mazmorra.get_neighbors(u):
                if v in visibles and (u, v) not in aristas and (v, u) not in aristas:
                    aristas.append((u, v))
        return list(visibles), aristas
    
    def dibujar_mapa(self):
        if self.game_over:
            return
        
        self.ax.clear()
        self.ax.set_xlim(0, 1)
        self.ax.set_ylim(0, 1)
        self.ax.axis("off")
        
        visibles, aristas = self.nodos_visibles()
        
        #Dibujar conexiones 
        for u, v in aristas:
            x1, y1 = self.mazmorra.positions[u]
            x2, y2 = self.mazmorra.positions[v]
            self.ax.plot([x1, x2], [y1, y2], "white", linewidth=1)
        
        #Dibujar nodo
        for nodo in visibles:
            x, y = self.mazmorra.positions[nodo]
            
            # Determinar color del nodo
            if nodo == self.jugador.position:
                color, tam, borde = "#00ff00", NODE_RADIUS * 1.6, '#00ff00'  
            elif self.monstruo.active and nodo == self.monstruo.position:
                color, tam, borde = "#ff0000", NODE_RADIUS * 1.3, '#8b0000'  
            elif nodo == self.mazmorra.exit_node:
                color, tam, borde = "#00ffff", NODE_RADIUS * 1.2, '#0066cc'  
            elif nodo in self.mazmorra.key_nodes:
                if nodo in self.jugador.keys_collected:
                    color, tam, borde = "#ffa500", NODE_RADIUS * 1.2, '#b8860b' 
                else:
                    color, tam, borde = "#ffff00", NODE_RADIUS * 1.2, '#b8860b' 
            elif nodo in self.mazmorra.restore_nodes:
                if nodo in self.jugador.restore_nodes_used:
                    color, tam, borde = "#800080", NODE_RADIUS * 1.2, '#cc00cc'  
                else:
                    color, tam, borde = "#ff00ff", NODE_RADIUS * 1.2, '#cc00cc'  
            elif nodo in self.jugador.visited:
                color, tam, borde = "#808080", NODE_RADIUS, '#555555'  
            else:
                color, tam, borde = "#0000ff", NODE_RADIUS, '#2a6ea5'  
            
            # Dibujar círculo
            circle = plt.Circle((x, y), tam, color=color, ec=borde, linewidth=2, zorder=2)
            self.ax.add_patch(circle)
            
            # Mostrar costo o marca de visitado
            es_vecino = nodo in self.mazmorra.get_neighbors(self.jugador.position)
            if es_vecino and nodo not in self.jugador.visited:
                costo = self.mazmorra.get_edge_weight(self.jugador.position, nodo)
                self.ax.text(x, y, str(costo), fontsize=7, ha="center", va="center", 
                            fontweight="bold", color="white")
            elif nodo in self.jugador.visited and nodo != self.jugador.position:
                self.ax.text(x, y, "✓", fontsize=10, ha="center", va="center", 
                            fontweight="bold", color="#00ff00")
            
            # Anillo amarillo alrededor del jugador
            if nodo == self.jugador.position:
                anillo = plt.Circle((x, y), tam * 1.4, color='#ffff00', 
                                fill=False, linewidth=3, zorder=3)
                self.ax.add_patch(anillo)
        
        self.canvas.draw()
        self.actualizar_stats()
    
    def reproducir_video(self):
        if os.path.exists(self.video_path):
            try:
                reader = imageio.get_reader(self.video_path, "ffmpeg")
                for frame in reader:
                    self.ax.clear()
                    self.ax.axis('off')
                    self.ax.imshow(frame)
                    self.canvas.draw()
                    self.canvas.get_tk_widget().update()
                    time.sleep(1/30)
                reader.close()
            except Exception as e:
                print(f"Error al reproducir video: {e}")
    
    def actualizar_juego(self):
        if not self.game_over:
            self.jugador.regenerar()
            self.monstruo.regenerar()
            
            self.jugador.fall_event()
            self.jugador.check_restore_nodes(self.mazmorra.restore_nodes)
            self.jugador.check_key_nodes(self.mazmorra.key_nodes)
            
            if not self.monstruo_activo and time.time() - self.tiempo_inicio >= MONSTER_SPAWN_DELAY:
                self.monstruo.activar()
                self.monstruo_activo = True
                print("El monstruo ha aparecido!")
            
            if self.monstruo.active:
                self.monstruo.mover()
                if self.monstruo.atrapo():
                    self.game_over = True
                    print("El monstruo te atrapo!")
                    self.reproducir_video()
            
            if self.jugador.position == self.mazmorra.exit_node and self.jugador.can_escape():
                self.game_over = True
                print("VICTORIA!")
                self.ax.text(0.5, 0.5, "VICTORIA!", fontsize=60, ha="center", va="center", color="green", transform=self.ax.transAxes)
                self.canvas.draw()
                time.sleep(3)
            self.dibujar_mapa()
        
        self.root.after(100, self.actualizar_juego)