
import tkinter as tk
from tkinter import ttk, messagebox
import random
import subprocess


class SudokuApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sudoku")
        self.root.geometry("720x820")
        self.root.minsize(520, 620)

        self.size = 9
        self.box_size = 3

        self.solution = []
        self.puzzle = []
        self.entries = {}
        self.marked_cells = set()
        self.mistake_cells = set()
        self.selected_cell = None
        self.undo_stack = []

        self.dark_mode = self.detect_dark_mode()

        self.update_colors()

        # -----------------------------
        # SLOG
        # -----------------------------
        self.style = ttk.Style()

        try:
            self.style.theme_use("aqua")
        except tk.TclError:
            try:
                self.style.theme_use("clam")
            except tk.TclError:
                pass

        self.style.configure(
            "Sudoku.TButton",
            font=("Helvetica Neue", 14),
            padding=(18, 8)
        )

        self.style.configure(
            "Sudoku.TMenubutton",
            font=("Helvetica Neue", 14),
            padding=(10, 6)
        )

        # -----------------------------
        # MENI
        # -----------------------------
        self.create_menu()

        # -----------------------------
        # GLAVNI KONTEJNER
        # -----------------------------
        self.main = tk.Frame(self.root, bg=self.BG)
        self.main.pack(fill="both", expand=True, padx=24, pady=20)

        # -----------------------------
        # GLAVA
        # -----------------------------
        self.header = tk.Frame(self.main, bg=self.BG)
        self.header.pack(fill="x", pady=(0, 15))

        self.header_top = tk.Frame(self.header, bg=self.BG)
        self.header_top.pack(fill="x")

        self.title_label = tk.Label(
            self.header_top,
            text="Sudoku",
            font=("Helvetica Neue", 32, "bold"),
            bg=self.BG,
            fg=self.TEXT,
            anchor="w"
        )
        self.title_label.pack(side="left")

        self.size_var = tk.StringVar(value="9 × 9")

        self.size_menu = ttk.OptionMenu(
            self.header_top,
            self.size_var,
            "9 × 9",
            "4 × 4",
            "9 × 9",
            "16 × 16",
            command=self.change_size
        )
        self.size_menu.configure(style="Sudoku.TMenubutton")
        self.size_menu.pack(side="right")

        self.subtitle = tk.Label(
            self.header,
            text="Izberi številke in zapolni celotno mrežo.",
            font=("Helvetica Neue", 14),
            bg=self.BG,
            fg=self.SECONDARY,
            anchor="w"
        )
        self.subtitle.pack(fill="x", pady=(5, 0))

        # -----------------------------
        # KARTICA ZA MREŽO
        # -----------------------------
        self.card = tk.Frame(
            self.main,
            bg=self.CARD,
            highlightthickness=0
        )
        self.card.pack(fill="both", expand=True)

        self.card.bind("<Configure>", self.resize_grid)

        self.grid_frame = None

        # -----------------------------
        # GUMBI
        # -----------------------------
        self.controls = tk.Frame(self.main, bg=self.BG)
        self.controls.pack(fill="x", pady=(15, 0))

        self.new_button = ttk.Button(
            self.controls,
            text="Nova igra",
            style="Sudoku.TButton",
            command=self.new_game
        )
        self.new_button.pack(side="left")

        self.marker_button = ttk.Button(
            self.controls,
            text="Označi celico",
            style="Sudoku.TButton",
            command=self.toggle_marker
        )
        self.marker_button.pack(side="left", padx=(10, 0))

        self.check_button = ttk.Button(
            self.controls,
            text="Preveri",
            style="Sudoku.TButton",
            command=self.check_solution
        )
        self.check_button.pack(side="right")

        # -----------------------------
        # TIPKE
        # -----------------------------
        self.root.bind_all("<KeyPress-m>", self.global_m)
        self.root.bind_all("<KeyPress-M>", self.global_m)

        # Začetna igra
        self.new_game(force=True)

        # Preverjanje temnega načina
        self.last_dark_mode = self.dark_mode
        self.root.after(2000, self.check_appearance)

    # ============================================================
    # TEMNI NAČIN
    # ============================================================

    def detect_dark_mode(self):
        try:
            result = subprocess.run(
                ["defaults", "read", "-g", "AppleInterfaceStyle"],
                capture_output=True,
                text=True,
                timeout=1
            )
            return result.stdout.strip().lower() == "dark"
        except Exception:
            return False

    def update_colors(self):
        if self.dark_mode:
            self.BG = "#1c1c1e"
            self.CARD = "#2c2c2e"
            self.CELL = "#2c2c2e"
            self.TEXT = "#f5f5f7"
            self.SECONDARY = "#98989d"
            self.GRID = "#636366"
            self.BLUE = "#0a84ff"
            self.FIXED_BG = "#3a3a3c"
            self.YELLOW = "#665c00"
            self.RED_BG = "#5c2020"
        else:
            self.BG = "#f5f5f7"
            self.CARD = "#ffffff"
            self.CELL = "#ffffff"
            self.TEXT = "#1d1d1f"
            self.SECONDARY = "#6e6e73"
            self.GRID = "#c7c7cc"
            self.BLUE = "#007aff"
            self.FIXED_BG = "#f2f2f7"
            self.YELLOW = "#fff3a6"
            self.RED_BG = "#ffd6d6"

    def apply_theme(self):
        self.root.configure(bg=self.BG)

        widgets = [
            self.main,
            self.header,
            self.header_top,
            self.controls
        ]

        for widget in widgets:
            if widget is not None:
                widget.configure(bg=self.BG)

        if hasattr(self, "card"):
            self.card.configure(bg=self.CARD)

        if hasattr(self, "title_label"):
            self.title_label.configure(
                bg=self.BG,
                fg=self.TEXT
            )

        if hasattr(self, "subtitle"):
            self.subtitle.configure(
                bg=self.BG,
                fg=self.SECONDARY
            )

        self.refresh_cell_colors()

    def check_appearance(self):
        current = self.detect_dark_mode()

        if current != self.last_dark_mode:
            self.dark_mode = current
            self.last_dark_mode = current
            self.update_colors()
            self.apply_theme()

        self.root.after(2000, self.check_appearance)

    # ============================================================
    # MENI
    # ============================================================

    def create_menu(self):
        menu = tk.Menu(self.root)

        game_menu = tk.Menu(menu, tearoff=0)
        game_menu.add_command(
            label="Nova igra",
            command=self.new_game
        )
        game_menu.add_command(
            label="Razveljavi",
            command=self.undo
        )
        game_menu.add_separator()
        game_menu.add_command(
            label="Preveri",
            command=self.check_solution
        )
        game_menu.add_command(
            label="Prikaži napake",
            command=self.show_mistakes
        )
        game_menu.add_separator()
        game_menu.add_command(
            label="Izhod",
            command=self.root.destroy
        )

        menu.add_cascade(
            label="Igra",
            menu=game_menu
        )

        help_menu = tk.Menu(menu, tearoff=0)
        help_menu.add_command(
            label="Kako igrati",
            command=self.show_help
        )
        help_menu.add_command(
            label="O Sudokuju",
            command=self.show_about
        )

        menu.add_cascade(
            label="Pomoč",
            menu=help_menu
        )

        self.root.config(menu=menu)

    # ============================================================
    # NOVA IGRA
    # ============================================================

    def has_user_progress(self):
        for (r, c), entry in self.entries.items():
            if (r, c) not in self.puzzle_fixed():
                if entry.get().strip():
                    return True

        return bool(self.marked_cells)

    def puzzle_fixed(self):
        fixed = set()

        for r in range(self.size):
            for c in range(self.size):
                if self.puzzle[r][c] != 0:
                    fixed.add((r, c))

        return fixed

    def new_game(self, force=False):
        if not force and self.has_user_progress():
            answer = messagebox.askyesno(
                "Nova igra",
                "Ta Sudoku je že delno rešen.\n\n"
                "Ali želiš začeti novo igro?"
            )

            if not answer:
                return

        self.undo_stack.clear()
        self.marked_cells.clear()
        self.mistake_cells.clear()
        self.selected_cell = None

        self.generate_sudoku()
        self.create_grid()

    # ============================================================
    # GENERATOR
    # ============================================================

    def generate_sudoku(self):
        if self.size == 4:
            self.box_size = 2
        elif self.size == 9:
            self.box_size = 3
        else:
            self.box_size = 4

        base = self.box_size

        def pattern(row, col):
            return (
                base * (row % base)
                + row // base
                + col
            ) % self.size

        rows = []
        groups = list(range(base))

        for group in random.sample(groups, len(groups)):
            for row in random.sample(
                list(range(group * base, group * base + base)),
                base
            ):
                rows.append(row)

        cols = []

        for group in random.sample(groups, len(groups)):
            for col in random.sample(
                list(range(group * base, group * base + base)),
                base
            ):
                cols.append(col)

        nums = list(range(1, self.size + 1))
        random.shuffle(nums)

        self.solution = [
            [
                nums[pattern(r, c)]
                for c in cols
            ]
            for r in rows
        ]

        self.puzzle = [
            row[:] for row in self.solution
        ]

        if self.size == 4:
            remove_count = 7
        elif self.size == 9:
            remove_count = 48
        else:
            remove_count = 170

        cells = [
            (r, c)
            for r in range(self.size)
            for c in range(self.size)
        ]

        random.shuffle(cells)

        for r, c in cells[:remove_count]:
            self.puzzle[r][c] = 0

    # ============================================================
    # USTVARJANJE MREŽE
    # ============================================================

    def create_grid(self):
        if self.grid_frame is not None:
            self.grid_frame.destroy()

        self.grid_frame = tk.Frame(
            self.card,
            bg=self.GRID
        )

        self.grid_frame.place(
            relx=0.5,
            rely=0.5,
            anchor="center"
        )

        self.entries = {}

        n = self.size

        for r in range(n):
            self.grid_frame.rowconfigure(
                r,
                weight=1,
                uniform="sudoku_rows"
            )

        for c in range(n):
            self.grid_frame.columnconfigure(
                c,
                weight=1,
                uniform="sudoku_columns"
            )

        for r in range(n):
            for c in range(n):

                top = 1
                bottom = 1
                left = 1
                right = 1

                if r % self.box_size == 0:
                    top = 2

                if c % self.box_size == 0:
                    left = 2

                if (r + 1) % self.box_size == 0:
                    bottom = 2

                if (c + 1) % self.box_size == 0:
                    right = 2

                cell_frame = tk.Frame(
                    self.grid_frame,
                    bg=self.GRID
                )

                cell_frame.grid(
                    row=r,
                    column=c,
                    sticky="nsew",
                    padx=(left, right),
                    pady=(top, bottom)
                )

                value = self.puzzle[r][c]

                entry = tk.Entry(
                    cell_frame,
                    justify="center",
                    relief="flat",
                    bd=0,
                    highlightthickness=1,
                    highlightbackground=self.GRID,
                    highlightcolor=self.BLUE,
                    bg=self.FIXED_BG if value else self.CELL,
                    fg=self.TEXT,
                    insertbackground=self.TEXT,
                    font=("Helvetica Neue", 20),
                    disabledbackground=self.FIXED_BG,
                    disabledforeground=self.TEXT
                )

                entry.pack(
                    fill="both",
                    expand=True
                )

                if value:
                    entry.insert(
                        0,
                        self.value_to_symbol(value)
                    )
                    entry.configure(
                        state="disabled"
                    )

                entry.bind(
                    "<KeyPress>",
                    lambda event, rr=r, cc=c:
                    self.handle_key(event, rr, cc)
                )

                entry.bind(
                    "<Command-z>",
                    lambda event, rr=r, cc=c:
                    self.undo_and_break(event, rr, cc)
                )

                entry.bind(
                    "<Command-Z>",
                    lambda event, rr=r, cc=c:
                    self.undo_and_break(event, rr, cc)
                )

                entry.bind(
                    "<Control-z>",
                    lambda event, rr=r, cc=c:
                    self.undo_and_break(event, rr, cc)
                )

                entry.bind(
                    "<Control-Z>",
                    lambda event, rr=r, cc=c:
                    self.undo_and_break(event, rr, cc)
                )

                entry.bind(
                    "<FocusIn>",
                    lambda event, rr=r, cc=c:
                    self.on_focus_in(rr, cc)
                )

                entry.bind(
                    "<FocusOut>",
                    lambda event, rr=r, cc=c:
                    self.on_focus_out(rr, cc)
                )

                entry.bind(
                    "<Button-1>",
                    lambda event, rr=r, cc=c:
                    self.select_cell(rr, cc)
                )

                self.entries[(r, c)] = entry

        self.grid_frame.update_idletasks()
        self.resize_grid()

        self.root.after_idle(
            self.update_font_sizes
        )

        self.select_first_editable()

    # ============================================================
    # VELIKOST MREŽE
    # ============================================================

    def resize_grid(self, event=None):
        if self.grid_frame is None:
            return

        width = self.card.winfo_width()
        height = self.card.winfo_height()

        if width <= 1 or height <= 1:
            return

        side = int(min(width, height) * 0.90)

        self.grid_frame.place(
            relx=0.5,
            rely=0.5,
            anchor="center",
            width=side,
            height=side
        )

        self.update_font_sizes()

    def update_font_sizes(self):
        if not self.entries or self.grid_frame is None:
            return

        side = min(
            self.grid_frame.winfo_width(),
            self.grid_frame.winfo_height()
        )

        if side <= 1:
            return

        cell_size = side / self.size

        font_size = max(
            8,
            int(cell_size * 0.62)
        )

        if self.size == 4:
            font_size = min(font_size, 55)
        elif self.size == 9:
            font_size = min(font_size, 38)
        else:
            font_size = min(font_size, 23)

        font = (
            "Helvetica Neue",
            font_size
        )

        for entry in self.entries.values():
            entry.configure(font=font)

    # ============================================================
    # SIMBOLI
    # ============================================================

    def allowed_symbols(self):
        if self.size <= 9:
            return {
                str(i): i
                for i in range(1, self.size + 1)
            }

        symbols = {
            str(i): i
            for i in range(1, 10)
        }

        for i, letter in enumerate(
            "ABCDEFG",
            start=10
        ):
            symbols[letter] = i

        return symbols

    def value_to_symbol(self, value):
        if value <= 9:
            return str(value)

        return chr(
            ord("A") + value - 10
        )

    # ============================================================
    # TIPKE
    # ============================================================

    def handle_key(self, event, r, c):
        if self.puzzle[r][c] != 0:
            return "break"

        key = event.keysym

        # Premikanje
        if key in (
            "Left",
            "Right",
            "Up",
            "Down"
        ):
            self.move_selection(
                r,
                c,
                key
            )
            return "break"

        # Preverjanje
        if key == "Return":
            self.check_solution()
            return "break"

        # Označevanje
        if key.lower() == "m":
            self.toggle_marker(
                r,
                c
            )
            return "break"

        # Brisanje
        if key in (
            "BackSpace",
            "Delete"
        ):
            self.save_undo_state()

            self.entries[(r, c)].delete(
                0,
                "end"
            )

            self.mistake_cells.discard(
                (r, c)
            )

            self.refresh_cell_colors()
            return "break"

        # Vnos številk / črk
        symbol = event.char.upper()

        allowed = self.allowed_symbols()

        if symbol in allowed:
            self.save_undo_state()

            entry = self.entries[(r, c)]

            entry.delete(
                0,
                "end"
            )

            entry.insert(
                0,
                symbol
            )

            self.marked_cells.discard(
                (r, c)
            )

            self.mistake_cells.discard(
                (r, c)
            )

            self.refresh_cell_colors()

            return "break"

        return "break"

    # ============================================================
    # PREMIKANJE
    # ============================================================

    def move_selection(self, r, c, direction):
        dr = 0
        dc = 0

        if direction == "Left":
            dc = -1
        elif direction == "Right":
            dc = 1
        elif direction == "Up":
            dr = -1
        elif direction == "Down":
            dr = 1

        nr = r + dr
        nc = c + dc

        while (
            0 <= nr < self.size
            and 0 <= nc < self.size
        ):
            if self.puzzle[nr][nc] == 0:
                self.select_cell(
                    nr,
                    nc
                )
                return

            nr += dr
            nc += dc

    def select_first_editable(self):
        for r in range(self.size):
            for c in range(self.size):
                if self.puzzle[r][c] == 0:
                    self.select_cell(r, c)
                    return

    def select_cell(self, r, c):
        if self.puzzle[r][c] != 0:
            return

        self.selected_cell = (r, c)

        entry = self.entries[(r, c)]

        entry.focus_set()

        try:
            entry.icursor("end")
        except Exception:
            pass

        self.refresh_cell_colors()

    # ============================================================
    # FOKUS
    # ============================================================

    def on_focus_in(self, r, c):
        if self.puzzle[r][c] == 0:
            self.selected_cell = (r, c)

        self.refresh_cell_colors()

        self.root.after(
            120,
            lambda: self.keep_focus_outline(r, c)
        )

    def on_focus_out(self, r, c):
        self.refresh_cell_colors()

    def keep_focus_outline(self, r, c):
        if self.selected_cell == (r, c):
            self.refresh_cell_colors()

    # ============================================================
    # OZNAČEVANJE
    # ============================================================

    def global_m(self, event):
        if self.selected_cell is not None:
            self.toggle_marker()

    def toggle_marker(self, r=None, c=None):
        if r is None or c is None:
            if self.selected_cell is None:
                return

            r, c = self.selected_cell

        if self.puzzle[r][c] != 0:
            return

        self.save_undo_state()

        cell = (r, c)

        if cell in self.marked_cells:
            self.marked_cells.remove(cell)
        else:
            self.marked_cells.add(cell)

        self.refresh_cell_colors()

    # ============================================================
    # BARVE CELIC
    # ============================================================

    def refresh_cell_colors(self):
        for (r, c), entry in self.entries.items():

            if self.puzzle[r][c] != 0:
                entry.configure(
                    bg=self.FIXED_BG,
                    disabledbackground=self.FIXED_BG,
                    disabledforeground=self.TEXT
                )
                continue

            cell = (r, c)

            if cell in self.mistake_cells:
                bg = self.RED_BG
            elif cell in self.marked_cells:
                bg = self.YELLOW
            else:
                bg = self.CELL

            active = (
                self.selected_cell == cell
                and entry.focus_get() == entry
            )

            entry.configure(
                bg=bg,
                highlightbackground=(
                    self.BLUE
                    if active
                    else self.GRID
                ),
                highlightcolor=self.BLUE,
                highlightthickness=2 if active else 1
            )

    # ============================================================
    # RAZVELJAVI
    # ============================================================

    def save_undo_state(self):
        state = {}

        for cell, entry in self.entries.items():
            if self.puzzle[cell[0]][cell[1]] == 0:
                state[cell] = entry.get()

        self.undo_stack.append(
            (
                state,
                set(self.marked_cells),
                set(self.mistake_cells)
            )
        )

        if len(self.undo_stack) > 100:
            self.undo_stack.pop(0)

    def undo(self):
        if not self.undo_stack:
            return

        state, marked, mistakes = self.undo_stack.pop()

        for cell, value in state.items():
            entry = self.entries.get(cell)

            if entry is not None:
                entry.delete(
                    0,
                    "end"
                )

                if value:
                    entry.insert(
                        0,
                        value
                    )

        self.marked_cells = set(marked)
        self.mistake_cells = set(mistakes)

        self.refresh_cell_colors()

    def undo_and_break(self, event, r, c):
        self.undo()
        return "break"

    # ============================================================
    # PREVERJANJE
    # ============================================================

    def check_solution(self):
        incomplete = False
        mistakes = []

        for r in range(self.size):
            for c in range(self.size):

                if self.puzzle[r][c] != 0:
                    continue

                value = self.entries[(r, c)].get().strip()

                if not value:
                    incomplete = True
                    continue

                allowed = self.allowed_symbols()

                if value.upper() not in allowed:
                    mistakes.append((r, c))
                    continue

                number = allowed[value.upper()]

                if number != self.solution[r][c]:
                    mistakes.append((r, c))

        if incomplete:
            messagebox.showinfo(
                "Sudoku",
                "Sudoku še ni v celoti izpolnjen."
            )
            return

        if not mistakes:
            self.mistake_cells.clear()
            self.refresh_cell_colors()

            # CUSTOM SUCCESS WINDOW
            self.show_success_popup()

            return

        answer = messagebox.askyesno(
            "Sudoku",
            f"Najdenih napak: {len(mistakes)}.\n\n"
            "Ali želiš, da označim napačne celice?"
        )

        if answer:
            self.mistake_cells = set(mistakes)
            self.refresh_cell_colors()

            messagebox.showinfo(
                "Sudoku",
                "Napačne celice so označene."
            )

    # ============================================================
    # CUSTOM SUCCESS POPUP
    # ============================================================

    def show_success_popup(self):
        popup = tk.Toplevel(self.root)

        popup.title("Sudoku")
        popup.geometry("390x300")
        popup.minsize(350, 260)
        popup.resizable(False, False)

        popup.configure(
            bg=self.BG
        )

        # macOS-style okvir
        container = tk.Frame(
            popup,
            bg=self.BG
        )
        container.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=22
        )

        # Velik kljukica
        check = tk.Label(
            container,
            text="✓",
            font=("Helvetica Neue", 64, "bold"),
            bg=self.BG,
            fg=self.BLUE
        )
        check.pack(
            pady=(5, 0)
        )

        title = tk.Label(
            container,
            text="Čestitke!",
            font=("Helvetica Neue", 24, "bold"),
            bg=self.BG,
            fg=self.TEXT
        )
        title.pack(
            pady=(0, 5)
        )

        text = tk.Label(
            container,
            text="Sudoku je pravilno rešen!",
            font=("Helvetica Neue", 15),
            bg=self.BG,
            fg=self.SECONDARY
        )
        text.pack(
            pady=(0, 20)
        )

        close_button = ttk.Button(
            container,
            text="V redu",
            style="Sudoku.TButton",
            command=popup.destroy
        )
        close_button.pack()

        popup.transient(self.root)
        popup.grab_set()

        popup.update_idletasks()

        # Centriranje glede na glavno okno
        root_x = self.root.winfo_rootx()
        root_y = self.root.winfo_rooty()

        root_w = self.root.winfo_width()
        root_h = self.root.winfo_height()

        popup_w = popup.winfo_width()
        popup_h = popup.winfo_height()

        x = root_x + (root_w - popup_w) // 2
        y = root_y + (root_h - popup_h) // 2

        popup.geometry(
            f"+{x}+{y}"
        )

        close_button.focus_set()

        popup.bind(
            "<Return>",
            lambda event: popup.destroy()
        )

        popup.bind(
            "<Escape>",
            lambda event: popup.destroy()
        )

    # ============================================================
    # PRIKAŽI NAPAKE
    # ============================================================

    def show_mistakes(self):
        answer = messagebox.askyesno(
            "Prikaži napake",
            "Ali želiš označiti napačne celice?"
        )

        if not answer:
            return

        mistakes = []

        allowed = self.allowed_symbols()

        for r in range(self.size):
            for c in range(self.size):

                if self.puzzle[r][c] != 0:
                    continue

                value = self.entries[(r, c)].get().strip()

                if not value:
                    continue

                if value.upper() not in allowed:
                    mistakes.append((r, c))
                    continue

                number = allowed[value.upper()]

                if number != self.solution[r][c]:
                    mistakes.append((r, c))

        self.mistake_cells = set(mistakes)

        self.refresh_cell_colors()

        if not mistakes:
            messagebox.showinfo(
                "Napake",
                "Ni najdenih napak."
            )
        else:
            messagebox.showwarning(
                "Napake",
                f"Najdenih napak: {len(mistakes)}."
            )

    # ============================================================
    # MENJAVA VELIKOSTI
    # ============================================================

    def change_size(self, value):
        mapping = {
            "4 × 4": 4,
            "9 × 9": 9,
            "16 × 16": 16
        }

        new_size = mapping[value]

        if new_size == self.size:
            return

        if self.has_user_progress():
            answer = messagebox.askyesno(
                "Sprememba velikosti",
                "Ta Sudoku je že delno rešen.\n\n"
                f"Ali želiš začeti novo igro z velikostjo {value}?"
            )

            if not answer:
                self.size_var.set(
                    f"{self.size} × {self.size}"
                )
                return

        self.size = new_size

        self.marked_cells.clear()
        self.mistake_cells.clear()
        self.undo_stack.clear()
        self.selected_cell = None

        self.generate_sudoku()
        self.create_grid()

        self.root.after_idle(
            self.resize_grid
        )

        self.root.after(
            50,
            self.update_font_sizes
        )

    # ============================================================
    # POMOČ
    # ============================================================

    def show_help(self):
        window = tk.Toplevel(self.root)

        window.title("Kako igrati Sudoku")
        window.geometry("520x570")
        window.minsize(460, 500)

        window.configure(
            bg=self.BG
        )

        title = tk.Label(
            window,
            text="Kako igrati Sudoku",
            font=("Helvetica Neue", 26, "bold"),
            bg=self.BG,
            fg=self.TEXT
        )
        title.pack(
            anchor="w",
            padx=28,
            pady=(25, 2)
        )

        subtitle = tk.Label(
            window,
            text="Pravila in bližnjice",
            font=("Helvetica Neue", 14),
            bg=self.BG,
            fg=self.SECONDARY
        )
        subtitle.pack(
            anchor="w",
            padx=28,
            pady=(0, 18)
        )

        text_frame = tk.Frame(
            window,
            bg=self.BG
        )
        text_frame.pack(
            fill="both",
            expand=True,
            padx=28
        )

        sections = [
            (
                "Osnovna pravila",
                "Vsaka vrstica, vsak stolpec in vsak označen blok "
                "mora vsebovati vsako številko samo enkrat."
            ),
            (
                "Premikanje",
                "Uporabi puščice na tipkovnici za premikanje med "
                "praznimi celicami. Aktivna celica ima moder rob."
            ),
            (
                "Vnos",
                "Vnesi številko s tipkovnico. Pri 16 × 16 so poleg "
                "števil 1–9 uporabljene tudi črke A–G."
            ),
            (
                "Označevanje",
                "Pritisni M ali gumb »Označi celico«, da trenutno "
                "celico obarvaš kot opomnik."
            ),
            (
                "Preverjanje",
                "Pritisni Enter ali gumb »Preveri«. Če je Sudoku "
                "popolnoma izpolnjen, se preveri celotna rešitev."
            ),
            (
                "Razveljavi",
                "⌘Z na Macu oziroma Ctrl+Z na drugih sistemih "
                "razveljavi zadnjo spremembo."
            ),
            (
                "Nova igra",
                "Če je trenutna igra že delno rešena, te aplikacija "
                "pred začetkom nove igre vpraša za potrditev."
            )
        ]

        for heading, description in sections:
            heading_label = tk.Label(
                text_frame,
                text=heading,
                font=("Helvetica Neue", 15, "bold"),
                bg=self.BG,
                fg=self.TEXT,
                anchor="w"
            )
            heading_label.pack(
                fill="x",
                pady=(0, 2)
            )

            description_label = tk.Label(
                text_frame,
                text=description,
                font=("Helvetica Neue", 12),
                bg=self.BG,
                fg=self.SECONDARY,
                justify="left",
                anchor="w",
                wraplength=450
            )
            description_label.pack(
                fill="x",
                pady=(0, 12)
            )

        close_button = ttk.Button(
            window,
            text="Zapri",
            style="Sudoku.TButton",
            command=window.destroy
        )
        close_button.pack(
            pady=(5, 20)
        )

        window.transient(self.root)
        window.grab_set()

    # ============================================================
    # O APLIKACIJI
    # ============================================================

    def show_about(self):
        messagebox.showinfo(
            "O Sudokuju",
            "Sudoku\n\n"
            "Preprosta Sudoku igra z načini "
            "4 × 4, 9 × 9 in 16 × 16.\n\n"
            "Podpira temni način, označevanje celic, "
            "razveljavitev in preverjanje rešitev."
        )


# ================================================================
# ZAGON
# ================================================================

if __name__ == "__main__":
    root = tk.Tk()
    app = SudokuApp(root)
    root.mainloop()
