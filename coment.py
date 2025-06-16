# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import messagebox
import random
import threading
import time

# ###########################################################################
# #                                                                         #
# #        PESSOA 1: ESTRUTURA DO TABULEIRO E CONSTANTES INICIAIS             #
# #                                                                         #
# ###########################################################################
#
# Explicação: Esta seção define todas as constantes e estruturas de dados
# que servem como o "mapa" do nosso jogo. Elas traduzem a lógica abstrata
# do jogo (como "avançar 5 casas") para coordenadas visuais na tela.
# É a base para desenhar o tabuleiro e mover as peças corretamente.

# --- Constantes Globais de Configuração ---
COLORS = ["red", "green", "yellow", "blue"]  # Cores dos jogadores
SQUARE_SIZE = 40  # Tamanho de cada quadrado do tabuleiro em pixels
BOARD_GRID_SIZE = 15  # O tabuleiro é uma grade de 15x15 quadrados

# --- Mapeamento do Caminho Principal ---
# Dicionário que converte a posição lógica no caminho (0 a 51) para uma
# coordenada visual (coluna, linha) na grade do tabuleiro.
MAIN_PATH_VISUAL_MAP = {
    0: (6, 1), 1: (6, 2), 2: (6, 3), 3: (6, 4), 4: (6, 5),
    5: (5, 6), 6: (4, 6), 7: (3, 6), 8: (2, 6), 9: (1, 6),
    10: (0, 6), 11: (0, 7), 12: (0, 8), 13: (1, 8), 14: (2, 8),
    15: (3, 8), 16: (4, 8), 17: (5, 8), 18: (6, 9), 19: (6, 10),
    20: (6, 11), 21: (6, 12), 22: (6, 13), 23: (6, 14), 24: (7, 14),
    25: (8, 14), 26: (8, 13), 27: (8, 12), 28: (8, 11), 29: (8, 10),
    30: (8, 9), 31: (9, 8), 32: (10, 8), 33: (11, 8), 34: (12, 8),
    35: (13, 8), 36: (14, 8), 37: (14, 7), 38: (14, 6), 39: (13, 6),
    40: (12, 6), 41: (11, 6), 42: (10, 6), 43: (9, 6), 44: (8, 5),
    45: (8, 4), 46: (8, 3), 47: (8, 2), 48: (8, 1), 49: (8, 0),
    50: (7, 0), 51: (6, 0)
}

# Define o índice do caminho principal onde cada cor inicia seu percurso.
START_PATH_INDEX = {
    "red": 48, "green": 9, "yellow": 22, "blue": 35,
}

# --- Mapeamento das Retas Finais ---
# Dicionário que define as coordenadas visuais para a reta final de cada cor.
HOME_STRETCH_VISUAL_MAP = {
    "red": [(7, 1), (7, 2), (7, 3), (7, 4), (7, 5), (7, 6)],
    "green": [(1, 7), (2, 7), (3, 7), (4, 7), (5, 7), (6, 7)],
    "yellow": [(7, 13), (7, 12), (7, 11), (7, 10), (7, 9), (7, 8)],
    "blue": [(13, 7), (12, 7), (11, 7), (10, 7), (9, 7), (8, 7)],
}

# Define a última casa do caminho principal antes de um peão entrar em sua reta final.
# Isso é usado para saber quando fazer a "curva" para casa.
LAST_MAIN_SQUARE_BEFORE_HOME = {
    "red": 47,
    "green": 8,
    "yellow": 21,
    "blue": 34
}

# --- Casas Seguras (Safe Zones) ---
# Lista de coordenadas visuais que são consideradas seguras (estrelas),
# onde um peão não pode ser capturado.
SAFE_SQUARES_COORDS = [
    MAIN_PATH_VISUAL_MAP[START_PATH_INDEX["red"]],
    MAIN_PATH_VISUAL_MAP[START_PATH_INDEX["green"]],
    MAIN_PATH_VISUAL_MAP[START_PATH_INDEX["yellow"]],
    MAIN_PATH_VISUAL_MAP[START_PATH_INDEX["blue"]],
    MAIN_PATH_VISUAL_MAP[4], MAIN_PATH_VISUAL_MAP[17],
    MAIN_PATH_VISUAL_MAP[30], MAIN_PATH_VISUAL_MAP[43],
]


# ###########################################################################
# #                                                                         #
# #          PESSOA 2: REPRESENTAÇÃO DOS JOGADORES E PEÕES                  #
# #                                                                         #
# ###########################################################################
#
# Explicação: Aqui definimos as classes que representam os elementos do jogo:
# o Peão (Pawn) e o Jogador (Player). A classe `GameLogic` é iniciada aqui,
# preparando o estado inicial do jogo, como a criação dos jogadores e a
# posição inicial de todos os peões.

class Pawn:
    """Representa uma única peça (peão) no jogo."""
    def __init__(self, color, pawn_id):
        self.color = color  # Cor do peão (ex: "red")
        self.pawn_id = pawn_id  # ID do peão (0 a 3)
        # A posição pode ser "home", "finished", ou uma tupla que representa
        # a localização no tabuleiro, ex: ("main_path", 15)
        self.position = "home"

class Player:
    """Representa um jogador, que controla 4 peões."""
    def __init__(self, color):
        self.color = color
        # Cria uma lista com os 4 peões do jogador
        self.pawns = [Pawn(color, i) for i in range(4)]

class GameLogic:
    """
    Controla toda a lógica e as regras do jogo. Não tem relação com a interface,
    apenas com o estado e as regras.
    """
    def __init__(self):
        # Cria um dicionário de jogadores, um para cada cor definida.
        self.players = {color: Player(color) for color in COLORS}
        self.player_order = COLORS  # Define a ordem de jogada
        self.current_player_idx = 0  # Começa com o primeiro jogador da lista
        self.dice_roll = 0  # Armazena o último valor rolado no dado
        self.movable_pawns = []  # Lista de peões que podem se mover no turno atual

        # Dicionário com as coordenadas visuais das "casas" iniciais de cada peão.
        self.initial_pawn_home_coords = {
            "green":  [(2, 2), (3, 2), (2, 3), (3, 3)],
            "red":    [(11, 2), (12, 2), (11, 3), (12, 3)],
            "yellow": [(2, 11), (3, 11), (2, 12), (3, 12)],
            "blue":   [(11, 11), (12, 11), (11, 12), (12, 12)],
        }
    
    # ... O restante da classe GameLogic continua abaixo ...


# ###########################################################################
# #                                                                         #
# #         PESSOA 3: LÓGICA DO DADO E VALIDAÇÃO DE MOVIMENTOS                #
# #                                                                         #
# ###########################################################################
#
# Explicação: Esta parte do código lida com a ação principal do jogador: rolar
# o dado. A função `roll_dice` determina o valor e, em seguida, chama
# `_get_valid_moves` para aplicar as regras do Ludo e descobrir quais peões
# podem ser legalmente movidos com aquele resultado.

    def get_current_player(self):
        """Retorna o objeto do jogador atual."""
        return self.players[self.player_order[self.current_player_idx]]

    def roll_dice(self):
        """Simula o lançamento do dado e encontra os movimentos possíveis."""
        self.dice_roll = random.randint(1, 6)
        player = self.get_current_player()
        # Após rolar o dado, calcula quais peões podem se mover
        self.movable_pawns = self._get_valid_moves(player, self.dice_roll)
        return self.dice_roll, self.movable_pawns

    def _get_valid_moves(self, player, dice_roll):
        """Verifica cada peão do jogador para ver se ele tem um movimento válido."""
        valid_pawns = []
        for pawn in player.pawns:
            # REGRA 1: Ignora peões que já chegaram ao fim.
            if pawn.position == "finished":
                continue

            # REGRA 2: Peões na base ("home") só podem sair com um 6.
            if pawn.position == "home" and dice_roll != 6:
                continue
            
            # Calcula o destino para verificar se o movimento é possível.
            destination = self._calculate_destination(pawn, dice_roll)
            if destination is None:
                # O movimento é inválido se o destino for nulo (ex: passaria do fim da reta final).
                continue

            # REGRA 3 (Simplificada aqui): Evitar bloqueios por peões próprios.
            # (Este código não implementa a regra de bloqueio por 2 peões, mas a estrutura permite isso)
            is_blocked = False
            if destination != "finished":
                is_dest_safe = False
                if destination[0] == "main_path":
                    dest_coords = MAIN_PATH_VISUAL_MAP[destination[1]]
                    if dest_coords in SAFE_SQUARES_COORDS:
                        is_dest_safe = True
                
                # Verifica se a casa de destino já está ocupada por um peão do mesmo jogador (bloqueio simples)
                if not is_dest_safe and destination[0] != "home_stretch":
                    for other_pawn in player.pawns:
                        if other_pawn != pawn and other_pawn.position == destination:
                            is_blocked = True
                            break
            
            if not is_blocked:
                valid_pawns.append(pawn)

        return valid_pawns


# ###########################################################################
# #                                                                         #
# #         PESSOA 4: CÁLCULO DE TRAJETÓRIA E MOVIMENTAÇÃO DO PEÃO            #
# #                                                                         #
# ###########################################################################
#
# Explicação: Estas funções são o "GPS" do peão. `_calculate_destination`
# determina a casa final de um movimento, enquanto `_get_next_logical_pos`
# calcula um único passo no caminho, lidando com a lógica de virar para a
# reta final ou continuar no percurso principal.

    def _get_next_logical_pos(self, color, current_pos):
        """Calcula a próxima posição lógica a partir de uma posição atual."""
        if current_pos == "finished":
            return "finished"
        
        path_length = 52 # Tamanho total do caminho principal
        home_stretch_len = len(HOME_STRETCH_VISUAL_MAP[color])

        # Se já estiver na reta final, avança uma casa ou termina.
        if current_pos[0] == "home_stretch":
            current_idx = current_pos[1]
            if current_idx + 1 < home_stretch_len:
                return ("home_stretch", current_idx + 1)
            else:
                return "finished"
        
        # Se estiver no caminho principal, verifica se deve virar ou continuar.
        if current_pos[0] == "main_path":
            current_idx = current_pos[1]
            
            # Ponto de virada é a casa antes da casa inicial da cor.
            turn_off_square = (START_PATH_INDEX[color] - 1 + path_length) % path_length
            if current_idx == turn_off_square:
                return ("home_stretch", 0)  # Entra na reta final
            else:
                # Avança para a próxima casa no caminho principal (dando a volta se necessário)
                next_idx = (current_idx + 1) % path_length
                return ("main_path", next_idx)
        
        return None # Retorna None se a posição for inválida

    def _calculate_destination(self, pawn, steps):
        """Calcula a posição final de um peão após um número de passos."""
        if pawn.position == "home":
            if steps != 6:
                return None
            # Posição inicial é a casa de partida da cor.
            current_pos = ("main_path", START_PATH_INDEX[pawn.color])
            steps_to_move = steps - 1 # O primeiro passo é para sair da base
        else:
            current_pos = pawn.position
            steps_to_move = steps

        # Simula o movimento passo a passo para encontrar o destino.
        for i in range(steps_to_move):
            current_pos = self._get_next_logical_pos(pawn.color, current_pos)
            if current_pos is None:
                return None # Movimento inválido
            # Verifica se o peão "passaria" do ponto final.
            if current_pos == "finished" and i < steps_to_move - 1:
                return None
        
        return current_pos

    def get_pawn_path_waypoints(self, pawn, steps):
        """Gera uma lista de coordenadas visuais para a animação do movimento."""
        waypoints = [self.get_visual_coords(pawn)]
        
        if pawn.position == "home":
            if steps != 6: return []
            current_pos = ("main_path", START_PATH_INDEX[pawn.color])
            waypoints.append(self.get_visual_coords_for_logical_pos(pawn.color, current_pos))
            steps_to_move = steps - 1
        else:
            current_pos = pawn.position
            steps_to_move = steps
            
        for _ in range(steps_to_move):
            current_pos = self._get_next_logical_pos(pawn.color, current_pos)
            if current_pos == "finished":
                waypoints.append((7.5, 7.5)) # Coordenada do centro para animação
            elif current_pos is not None:
                waypoints.append(self.get_visual_coords_for_logical_pos(pawn.color, current_pos))
        
        return waypoints

    def get_visual_coords_for_logical_pos(self, pawn_color, logical_pos):
        """Traduz uma posição lógica para uma coordenada visual."""
        if logical_pos[0] == "main_path":
            return MAIN_PATH_VISUAL_MAP[logical_pos[1]]
        elif logical_pos[0] == "home_stretch":
            return HOME_STRETCH_VISUAL_MAP[pawn_color][logical_pos[1]]
        return (0,0)

    def move_pawn(self, pawn):
        """Efetivamente move um peão e verifica se houve captura."""
        new_position = self._calculate_destination(pawn, self.dice_roll)

        if new_position:
            pawn.position = new_position
        
        captured_pawn = None
        # Verifica se um peão foi capturado.
        if pawn.position != "finished" and pawn.position[0] == "main_path":
            current_pawn_visual_coords = MAIN_PATH_VISUAL_MAP[pawn.position[1]]

            # Captura só ocorre em casas não seguras.
            if current_pawn_visual_coords not in SAFE_SQUARES_COORDS:
                for other_color in COLORS:
                    if other_color == pawn.color: continue
                    for other_pawn in self.players[other_color].pawns:
                        # Se outro peão de outra cor estiver na mesma posição...
                        if other_pawn.position == pawn.position:
                            other_pawn.position = "home"  # ...ele volta para a base.
                            captured_pawn = other_pawn
                            break
                    if captured_pawn: break
        
        return captured_pawn

    def next_player(self):
        """Passa a vez para o próximo jogador."""
        self.current_player_idx = (self.current_player_idx + 1) % len(self.player_order)

    def get_visual_coords(self, pawn):
        """Obtém as coordenadas visuais atuais de um peão."""
        pos = pawn.position
        if pos == "home":
            return self.initial_pawn_home_coords[pawn.color][pawn.pawn_id]
        if pos == "finished":
            return (7.5, 7.5) # Centro do tabuleiro
        if pos[0] == "main_path":
            return MAIN_PATH_VISUAL_MAP[pos[1]]
        if pos[0] == "home_stretch":
            return HOME_STRETCH_VISUAL_MAP[pawn.color][pos[1]]
        return (0, 0)

    def check_win_condition(self, player):
        """Verifica se um jogador venceu (todos os peões na posição "finished")."""
        return all(pawn.position == "finished" for pawn in player.pawns)


# ###########################################################################
# #                                                                         #
# #      PESSOA 5: INTERFACE GRÁFICA E INTERAÇÃO COM O USUÁRIO (GUI)          #
# #                                                                         #
# ###########################################################################
#
# Explicação: Esta classe, `LudoBoardGUI`, é responsável por tudo que o
# usuário vê. Ela usa a biblioteca `tkinter` para criar a janela, desenhar o
# tabuleiro, os peões e os botões. Também lida com a entrada do usuário,
# como cliques no botão de rolar o dado e cliques nos peões para movê-los.

class LudoBoardGUI:
    def __init__(self, master):
        self.master = master
        self.game = GameLogic() # Instancia a lógica do jogo.
        self.game_lock = threading.Lock() # O "semáforo" para controlar o acesso ao jogo
        self.animation_in_progress = False # Flag para evitar ações durante a animação

        master.title("Ludo")
        # Define o tamanho da janela com base no tamanho e quantidade de quadrados.
        master.geometry(f"{BOARD_GRID_SIZE * SQUARE_SIZE}x{BOARD_GRID_SIZE * SQUARE_SIZE + 100}")
        
        # Cria o Canvas, a "tela" onde o tabuleiro e os peões serão desenhados.
        self.canvas = tk.Canvas(master, width=BOARD_GRID_SIZE * SQUARE_SIZE, height=BOARD_GRID_SIZE * SQUARE_SIZE)
        self.canvas.pack()
        
        # Cria os widgets: label de informação, label do dado e botão de rolar.
        self.info_label = tk.Label(master, text="Bem-vindo ao Ludo! Clique em 'Rolar Dados'.", font=("Arial", 12))
        self.info_label.pack(pady=5)
        
        control_frame = tk.Frame(master)
        control_frame.pack(pady=10)
        self.dice_label = tk.Label(control_frame, text="🎲", font=("Arial", 30))
        self.dice_label.pack(side=tk.LEFT, padx=10)
        self.roll_button = tk.Button(control_frame, text="Rolar Dados", command=self.handle_roll_dice, font=("Arial", 14))
        self.roll_button.pack(side=tk.RIGHT, padx=10)
        
        # Desenha o estado inicial do jogo.
        self.draw_full_board()
        self.draw_all_pawns()
        self.update_turn_indicator()
        
        # Associa o evento de clique do mouse no canvas à função on_canvas_click.
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        
    def on_canvas_click(self, event):
        """É chamado sempre que o usuário clica no tabuleiro."""
        # Se o botão de rolar está ativo ou uma animação está ocorrendo, ignora o clique.
        if self.roll_button['state'] == tk.NORMAL or self.animation_in_progress:
            return

        # Descobre qual item do canvas foi clicado.
        items = self.canvas.find_overlapping(event.x, event.y, event.x, event.y)
        if not items:
            return
        
        # Verifica se o item clicado é um peão que pode ser movido.
        clicked_pawn = None
        for item_id in items:
            pawn = self._get_clicked_pawn(item_id)
            if pawn:
                clicked_pawn = pawn
                break 

        if clicked_pawn:
            # Se um peão válido foi clicado, inicia o processo de movimento.
            self.canvas.delete("highlight") # Remove o destaque dos peões
            threading.Thread(target=self._threaded_move, args=(clicked_pawn,), daemon=True).start()
        else:
            self.info_label.config(text="Clique inválido. Escolha um peão destacado.")
            
    def draw_full_board(self):
        """Desenha todos os elementos estáticos do tabuleiro."""
        # Fundo
        self.canvas.create_rectangle(0, 0, BOARD_GRID_SIZE*SQUARE_SIZE, BOARD_GRID_SIZE*SQUARE_SIZE, fill="#DDEEFF", outline="black")
        # Bases coloridas
        self.canvas.create_rectangle(0, 0, 6*SQUARE_SIZE, 6*SQUARE_SIZE, fill="green", width=0)
        self.canvas.create_rectangle(9*SQUARE_SIZE, 0, 15*SQUARE_SIZE, 6*SQUARE_SIZE, fill="red", width=0)
        self.canvas.create_rectangle(0, 9*SQUARE_SIZE, 6*SQUARE_SIZE, 15*SQUARE_SIZE, fill="yellow", width=0)
        self.canvas.create_rectangle(9*SQUARE_SIZE, 9*SQUARE_SIZE, 15*SQUARE_SIZE, 15*SQUARE_SIZE, fill="blue", width=0)
        # Quadrados internos das bases
        for coords_list in self.game.initial_pawn_home_coords.values():
            for c, r in coords_list:
                self.draw_square(c, r, "white", "black")
        # Caminho principal
        for col, row in MAIN_PATH_VISUAL_MAP.values():
            self.draw_square(col, row, "white", "gray")
        # Retas finais coloridas
        for color, path_coords in HOME_STRETCH_VISUAL_MAP.items():
            for col, row in path_coords:
                self.draw_square(col, row, color, "gray")
        # Casas de início coloridas
        for color, index in START_PATH_INDEX.items():
            self.draw_square(*MAIN_PATH_VISUAL_MAP[index], color, "black")
        # Estrelas nas casas seguras
        for coords in SAFE_SQUARES_COORDS:
            self._draw_star_symbol(*coords)
        # Triângulos centrais
        cx, cy = 7.5*SQUARE_SIZE, 7.5*SQUARE_SIZE
        self.canvas.create_polygon(6*SQUARE_SIZE, 6*SQUARE_SIZE, 9*SQUARE_SIZE, 6*SQUARE_SIZE, cx, cy, fill="red", outline="black")
        self.canvas.create_polygon(9*SQUARE_SIZE, 6*SQUARE_SIZE, 9*SQUARE_SIZE, 9*SQUARE_SIZE, cx, cy, fill="blue", outline="black")
        self.canvas.create_polygon(9*SQUARE_SIZE, 9*SQUARE_SIZE, 6*SQUARE_SIZE, 9*SQUARE_SIZE, cx, cy, fill="yellow", outline="black")
        self.canvas.create_polygon(6*SQUARE_SIZE, 9*SQUARE_SIZE, 6*SQUARE_SIZE, 6*SQUARE_SIZE, cx, cy, fill="green", outline="black")

    def draw_square(self, col, row, color, outline="lightgray", width=1):
        """Função auxiliar para desenhar um único quadrado no tabuleiro."""
        x1, y1 = col * SQUARE_SIZE, row * SQUARE_SIZE
        self.canvas.create_rectangle(x1, y1, x1 + SQUARE_SIZE, y1 + SQUARE_SIZE, fill=color, outline=outline, width=width)

    def _draw_star_symbol(self, col, row):
        """Função auxiliar para desenhar uma estrela em uma casa segura."""
        center_x, center_y = col * SQUARE_SIZE + SQUARE_SIZE / 2, row * SQUARE_SIZE + SQUARE_SIZE / 2
        self.canvas.create_text(center_x, center_y, text="★", font=("Arial", 20), fill="black")

    def draw_all_pawns(self):
        """Apaga e redesenha todos os peões em suas posições atuais."""
        self.canvas.delete("pawn") # Apaga todos os desenhos com a tag "pawn"
        for player in self.game.players.values():
            for pawn in player.pawns: 
                col, row = self.game.get_visual_coords(pawn)
                self.draw_pawn_at(pawn, col, row)

    def draw_all_pawns_except_moving(self, moving_pawn):
        """Redesenha todos os peões, exceto o que está se movendo (para evitar flicker)."""
        self.canvas.delete("pawn")
        for player in self.game.players.values():
            for pawn in player.pawns:
                if pawn != moving_pawn: 
                    col, row = self.game.get_visual_coords(pawn)
                    self.draw_pawn_at(pawn, col, row)

    def draw_pawn_at(self, pawn, col, row):
        """Desenha um único peão em uma coordenada visual específica."""
        x, y = col * SQUARE_SIZE + SQUARE_SIZE / 2, row * SQUARE_SIZE + SQUARE_SIZE / 2
        radius = SQUARE_SIZE / 2.8
        pawn_tag = f"pawn_{pawn.color}_{pawn.pawn_id}"
        self.canvas.delete(pawn_tag) # Apaga a versão antiga deste peão específico
        # Desenha o círculo do peão
        self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, 
                                  fill=pawn.color, outline="black", width=2, 
                                  tags=("pawn", pawn_tag))
        # Escreve o número do peão
        self.canvas.create_text(x, y, text=str(pawn.pawn_id + 1), fill="white", 
                                font=("Arial", 10, "bold"), tags=("pawn", pawn_tag))

    def highlight_movable_pawns(self, pawns):
        """Destaca os peões que podem ser movidos."""
        self.canvas.delete("highlight") # Remove destaques antigos
        for pawn in pawns:
            # Obtém as coordenadas corretas para o destaque.
            if pawn.position == "home":
                coords = self.game.initial_pawn_home_coords[pawn.color][pawn.pawn_id]
                x1, y1 = coords[0] * SQUARE_SIZE, coords[1] * SQUARE_SIZE
            else:
                col, row = self.game.get_visual_coords(pawn)
                x1, y1 = col * SQUARE_SIZE, row * SQUARE_SIZE
            
            # Desenha um retângulo dourado ao redor do quadrado do peão.
            self.canvas.create_rectangle(x1, y1, x1 + SQUARE_SIZE, y1 + SQUARE_SIZE, outline="gold", width=4, tags="highlight")
            
# ###########################################################################
# #                                                                         #
# #      PESSOA 6: CONCORRÊNCIA, ANIMAÇÃO E GERENCIAMENTO DE TURNOS           #
# #                                                                         #
# ###########################################################################
#
# Explicação: Esta é a parte mais complexa. Ela usa Threads para evitar que a
# interface gráfica congele durante as operações do jogo. O `threading.Lock`
# (nosso semáforo) garante que o estado do jogo não seja corrompido.
# A função `animate_pawn` cria o movimento suave das peças, e a `end_turn`
# gerencia a passagem de turno, a regra de jogar de novo com 6, e a
# condição de vitória.

    def _get_clicked_pawn(self, item_id):
        """Verifica se um item clicado no canvas corresponde a um peão que pode ser movido."""
        tags = self.canvas.gettags(item_id)
        for tag in tags:
            if tag.startswith("pawn_"):
                _, color, pawn_id_str = tag.split("_")
                pawn_id = int(pawn_id_str)
                with self.game_lock:
                    pawn_obj = self.game.players[color].pawns[pawn_id]
                    # Retorna o objeto do peão apenas se ele estiver na lista de peões movíveis.
                    if pawn_obj in self.game.movable_pawns:
                        return pawn_obj
        return None

    def handle_roll_dice(self):
        """Inicia a rolagem do dado em uma thread separada para não travar a GUI."""
        if self.animation_in_progress or self.roll_button['state'] == tk.DISABLED: return
        self.roll_button.config(state=tk.DISABLED) # Desativa o botão para evitar cliques duplos
        # Cria e inicia uma nova thread para executar a lógica do dado.
        threading.Thread(target=self._threaded_roll_dice, daemon=True).start()

    def _threaded_roll_dice(self):
        """Função executada na thread. Rola o dado de forma segura."""
        # Usa o 'lock' para garantir que nenhuma outra thread modifique o estado
        # do jogo enquanto estamos rolando o dado e calculando os movimentos.
        with self.game_lock:
            dice_value, movable_pawns = self.game.roll_dice()
        
        # Após a lógica, agenda a atualização da interface de volta na thread principal.
        self.master.after(0, self._update_ui_after_roll, dice_value, movable_pawns)

    def _threaded_move(self, pawn):
        """Executa a lógica de movimento em uma thread separada."""
        # Usa o 'lock' para garantir que o estado do jogo seja modificado de forma segura.
        with self.game_lock:
            if self.animation_in_progress: return # Previne movimentos simultâneos
            self.animation_in_progress = True
            
            # Pega o caminho para a animação e realiza o movimento lógico.
            visual_waypoints = self.game.get_pawn_path_waypoints(pawn, self.game.dice_roll)
            captured_pawn = self.game.move_pawn(pawn)
            
        # Agenda o início da animação na thread principal da GUI.
        self.master.after(0, self.animate_pawn, pawn, visual_waypoints, captured_pawn, 0)

    def animate_pawn(self, pawn, waypoints, captured_pawn_obj, current_waypoint_idx, segment_steps=10, progress_in_segment=0):
        """Anima o movimento do peão de um ponto a outro de forma suave."""
        # Condição de parada: a animação terminou.
        if not waypoints or current_waypoint_idx >= len(waypoints) - 1:
            self.draw_all_pawns() # Garante que a posição final está correta
            if captured_pawn_obj:
                self.info_label.config(text=f"Peão capturado! {pawn.color.capitalize()} joga de novo.")
            self.end_turn() # Finaliza o turno.
            return

        # Lógica para avançar para o próximo segmento do caminho
        if progress_in_segment >= segment_steps:
            progress_in_segment = 0
            current_waypoint_idx += 1
            if current_waypoint_idx >= len(waypoints) - 1: # Checagem extra de segurança
                self.draw_all_pawns()
                if captured_pawn_obj:
                    self.info_label.config(text=f"Peão capturado! {pawn.color.capitalize()} joga de novo.")
                self.end_turn()
                return

        # Interpolação linear para calcular a posição visual atual do peão
        start_col, start_row = waypoints[current_waypoint_idx]
        end_col, end_row = waypoints[current_waypoint_idx + 1]
        progress = progress_in_segment / segment_steps
        current_x_visual = start_col + (end_col - start_col) * progress
        current_y_visual = start_row + (end_row - start_row) * progress

        # Redesenha o tabuleiro e o peão em movimento
        self.draw_all_pawns_except_moving(pawn)
        self.draw_pawn_at(pawn, current_x_visual, current_y_visual)
        
        # Agenda a próxima "frame" da animação em 20ms.
        self.master.after(20, self.animate_pawn, pawn, waypoints, captured_pawn_obj, current_waypoint_idx, segment_steps, progress_in_segment + 1)

    def end_turn(self):
        """Controla o que acontece no final de uma jogada."""
        with self.game_lock: # Usa o lock para ler o estado do jogo com segurança.
            player = self.game.get_current_player()

            # CONDIÇÃO DE VITÓRIA: Verifica se o jogador venceu.
            if self.game.check_win_condition(player):
                self.master.after(0, self._show_win_message_and_quit, player)
                return

            # REGRA DO 6: Se o dado foi 6 (ou capturou-se um peão), o jogador joga de novo.
            if self.game.dice_roll == 6:
                self.animation_in_progress = False
                self.master.after(0, self._update_ui_for_reroll, player)
            else:
                # PASSA A VEZ: Se não, passa para o próximo jogador.
                self.game.next_player()
                self.animation_in_progress = False
                self.master.after(0, self.update_turn_indicator)

    def _update_ui_after_roll(self, dice_value, movable_pawns):
        """Atualiza a interface após o dado ser rolado."""
        self.dice_label.config(text=f"🎲 {dice_value}")
        self.info_label.config(text=f"{self.game.get_current_player().color.capitalize()} rolou {dice_value}!")
        
        if not movable_pawns:
            # Se não há movimentos, passa o turno após um breve delay.
            self.info_label.config(text=f"Nenhum movimento possível para {self.game.get_current_player().color.capitalize()}.")
            self.master.after(1500, self.end_turn) 
        else:
            # Se há movimentos, destaca os peões e pede ao jogador para escolher.
            self.highlight_movable_pawns(movable_pawns)
            self.info_label.config(text="Clique em um peão destacado para mover.")

    def _update_ui_for_reroll(self, player):
        """Atualiza a UI para permitir que o jogador jogue novamente."""
        self.info_label.config(text=f"{player.color.capitalize()} tirou 6 e joga de novo! Role os dados.")
        self.roll_button.config(state=tk.NORMAL) # Reativa o botão de rolar.

    def update_turn_indicator(self):
        """Prepara a interface para o turno do próximo jogador."""
        player_color = self.game.get_current_player().color.capitalize()
        self.info_label.config(text=f"É a vez do jogador {player_color}. Role os dados.")
        self.roll_button.config(state=tk.NORMAL)
        self.dice_label.config(text="🎲")
        self.draw_all_pawns() # Garante que os peões estão nas posições corretas

    def _show_win_message_and_quit(self, player):
        """Mostra a mensagem de vitória e fecha o jogo."""
        messagebox.showinfo("Fim de Jogo", f"O jogador {player.color.capitalize()} venceu!")
        self.master.quit()


# ###########################################################################
# #                                                                         #
# #                       PONTO DE ENTRADA DO PROGRAMA                        #
# #                                                                         #
# ###########################################################################
#
# Explicação: Esta é a parte final do script. `if __name__ == "__main__":`
# garante que este código só será executado quando o arquivo for rodado
# diretamente. Ele cria a janela principal, instancia nossa classe de GUI
# e inicia o loop principal do `tkinter`, que mantém a janela aberta e
# responsiva aos eventos.

if __name__ == "__main__":
    root = tk.Tk()  # Cria a janela principal da aplicação
    game_gui = LudoBoardGUI(root)  # Cria uma instância da nossa classe de interface
    root.mainloop()  # Inicia o loop de eventos do tkinter, que "liga" o programa