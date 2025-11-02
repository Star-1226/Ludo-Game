import random
import tkinter as tk
from tkinter import messagebox


class Player:
    def __init__(self, name, color):
        self.name = name
        self.color = color
        self.pieces = [0, 0, 0, 0] # 0: in base, 1-52: on board, 53-58: home stretch, 100: finished
        self.six_rolls_in_a_row = 0
        self.blocked_pieces = []
        self.finished_pieces = 0

    def all_pieces_home(self):
        return all(postion == 0 for postion in self.pieces)

    def all_pieces_finished(self):
        return self.finished_pieces == 4


class LudoGame:
    def __init__(self):
        self.board_size = 52
        self.start_positions = {
            "Red": 1,
            "Green": 14,
            "Yellow": 27,
            "Blue": 40
        }
        self.home_stretch_positions = {
            "Red": [52, 53, 54, 55, 56, 57], # Positions before entering home
            "Green": [13, 12, 11, 10, 9, 8], # These will need to be mapped to global board positions
            "Yellow": [26, 25, 24, 23, 22, 21],
            "Blue": [39, 38, 37, 36, 35, 34]
        }
        self.players = [
            Player("Player 1", "Red"),
            Player("Player 2", "Green"),
            Player("Player 3", "Blue"),
            Player("Player 4", "Yellow"),
        ]
        self.current_player_idx = 0
        self.last_roll = None
        self.six_rolls_count = 0
        self.game_log = []
        self.game_over = False

    def roll_dice(self):
        player = self.players[self.current_player_idx]
        roll = random.randint(1, 6)
        self.game_log.append(f"{player.name} rolled a {roll}")

        if roll == 6:
            player.six_rolls_in_a_row += 1
            if player.six_rolls_in_a_row == 3:
                self.game_log.append(f"{player.name} rolled three 6s in a row and loses their turn.")
                player.six_rolls_in_a_row = 0
                self.last_roll = None # Player loses turn, no move can be made
                self.next_player()
                return {"roll": roll, "lost_turn": True}
        else:
            player.six_rolls_in_a_row = 0

        self.last_roll = roll
        return {"roll": roll, "lost_turn": False}

    def move_piece(self, player, piece_idx, steps):
        current_position = player.pieces[piece_idx]
        player_color = player.color
        start_pos = self.start_positions[player_color]
        home_stretch = self.home_stretch_positions[player_color]

        # Case 1: Piece is in the base
        if current_position == 0:
            if steps == 6:
                player.pieces[piece_idx] = start_pos
                self.game_log.append(f"{player.name}'s {player_color} piece {piece_idx+1} moved out of base to start position.")
                return {"moved": True, "next_player": False}  # Extra roll for 6
            else:
                self.game_log.append(f"{player.name}'s {player_color} piece {piece_idx+1} needs a 6 to move out of base.")
                return {"moved": False, "next_player": True}

        board_path = list(range(1, self.board_size + 1))
        
        # Determine effective current position for movement
        effective_current_position = current_position
        
        # Calculate new potential position
        new_position = effective_current_position + steps

        # Check if entering home stretch
        if effective_current_position <= self.board_size and new_position > self.board_size:
            if new_position > (self.board_size + 6): # Beyond the home stretch
                self.game_log.append(f"{player.name}'s {player_color} piece {piece_idx+1} cannot move beyond home with {steps}.")
                return {"moved": False, "next_player": steps != 6}
            
            player.pieces[piece_idx] = new_position
            if new_position == (self.board_size + 6): # Reached home column
                player.finished_pieces += 1
                player.pieces[piece_idx] = 100 # Mark as finished
                self.game_log.append(f"{player.name}'s {player_color} piece {piece_idx+1} reached home!")
                if player.finished_pieces == 4:
                    self.game_over = True
                    self.game_log.append(f"Game Over! {player.name} wins!")
                return {"moved": True, "finished": True, "next_player": steps != 6}
            
            self.game_log.append(f"{player.name}'s {player_color} piece {piece_idx+1} moved to {new_position} (home stretch).")
            return {"moved": True, "next_player": steps != 6}

        # Check for movement on the main board
        if new_position <= self.board_size:
            player.pieces[piece_idx] = new_position
            self.game_log.append(f"{player.name}'s {player_color} piece {piece_idx+1} moved to {new_position}.")

            # Check for landing on opponent's pawn
            for opponent in self.players:
                if opponent.color != player_color:
                    for opp_piece_idx, opp_pos in enumerate(opponent.pieces):
                        if opp_pos == new_position and new_position != start_pos: # Cannot send back at start
                            opponent.pieces[opp_piece_idx] = 0 # Send back to base
                            self.game_log.append(f"{player.name}'s {player_color} piece {opp_piece_idx+1} landed on {opponent.name}'s {opponent.color} piece {opp_piece_idx+1}, sending it back to base!")
            
            return {"moved": True, "next_player": steps != 6}
        
        # If the new position is beyond the main board but not yet in the home stretch (or an invalid move)
        self.game_log.append(f"{player.name}'s {player_color} piece {piece_idx+1} cannot move to {new_position}.")
        return {"moved": False, "next_player": steps != 6} # If not moved, next player always turns

    def next_player(self):
        self.current_player_idx = (self.current_player_idx + 1) % len(self.players)

    def is_game_over(self):
        return self.game_over

    def game_state(self):
        return {
            "players": [
                {
                    "name": p.name,
                    "color": p.color,
                    "pieces": p.pieces,
                    "sixRollsInARow": p.six_rolls_in_a_row,
                    "finishedPieces": p.finished_pieces,
                } for p in self.players
            ],
            "currentPlayerIndex": self.current_player_idx,
            "lastRoll": self.last_roll,
            "gameOver": self.is_game_over(),
            "gameLog": self.game_log,
            "startPositions": self.start_positions
        }

    def get_movable_pieces(self, player, roll):
        movable_indices = []
        for i, position in enumerate(player.pieces):
            if position == 0 and roll == 6:
                movable_indices.append(i)
            elif 0 < position < 100:
                # This is a simplified check. A more robust Ludo game would involve
                # checking if the move is valid based on the current board state,
                # including opponent's pieces and home stretch.
                # For now, we'll allow any piece on the board or home stretch to be movable
                # if the roll is available.
                movable_indices.append(i)
        return movable_indices


class LudoGUI:
    def __init__(self, master):
        self.master = master
        master.title("Ludo Game")
        self.game = LudoGame()

        self.player_colors_map = {"Red": "#ef4444", "Green": "#22c55e", "Yellow": "#f59e0b", "Blue": "#3b82f6"}
        self.base_colors_map = {"Red": "#7f1d1d", "Green": "#064e3b", "Yellow": "#7c4a03", "Blue": "#0b3579"}
        self.cell_labels = {}  # To store references to labels for pieces
        self.piece_widgets = {} # Store piece IDs on canvas

        self.board_size_px = 600
        self.cell_size_px = self.board_size_px / 15

        # --- GUI Elements ---
        self.create_widgets()
        self.update_gui()

    def create_widgets(self):
        main_frame = tk.Frame(self.master, bg="#0b1220")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Player Info Frame
        self.player_info_frame = tk.Frame(main_frame, bg="#0f172a", bd=2, relief="groove")
        self.player_info_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.Y)
        
        self.player_labels = []
        for i, player in enumerate(self.game.players):
            p_frame = tk.Frame(self.player_info_frame, bg="#0f172a")
            p_frame.pack(pady=5, padx=5, anchor="w")

            color_swatch = tk.Label(p_frame, bg=self.player_colors_map[player.color], width=2, height=1, relief="solid", bd=1)
            color_swatch.pack(side=tk.LEFT, padx=2)

            p_label = tk.Label(p_frame, text=f"{player.name} ({player.color}): 0 finished", bg="#0f172a", fg="white")
            p_label.pack(side=tk.LEFT, padx=2)
            self.player_labels.append(p_label)

        # Game Board Canvas
        self.board_canvas = tk.Canvas(main_frame, width=self.board_size_px, height=self.board_size_px, bg="#111827", bd=2, relief="groove")
        self.board_canvas.pack(side=tk.LEFT, padx=10, pady=10)
        self._draw_static_board()

        # Control and Log Frame
        right_frame = tk.Frame(main_frame, bg="#0b1220")
        right_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.BOTH, expand=True)

        control_frame = tk.Frame(right_frame, bg="#0f172a", bd=2, relief="groove")
        control_frame.pack(pady=10, fill=tk.X)

        self.dice_label = tk.Label(control_frame, text="Dice: --", font=("Arial", 16), bg="#0f172a", fg="white")
        self.dice_label.pack(side=tk.LEFT, padx=10, pady=5)

        self.roll_button = tk.Button(control_frame, text="Roll Dice", command=self.roll_dice, bg="#111827", fg="white", activebackground="#1f2937", activeforeground="white")
        self.roll_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.reset_button = tk.Button(control_frame, text="Reset Game", command=self.reset_game, bg="#111827", fg="white", activebackground="#1f2937", activeforeground="white")
        self.reset_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Game Log
        self.log_frame = tk.Frame(right_frame, bg="#0f172a", bd=2, relief="groove")
        self.log_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        self.log_label = tk.Label(self.log_frame, text="Game Log:", anchor="w", bg="#0f172a", fg="white")
        self.log_label.pack(side=tk.TOP, fill=tk.X)

        self.log_text = tk.Text(self.log_frame, height=15, width=40, state="disabled", bg="#111827", fg="#94a3b8", bd=0, highlightthickness=0)
        self.log_text.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

    def _draw_static_board(self):
        # Draw grid cells
        for r in range(15):
            for c in range(15):
                x1, y1 = c * self.cell_size_px, r * self.cell_size_px
                x2, y2 = x1 + self.cell_size_px, y1 + self.cell_size_px
                self.board_canvas.create_rectangle(x1, y1, x2, y2, fill="#111827", outline="#1f2937", width=1)
        
        # Draw home bases
        home_base_coords = {
            "Red": [(0,0), (5,5)],
            "Green": [(0,9), (5,14)],
            "Yellow": [(9,0), (14,5)],
            "Blue": [(9,9), (14,14)]
        }
        for color_name, (start_rc, end_rc) in home_base_coords.items():
            r1, c1 = start_rc
            r2, c2 = end_rc
            x1, y1 = c1 * self.cell_size_px, r1 * self.cell_size_px
            x2, y2 = (c2 + 1) * self.cell_size_px, (r2 + 1) * self.cell_size_px
            self.board_canvas.create_rectangle(x1, y1, x2, y2, fill=self.base_colors_map[color_name], outline="#1f2937", width=1)
        
        # Draw start cells within home bases
        start_cell_offsets = {
            "Red": [(1,1),(1,3),(3,1),(3,3)],
            "Green": [(1,10),(1,12),(3,10),(3,12)],
            "Yellow": [(10,1),(10,3),(12,1),(12,3)],
            "Blue": [(10,10),(10,12),(12,10),(12,12)]
        }
        for color_name, offsets in start_cell_offsets.items():
            for r_offset, c_offset in offsets:
                x1, y1 = c_offset * self.cell_size_px, r_offset * self.cell_size_px
                x2, y2 = x1 + self.cell_size_px, y1 + self.cell_size_px
                self.board_canvas.create_rectangle(x1, y1, x2, y2, fill="#111827", outline="#1f2937", width=1)

        # Draw main path
        path_coords = self._get_path_coordinates()
        for r, c in path_coords:
            x1, y1 = c * self.cell_size_px, r * self.cell_size_px
            x2, y2 = x1 + self.cell_size_px, y1 + self.cell_size_px
            self.board_canvas.create_rectangle(x1, y1, x2, y2, fill="#0f172a", outline="#1f2937", width=1)

        # Draw home stretches
        home_stretch_coords = self._get_home_stretch_coordinates()
        for color_name, coords in home_stretch_coords.items():
            for r, c in coords:
                x1, y1 = c * self.cell_size_px, r * self.cell_size_px
                x2, y2 = x1 + self.cell_size_px, y1 + self.cell_size_px
                self.board_canvas.create_rectangle(x1, y1, x2, y2, fill=self.player_colors_map[color_name], outline="#1f2937", width=1, dash=(2,2))
        
        # Draw center square
        center_start_r, center_start_c = 6, 6
        center_end_r, center_end_c = 8, 8
        x1, y1 = center_start_c * self.cell_size_px, center_start_r * self.cell_size_px
        x2, y2 = (center_end_c + 1) * self.cell_size_px, (center_end_r + 1) * self.cell_size_px
        self.board_canvas.create_rectangle(x1, y1, x2, y2, fill="#0f172a", outline="#1f2937", width=1)



    def log_message(self, message):
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END) # Auto-scroll to the end
        self.log_text.config(state="disabled")

    def update_gui(self):
        state = self.game.game_state()
        self.dice_label.config(text=f"Dice: {state['lastRoll'] if state['lastRoll'] else '--'}")
        
        # Update player info
        for i, player_data in enumerate(state['players']):
            self.player_labels[i].config(text=f"{player_data['name']} ({player_data['color']}): {player_data['finishedPieces']} finished")
            if i == state['currentPlayerIndex']:
                self.player_labels[i].config(font=("Arial", 10, "bold"), fg="yellow") # Highlight current player
            else:
                self.player_labels[i].config(font=("Arial", 10, "normal"), fg="white")

        # Update game log
        self.log_text.config(state="normal")
        self.log_text.delete(1.0, tk.END) # Clear existing log
        for msg in state['gameLog']:
            self.log_message(msg)
        self.log_text.config(state="disabled")

        self.render_board()

        if state['gameOver']:
            messagebox.showinfo("Game Over", f"{state['players'][state['currentPlayerIndex']]['name']} wins!")
            self.roll_button.config(state="disabled")

    def render_board(self):
        # Clear existing pieces on canvas
        for piece_id in self.piece_widgets.values():
            self.board_canvas.delete(piece_id)
        self.piece_widgets.clear()

        # Define simplified board coordinates for GUI
        path_coords = self._get_path_coordinates()
        home_stretch_coords = self._get_home_stretch_coordinates()
        
        base_start_cell_coords = {
            "Red": [(1,1),(1,3),(3,1),(3,3)],
            "Green": [(1,10),(1,12),(3,10),(3,12)],
            "Yellow": [(10,1),(10,3),(12,1),(12,3)],
            "Blue": [(10,10),(10,12),(12,10),(12,12)]
        }

        for player_idx, player_data in enumerate(self.game.players):
            player_color_name = player_data.color
            player_gui_color = self.player_colors_map[player_color_name]

            for piece_idx, piece_position in enumerate(player_data.pieces):
                r, c = -1, -1 # Invalid coordinates by default

                if piece_position == 0:  # In base
                    if player_color_name in base_start_cell_coords and piece_idx < len(base_start_cell_coords[player_color_name]):
                        r, c = base_start_cell_coords[player_color_name][piece_idx]

                elif 1 <= piece_position <= 52: # On main path
                    if piece_position - 1 < len(path_coords):
                        r, c = path_coords[piece_position - 1]

                elif 53 <= piece_position < 100: # In home stretch
                    stretch_index = piece_position - 53
                    if player_color_name in home_stretch_coords and stretch_index < len(home_stretch_coords[player_color_name]):
                        r, c = home_stretch_coords[player_color_name][stretch_index]
                
                # Draw piece on GUI if coordinates are valid
                if r != -1 and c != -1:
                    x_center = (c * self.cell_size_px) + (self.cell_size_px / 2)
                    y_center = (r * self.cell_size_px) + (self.cell_size_px / 2)
                    radius = self.cell_size_px / 3
                    
                    piece_id = self.board_canvas.create_oval(
                        x_center - radius, y_center - radius,
                        x_center + radius, y_center + radius,
                        fill=player_gui_color, outline="white", width=1
                    )
                    self.board_canvas.create_text(x_center, y_center, text=str(piece_idx + 1), fill="white", font=("Arial", 10, "bold"), tags=piece_id) # Add piece number
                    self.board_canvas.tag_bind(piece_id, "<Button-1>", lambda e, p_idx=player_idx, pc_idx=piece_idx: self.handle_piece_click(p_idx, pc_idx))
                    self.board_canvas.tag_bind(f"text{piece_id}", "<Button-1>", lambda e, p_idx=player_idx, pc_idx=piece_idx: self.handle_piece_click(p_idx, pc_idx))
                    self.piece_widgets[(player_idx, piece_idx)] = piece_id # Store reference
                    
        # Highlight current player's movable pieces
        current_player_idx = self.game.current_player_idx
        roll = self.game.last_roll
        if roll is not None:
            current_player = self.game.players[current_player_idx]
            for piece_idx, position in enumerate(current_player.pieces):
                # A piece is movable if it's in base and rolled a 6, or it's on the board/home stretch
                # and there's a valid move (simplified check for now, can be improved)
                is_movable = False
                if position == 0 and roll == 6:
                    is_movable = True
                elif 0 < position < 100:
                    # For now, assume any piece on the board or home stretch is movable
                    # This needs more sophisticated logic based on actual Ludo rules (e.g., blocking, exact landing)
                    # For the current simple implementation, we'll allow movement if roll is available
                    is_movable = True
                
                if is_movable:
                    piece_id = self.piece_widgets.get((current_player_idx, piece_idx))
                    if piece_id:
                        self.board_canvas.itemconfig(piece_id, outline="yellow", width=3) # Highlight movable pieces

    def _get_path_coordinates(self):
        # Red's path (clockwise from start)
        path = [
            (6,1), (6,2), (6,3), (6,4), (6,5),
            (5,6), (4,6), (3,6), (2,6), (1,6), (0,6),
            (0,7),
            (0,8), (1,8), (2,8), (3,8), (4,8), (5,8),
            (6,9), (6,10), (6,11), (6,12), (6,13),
            (7,14),
            (8,13), (8,12), (8,11), (8,10), (8,9), (8,8),
            (9,8), (10,8), (11,8), (12,8), (13,8), (14,8),
            (14,7),
            (14,6), (13,6), (12,6), (11,6), (10,6), (9,6),
            (8,5), (8,4), (8,3), (8,2), (8,1),
            (7,0),
        ]
        return path

    def _get_home_stretch_coordinates(self):
        home_stretches = {
            "Red": [(7,1), (7,2), (7,3), (7,4), (7,5), (7,6)],
            "Green": [(1,7), (2,7), (3,7), (4,7), (5,7), (6,7)],
            "Yellow": [(7,13), (7,12), (7,11), (7,10), (7,9), (7,8)],
            "Blue": [(13,7), (12,7), (11,7), (10,7), (9,7), (8,7)]
        }
        return home_stretches

    def roll_dice(self):
        if self.game.is_game_over():
            messagebox.showinfo("Game Over", "The game is already over!")
            return
        
        roll_result = self.game.roll_dice()
        if roll_result.get("lost_turn"):
            self.log_message(f"Player {self.game.current_player_idx + 1} lost their turn!")
            self.update_gui()
            return

        self.update_gui()

        player = self.game.players[self.game.current_player_idx]
        movable_pieces_indices = [
            i
            for i, position in enumerate(player.pieces)
            if (position > 0 and position < 100) or (position == 0 and self.game.last_roll == 6)
        ]
        if not movable_pieces_indices and not (self.game.last_roll == 6 and any(p == 0 for p in player.pieces)):
            self.log_message(f"Player {self.game.current_player_idx + 1} has no valid moves. Next turn.")
            self.game.last_roll = None # Clear last roll if no moves possible
            self.game.next_player()
            self.update_gui()

    def handle_piece_click(self, player_idx, piece_idx):
        if player_idx != self.game.current_player_idx:
            self.log_message("It's not your turn!")
            return
        if self.game.last_roll is None:
            self.log_message("You must roll the dice first!")
            return
        
        # More robust check for movable pieces
        movable_pieces = self.game.get_movable_pieces(self.game.players[player_idx], self.game.last_roll)
        if piece_idx not in movable_pieces:
            self.log_message(f"Piece {piece_idx + 1} is not a valid move with a roll of {self.game.last_roll}.")
            return

        result = self.game.move_piece(self.game.players[player_idx], piece_idx, self.game.last_roll)
        if result["moved"]:
            self.log_message(f"Player {player_idx+1} moved token {piece_idx+1} by {self.game.last_roll} steps.")
        else:
            self.log_message(f"Player {player_idx+1} could not move token {piece_idx+1}.")
        
        if result.get("next_player", True):
            self.game.next_player()
        
        self.game.last_roll = None # Clear last roll after a move
        self.update_gui()

    def reset_game(self):
        self.game = LudoGame() # Recreate game instance
        self.roll_button.config(state="normal")
        self.log_text.config(state="normal")
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state="disabled")
        self.log_message("Game reset complete.")
        self.update_gui()


if __name__ == "__main__":
    root = tk.Tk()
    gui = LudoGUI(root)
    root.mainloop()
