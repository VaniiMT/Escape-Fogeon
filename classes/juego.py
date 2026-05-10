import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time
import networkx as nx
#For video
import os
import imageio

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
                    bg='#0a0a2a', fg='white').grid(row=i, column=0, sticky="w", pady=5, padx=10)
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