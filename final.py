import tkinter as tk
from tkinter import messagebox
import random
import threading
import time

COLORS = ["red", "green", "yellow", "blue"]
SQUARE_SIZE = 40
BOARD_GRID_SIZE = 15

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

START_PATH_INDEX = {
    "red": 48, "green": 9, "yellow": 22, "blue": 35,
}

HOME_STRETCH_VISUAL_MAP = {
    "red": [(7, 1), (7, 2), (7, 3), (7, 4), (7, 5), (7, 6)],
    "green": [(1, 7), (2, 7), (3, 7), (4, 7), (5, 7), (6, 7)],
    "yellow": [(7, 13), (7, 12), (7, 11), (7, 10), (7, 9), (7, 8)],
    "blue": [(13, 7), (12, 7), (11, 7), (10, 7), (9, 7), (8, 7)],
}

LAST_MAIN_SQUARE_BEFORE_HOME = {
    "red": 47,
    "green": 8,
    "yellow": 21,
    "blue": 34
}

SAFE_SQUARES_COORDS = [
    MAIN_PATH_VISUAL_MAP[START_PATH_INDEX["red"]],
    MAIN_PATH_VISUAL_MAP[START_PATH_INDEX["green"]],
    MAIN_PATH_VISUAL_MAP[START_PATH_INDEX["yellow"]],
    MAIN_PATH_VISUAL_MAP[START_PATH_INDEX["blue"]],
    MAIN_PATH_VISUAL_MAP[4], MAIN_PATH_VISUAL_MAP[17],
    MAIN_PATH_VISUAL_MAP[30], MAIN_PATH_VISUAL_MAP[43],
]

class Pawn:
    def __init__(self, color, pawn_id):
        self.color = color
        self.pawn_id = pawn_id
        self.position = "home"

class Player:
    def __init__(self, color):
        self.color = color
        self.pawns = [Pawn(color, i) for i in range(4)]

class GameLogic:
    def __init__(self):
        self.players = {color: Player(color) for color in COLORS}
        self.player_order = COLORS
        self.current_player_idx = 0
        self.dice_roll = 0
        self.movable_pawns = []
        self.initial_pawn_home_coords = {
            "green":  [(2, 2), (3, 2), (2, 3), (3, 3)],
            "red":    [(11, 2), (12, 2), (11, 3), (12, 3)],
            "yellow": [(2, 11), (3, 11), (2, 12), (3, 12)],
            "blue":   [(11, 11), (12, 11), (11, 12), (12, 12)],
        }

    def get_current_player(self):
        return self.players[self.player_order[self.current_player_idx]]

    def roll_dice(self):
        self.dice_roll = random.randint(1, 6)
        player = self.get_current_player()
        self.movable_pawns = self._get_valid_moves(player, self.dice_roll)
        return self.dice_roll, self.movable_pawns

    def _get_valid_moves(self, player, dice_roll):
        valid_pawns = []
        for pawn in player.pawns:
            if pawn.position == "finished":
                continue

            if pawn.position == "home" and dice_roll != 6:
                continue
            
            destination = self._calculate_destination(pawn, dice_roll)
            if destination is None:
                continue

            is_blocked = False
            if destination != "finished":
                is_dest_safe = False
                if destination[0] == "main_path":
                    dest_coords = MAIN_PATH_VISUAL_MAP[destination[1]]
                    if dest_coords in SAFE_SQUARES_COORDS:
                        is_dest_safe = True
                
                if not is_dest_safe and destination[0] != "home_stretch":
                    for other_pawn in player.pawns:
                        if other_pawn != pawn and other_pawn.position == destination:
                            is_blocked = True
                            break
            
            if not is_blocked:
                valid_pawns.append(pawn)

        return valid_pawns

    def _get_next_logical_pos(self, color, current_pos):
        if current_pos == "finished":
            return "finished"
        
        path_length = 52
        home_stretch_len = len(HOME_STRETCH_VISUAL_MAP[color])

        if current_pos[0] == "home_stretch":
            current_idx = current_pos[1]
            if current_idx + 1 < home_stretch_len:
                return ("home_stretch", current_idx + 1)
            else:
                return "finished"
        
        if current_pos[0] == "main_path":
            current_idx = current_pos[1]
            
            # The turn-off point is the square right before the player's starting square.
            turn_off_square = (START_PATH_INDEX[color] - 1 + path_length) % path_length
            if current_idx == turn_off_square:
                return ("home_stretch", 0)
            else:
                next_idx = (current_idx + 1) % path_length
                return ("main_path", next_idx)
        
        return None

    def _calculate_destination(self, pawn, steps):
        if pawn.position == "home":
            if steps != 6:
                return None
            current_pos = ("main_path", START_PATH_INDEX[pawn.color])
            steps_to_move = steps - 1
        else:
            current_pos = pawn.position
            steps_to_move = steps

        for i in range(steps_to_move):
            current_pos = self._get_next_logical_pos(pawn.color, current_pos)
            if current_pos is None:
                return None
            if current_pos == "finished" and i < steps_to_move - 1:
                return None
        
        return current_pos

    def get_pawn_path_waypoints(self, pawn, steps):
        waypoints = [self.get_visual_coords(pawn)]
        
        if pawn.position == "home":
            if steps != 6:
                return []
            current_pos = ("main_path", START_PATH_INDEX[pawn.color])
            waypoints.append(self.get_visual_coords_for_logical_pos(pawn.color, current_pos))
            steps_to_move = steps - 1
        else:
            current_pos = pawn.position
            steps_to_move = steps
            
        for _ in range(steps_to_move):
            current_pos = self._get_next_logical_pos(pawn.color, current_pos)
            if current_pos == "finished":
                waypoints.append((7.5, 7.5))
            elif current_pos is not None:
                waypoints.append(self.get_visual_coords_for_logical_pos(pawn.color, current_pos))
        
        return waypoints

    def get_visual_coords_for_logical_pos(self, pawn_color, logical_pos):
        if logical_pos[0] == "main_path":
            return MAIN_PATH_VISUAL_MAP[logical_pos[1]]
        elif logical_pos[0] == "home_stretch":
            return HOME_STRETCH_VISUAL_MAP[pawn_color][logical_pos[1]]
        return (0,0)

    def move_pawn(self, pawn):
        new_position = self._calculate_destination(pawn, self.dice_roll)

        if new_position:
            pawn.position = new_position
        
        captured_pawn = None
        if pawn.position != "finished" and pawn.position[0] == "main_path":
            current_pawn_visual_coords = MAIN_PATH_VISUAL_MAP[pawn.position[1]]

            if current_pawn_visual_coords not in SAFE_SQUARES_COORDS:
                for other_color in COLORS:
                    if other_color == pawn.color: continue
                    for other_pawn in self.players[other_color].pawns:
                        if other_pawn.position == pawn.position:
                            other_pawn.position = "home"
                            captured_pawn = other_pawn
                            break
                    if captured_pawn: break
        
        return captured_pawn

    def next_player(self):
        self.current_player_idx = (self.current_player_idx + 1) % len(self.player_order)

    def get_visual_coords(self, pawn):
        pos = pawn.position
        if pos == "home":
            return self.initial_pawn_home_coords[pawn.color][pawn.pawn_id]
        if pos == "finished":
            return (7.5, 7.5) 
        if pos[0] == "main_path":
            return MAIN_PATH_VISUAL_MAP[pos[1]]
        if pos[0] == "home_stretch":
            return HOME_STRETCH_VISUAL_MAP[pawn.color][pos[1]]
        return (0, 0)

    def check_win_condition(self, player):
        return all(pawn.position == "finished" for pawn in player.pawns)


class LudoBoardGUI:
    def __init__(self, master):
        self.master = master
        self.game = GameLogic()
        self.game_lock = threading.Lock()
        self.animation_in_progress = False

        master.title("Ludo")
        master.geometry(f"{BOARD_GRID_SIZE * SQUARE_SIZE}x{BOARD_GRID_SIZE * SQUARE_SIZE + 100}")
        self.canvas = tk.Canvas(master, width=BOARD_GRID_SIZE * SQUARE_SIZE, height=BOARD_GRID_SIZE * SQUARE_SIZE)
        self.canvas.pack()
        self.info_label = tk.Label(master, text="Bem-vindo ao Ludo! Clique em 'Rolar Dados'.", font=("Arial", 12))
        self.info_label.pack(pady=5)
        
        control_frame = tk.Frame(master)
        control_frame.pack(pady=10)
        self.dice_label = tk.Label(control_frame, text="🎲", font=("Arial", 30))
        self.dice_label.pack(side=tk.LEFT, padx=10)
        self.roll_button = tk.Button(control_frame, text="Rolar Dados", command=self.handle_roll_dice, font=("Arial", 14))
        self.roll_button.pack(side=tk.RIGHT, padx=10)
        
        self.draw_full_board()
        self.draw_all_pawns()
        self.update_turn_indicator()
        
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        
    def handle_roll_dice(self):
        if self.animation_in_progress or self.roll_button['state'] == tk.DISABLED: return
        self.roll_button.config(state=tk.DISABLED)
        threading.Thread(target=self._threaded_roll_dice, daemon=True).start()

    def _threaded_roll_dice(self):
        with self.game_lock:
            dice_value, movable_pawns = self.game.roll_dice()
        self.master.after(0, self._update_ui_after_roll, dice_value, movable_pawns)

    def on_canvas_click(self, event):
        if self.roll_button['state'] == tk.NORMAL or self.animation_in_progress:
            return

        items = self.canvas.find_overlapping(event.x, event.y, event.x, event.y)
        if not items:
            return
        
        clicked_pawn = None
        for item_id in items:
            pawn = self._get_clicked_pawn(item_id)
            if pawn:
                clicked_pawn = pawn
                break 

        if clicked_pawn:
            self.canvas.delete("highlight")
            threading.Thread(target=self._threaded_move, args=(clicked_pawn,), daemon=True).start()
        else:
            self.info_label.config(text="Clique inválido. Escolha um peão destacado.")

    def _get_clicked_pawn(self, item_id):
        tags = self.canvas.gettags(item_id)
        for tag in tags:
            if tag.startswith("pawn_"):
                _, color, pawn_id_str = tag.split("_")
                pawn_id = int(pawn_id_str)
                with self.game_lock:
                    pawn_obj = self.game.players[color].pawns[pawn_id]
                    if pawn_obj in self.game.movable_pawns:
                        return pawn_obj
        return None

    def _threaded_move(self, pawn):
        with self.game_lock:
            if self.animation_in_progress: return
            self.animation_in_progress = True
            
            visual_waypoints = self.game.get_pawn_path_waypoints(pawn, self.game.dice_roll)
            captured_pawn = self.game.move_pawn(pawn)
            
        self.master.after(0, self.animate_pawn, pawn, visual_waypoints, captured_pawn, 0)

    def animate_pawn(self, pawn, waypoints, captured_pawn_obj, current_waypoint_idx, segment_steps=10, progress_in_segment=0):
        if not waypoints or current_waypoint_idx >= len(waypoints) - 1:
            self.draw_all_pawns()
            if captured_pawn_obj:
                self.info_label.config(text=f"Peão capturado! {pawn.color.capitalize()} joga de novo.")
            self.end_turn()
            return

        if progress_in_segment >= segment_steps:
            progress_in_segment = 0
            current_waypoint_idx += 1
            # Re-check to prevent index errors
            if current_waypoint_idx >= len(waypoints) - 1:
                self.draw_all_pawns()
                if captured_pawn_obj:
                    self.info_label.config(text=f"Peão capturado! {pawn.color.capitalize()} joga de novo.")
                self.end_turn()
                return

        start_col, start_row = waypoints[current_waypoint_idx]
        end_col, end_row = waypoints[current_waypoint_idx + 1]

        progress = progress_in_segment / segment_steps
        current_x_visual = start_col + (end_col - start_col) * progress
        current_y_visual = start_row + (end_row - start_row) * progress

        self.draw_all_pawns_except_moving(pawn)
        self.draw_pawn_at(pawn, current_x_visual, current_y_visual)
        
        self.master.after(20, self.animate_pawn, pawn, waypoints, captured_pawn_obj, current_waypoint_idx, segment_steps, progress_in_segment + 1)

    def end_turn(self):
        """Handles the logic at the end of a player's turn."""
        with self.game_lock:
            player = self.game.get_current_player()

            if self.game.check_win_condition(player):
                self.master.after(0, self._show_win_message_and_quit, player)
                return

            # If a 6 was rolled, the player gets another turn.
            if self.game.dice_roll == 6:
                self.animation_in_progress = False
                self.master.after(0, self._update_ui_for_reroll, player)
            else:
                # Otherwise, it's the next player's turn.
                self.game.next_player()
                self.animation_in_progress = False
                self.master.after(0, self.update_turn_indicator)

    def _update_ui_after_roll(self, dice_value, movable_pawns):
        self.dice_label.config(text=f"🎲 {dice_value}")
        self.info_label.config(text=f"{self.game.get_current_player().color.capitalize()} rolou {dice_value}!")
        
        if not movable_pawns:
            self.info_label.config(text=f"Nenhum movimento possível para {self.game.get_current_player().color.capitalize()}.")
            self.master.after(1500, self.end_turn) 
        else:
            self.highlight_movable_pawns(movable_pawns)
            self.info_label.config(text="Clique em um peão destacado para mover.")

    def _update_ui_for_reroll(self, player):
        self.info_label.config(text=f"{player.color.capitalize()} tirou 6 e joga de novo! Role os dados.")
        self.roll_button.config(state=tk.NORMAL)

    def update_turn_indicator(self):
        player_color = self.game.get_current_player().color.capitalize()
        self.info_label.config(text=f"É a vez do jogador {player_color}. Role os dados.")
        self.roll_button.config(state=tk.NORMAL)
        self.dice_label.config(text="🎲")
        self.draw_all_pawns()

    def highlight_movable_pawns(self, pawns):
        self.canvas.delete("highlight")
        for pawn in pawns:
            # Get the correct visual coordinates for the highlight.
            if pawn.position == "home":
                # Use the coordinates of the pawn's home square, not the pawn piece itself.
                coords = self.game.initial_pawn_home_coords[pawn.color][pawn.pawn_id]
                x1, y1 = coords[0] * SQUARE_SIZE, coords[1] * SQUARE_SIZE
            else:
                col, row = self.game.get_visual_coords(pawn)
                x1, y1 = col * SQUARE_SIZE, row * SQUARE_SIZE
            
            self.canvas.create_rectangle(x1, y1, x1 + SQUARE_SIZE, y1 + SQUARE_SIZE, outline="gold", width=4, tags="highlight")

    def _show_win_message_and_quit(self, player):
        messagebox.showinfo("Fim de Jogo", f"O jogador {player.color.capitalize()} venceu!")
        self.master.quit()

    def draw_full_board(self):
        self.canvas.create_rectangle(0, 0, BOARD_GRID_SIZE*SQUARE_SIZE, BOARD_GRID_SIZE*SQUARE_SIZE, fill="#DDEEFF", outline="black")
        self.canvas.create_rectangle(0, 0, 6*SQUARE_SIZE, 6*SQUARE_SIZE, fill="green", width=0)
        self.canvas.create_rectangle(9*SQUARE_SIZE, 0, 15*SQUARE_SIZE, 6*SQUARE_SIZE, fill="red", width=0)
        self.canvas.create_rectangle(0, 9*SQUARE_SIZE, 6*SQUARE_SIZE, 15*SQUARE_SIZE, fill="yellow", width=0)
        self.canvas.create_rectangle(9*SQUARE_SIZE, 9*SQUARE_SIZE, 15*SQUARE_SIZE, 15*SQUARE_SIZE, fill="blue", width=0)
        for coords_list in self.game.initial_pawn_home_coords.values():
            for c, r in coords_list:
                self.draw_square(c, r, "white", "black")
        for col, row in MAIN_PATH_VISUAL_MAP.values():
            self.draw_square(col, row, "white", "gray")
        for color, path_coords in HOME_STRETCH_VISUAL_MAP.items():
            for col, row in path_coords:
                self.draw_square(col, row, color, "gray")
        for color, index in START_PATH_INDEX.items():
            self.draw_square(*MAIN_PATH_VISUAL_MAP[index], color, "black")
        for coords in SAFE_SQUARES_COORDS:
            self._draw_star_symbol(*coords)
        cx, cy = 7.5*SQUARE_SIZE, 7.5*SQUARE_SIZE
        self.canvas.create_polygon(6*SQUARE_SIZE, 6*SQUARE_SIZE, 9*SQUARE_SIZE, 6*SQUARE_SIZE, cx, cy, fill="red", outline="black")
        self.canvas.create_polygon(9*SQUARE_SIZE, 6*SQUARE_SIZE, 9*SQUARE_SIZE, 9*SQUARE_SIZE, cx, cy, fill="blue", outline="black")
        self.canvas.create_polygon(9*SQUARE_SIZE, 9*SQUARE_SIZE, 6*SQUARE_SIZE, 9*SQUARE_SIZE, cx, cy, fill="yellow", outline="black")
        self.canvas.create_polygon(6*SQUARE_SIZE, 9*SQUARE_SIZE, 6*SQUARE_SIZE, 6*SQUARE_SIZE, cx, cy, fill="green", outline="black")

    def draw_square(self, col, row, color, outline="lightgray", width=1):
        x1, y1 = col * SQUARE_SIZE, row * SQUARE_SIZE
        self.canvas.create_rectangle(x1, y1, x1 + SQUARE_SIZE, y1 + SQUARE_SIZE, fill=color, outline=outline, width=width)

    def _draw_star_symbol(self, col, row):
        center_x, center_y = col * SQUARE_SIZE + SQUARE_SIZE / 2, row * SQUARE_SIZE + SQUARE_SIZE / 2
        self.canvas.create_text(center_x, center_y, text="★", font=("Arial", 20), fill="black")

    def draw_all_pawns(self):
        self.canvas.delete("pawn")
        for player in self.game.players.values():
            for pawn in player.pawns: 
                col, row = self.game.get_visual_coords(pawn)
                self.draw_pawn_at(pawn, col, row)

    def draw_all_pawns_except_moving(self, moving_pawn):
        self.canvas.delete("pawn")
        for player in self.game.players.values():
            for pawn in player.pawns:
                if pawn != moving_pawn: 
                    col, row = self.game.get_visual_coords(pawn)
                    self.draw_pawn_at(pawn, col, row)

    def draw_pawn_at(self, pawn, col, row):
        x, y = col * SQUARE_SIZE + SQUARE_SIZE / 2, row * SQUARE_SIZE + SQUARE_SIZE / 2
        radius = SQUARE_SIZE / 2.8
        pawn_tag = f"pawn_{pawn.color}_{pawn.pawn_id}"
        self.canvas.delete(pawn_tag) 
        self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, 
                                  fill=pawn.color, outline="black", width=2, 
                                  tags=("pawn", pawn_tag))
        self.canvas.create_text(x, y, text=str(pawn.pawn_id + 1), fill="white", 
                                font=("Arial", 10, "bold"), tags=("pawn", pawn_tag))

if __name__ == "__main__":
    root = tk.Tk()
    game_gui = LudoBoardGUI(root)
    root.mainloop()