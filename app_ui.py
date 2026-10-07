"""
AutoMacro Studio Pro - Interface Gráfica Moderna
Autor: Antigravity
Data: 2026 - AutoMacro Studio Pro
"""

import os
import sys
import time
import json
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from pynput import mouse, keyboard

# Diretório base
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MACROS_DIR = os.path.join(BASE_DIR, "macros")
os.makedirs(MACROS_DIR, exist_ok=True)
DEFAULT_MACRO_PATH = os.path.join(MACROS_DIR, "macro_padrao.json")

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class MacroCore:
    """Motor de gravação e reprodução com precisão temporal milimétrica."""
    def __init__(self):
        self.events = []
        self.is_recording = False
        self.is_playing = False
        self.abort_requested = False
        self.start_time = 0.0

        self.mouse_controller = mouse.Controller()
        self.keyboard_controller = keyboard.Controller()

        self.mouse_listener = None
        self.keyboard_listener = None
        
        # Filtros
        self.record_moves = True
        self.record_clicks = True
        self.record_scrolls = True
        self.record_keys = True

        # Estatísticas
        self.stats = {"moves": 0, "clicks": 0, "scrolls": 0, "keys": 0, "duration": 0.0}

    def serialize_key(self, key):
        if isinstance(key, keyboard.Key):
            return {"type": "special", "name": key.name}
        elif hasattr(key, "char") and key.char is not None:
            return {"type": "char", "char": key.char}
        elif hasattr(key, "vk") and key.vk is not None:
            return {"type": "vk", "vk": key.vk}
        else:
            return {"type": "unknown", "str": str(key)}

    def deserialize_key(self, data):
        try:
            if data["type"] == "special":
                return getattr(keyboard.Key, data["name"], None)
            elif data["type"] == "char":
                return data["char"]
            elif data["type"] == "vk":
                return keyboard.KeyCode.from_vk(data["vk"])
        except Exception:
            pass
        return None

    def on_move(self, x, y):
        if not self.is_recording or not self.record_moves:
            return
        t = time.time() - self.start_time
        self.events.append({"type": "move", "time": t, "x": x, "y": y})
        self.stats["moves"] += 1

    def on_click(self, x, y, button, pressed):
        if not self.is_recording or not self.record_clicks:
            return
        t = time.time() - self.start_time
        self.events.append({
            "type": "click",
            "time": t,
            "x": x,
            "y": y,
            "button": button.name,
            "pressed": pressed
        })
        if pressed:
            self.stats["clicks"] += 1

    def on_scroll(self, x, y, dx, dy):
        if not self.is_recording or not self.record_scrolls:
            return
        t = time.time() - self.start_time
        self.events.append({
            "type": "scroll",
            "time": t,
            "x": x,
            "y": y,
            "dx": dx,
            "dy": dy
        })
        self.stats["scrolls"] += 1

    def on_press(self, key):
        if not self.is_recording or not self.record_keys:
            return
        if key in (keyboard.Key.f6, keyboard.Key.f7):
            return
        t = time.time() - self.start_time
        self.events.append({"type": "key_press", "time": t, "key": self.serialize_key(key)})
        self.stats["keys"] += 1

    def on_release(self, key):
        if not self.is_recording or not self.record_keys:
            return
        if key in (keyboard.Key.f6, keyboard.Key.f7):
            return
        t = time.time() - self.start_time
        self.events.append({"type": "key_release", "time": t, "key": self.serialize_key(key)})

    def start_recording(self):
        self.events = []
        self.stats = {"moves": 0, "clicks": 0, "scrolls": 0, "keys": 0, "duration": 0.0}
        self.is_recording = True
        self.start_time = time.time()

        self.mouse_listener = mouse.Listener(
            on_move=self.on_move,
            on_click=self.on_click,
            on_scroll=self.on_scroll
        )
        self.keyboard_listener = keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release
        )

        self.mouse_listener.start()
        self.keyboard_listener.start()

    def stop_recording(self):
        if not self.is_recording:
            return
        self.is_recording = False
        self.stats["duration"] = time.time() - self.start_time
        if self.mouse_listener and self.mouse_listener.is_alive():
            self.mouse_listener.stop()
        if self.keyboard_listener and self.keyboard_listener.is_alive():
            self.keyboard_listener.stop()

    def save_macro(self, filepath):
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump({
                "version": "1.0",
                "stats": self.stats,
                "events": self.events
            }, f, indent=2)

    def load_macro(self, filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                self.events = data
                self.stats = {"moves": 0, "clicks": 0, "scrolls": 0, "keys": 0, "duration": 0.0}
            else:
                self.events = data.get("events", [])
                self.stats = data.get("stats", {"moves": 0, "clicks": 0, "scrolls": 0, "keys": 0, "duration": 0.0})


class AutoMacroApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.core = MacroCore()
        self.current_filepath = DEFAULT_MACRO_PATH

        # Configuração da Janela
        self.title("AutoMacro Studio Pro — Gravador & Repetidor")
        self.geometry("780x680")
        self.minsize(740, 640)
        self.configure(fg_color="#0f1117")

        # Variáveis de Estado
        self.status_text = tk.StringVar(value="Pronto")
        self.status_color = tk.StringVar(value="#10b981") # Verde
        self.timer_text = tk.StringVar(value="00:00:00")
        self.actions_count_text = tk.StringVar(value="0 ações registradas")
        
        # Variáveis de Configuração
        self.var_record_mouse = tk.BooleanVar(value=True)
        self.var_record_moves = tk.BooleanVar(value=True)
        self.var_record_keys = tk.BooleanVar(value=True)
        self.var_infinite_loop = tk.BooleanVar(value=False)
        self.var_repetitions = tk.StringVar(value="1")
        self.var_speed = tk.DoubleVar(value=1.0)
        self.var_delay_loops = tk.StringVar(value="0.5")
        self.var_countdown = tk.IntVar(value=3)
        self.var_always_on_top = tk.BooleanVar(value=False)

        # Hotkeys Listener Global
        self.global_hotkey_listener = None
        self.init_global_hotkeys()

        # Construção da Interface
        self.build_ui()

        # Tentar carregar macro padrão se existir
        if os.path.exists(DEFAULT_MACRO_PATH):
            try:
                self.core.load_macro(DEFAULT_MACRO_PATH)
                self.update_stats_display()
            except Exception:
                pass

        # Timer de atualização visual
        self.update_timer_loop()

    def init_global_hotkeys(self):
        """Monitora F6, F7 e ESC globalmente no sistema."""
        def on_key_press(key):
            try:
                if key == keyboard.Key.f6:
                    self.after(0, self.toggle_recording)
                elif key == keyboard.Key.f7:
                    self.after(0, self.toggle_playback)
                elif key == keyboard.Key.esc:
                    if self.core.is_playing:
                        self.core.abort_requested = True
                        self.after(0, self.on_emergency_stop)
            except Exception:
                pass

        self.global_hotkey_listener = keyboard.Listener(on_press=on_key_press)
        self.global_hotkey_listener.daemon = True
        self.global_hotkey_listener.start()

    def build_ui(self):
        # 1. Top Header Bar
        header = ctk.CTkFrame(self, fg_color="#181b22", corner_radius=12, height=75)
        header.pack(fill="x", padx=16, pady=(16, 10))
        header.pack_propagate(False)

        title_container = ctk.CTkFrame(header, fg_color="transparent")
        title_container.pack(side="left", padx=18, pady=12)

        title_label = ctk.CTkLabel(
            title_container, 
            text="⚡ AutoMacro Studio Pro", 
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color="#ffffff"
        )
        title_label.pack(anchor="w")

        subtitle = ctk.CTkLabel(
            title_container, 
            text="Gravador e Repetidor com Precisão Milimétrica de Tempo", 
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="#9ca3af"
        )
        subtitle.pack(anchor="w")

        # Status Badge & Top Controls
        status_container = ctk.CTkFrame(header, fg_color="transparent")
        status_container.pack(side="right", padx=18)

        self.btn_pin = ctk.CTkSwitch(
            status_container, 
            text="Sempre no Topo", 
            variable=self.var_always_on_top,
            command=self.toggle_always_on_top,
            font=ctk.CTkFont(size=12),
            progress_color="#3b82f6"
        )
        self.btn_pin.pack(side="right", padx=(15, 0))

        self.status_badge = ctk.CTkLabel(
            status_container,
            textvariable=self.status_text,
            fg_color="#064e3b",
            text_color="#34d399",
            corner_radius=20,
            padx=14,
            pady=4,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.status_badge.pack(side="right")

        # 2. Main Content Grid
        main_grid = ctk.CTkFrame(self, fg_color="transparent")
        main_grid.pack(fill="both", expand=True, padx=16, pady=6)
        main_grid.columnconfigure(0, weight=1)
        main_grid.columnconfigure(1, weight=1)
        main_grid.rowconfigure(0, weight=1)

        # Card Esquerdo: Gravação
        self.build_recording_card(main_grid)

        # Card Direito: Reprodução
        self.build_playback_card(main_grid)

        # 3. Bottom Dashboard (Estatísticas, Arquivos & Logs)
        self.build_bottom_panel()

    def build_recording_card(self, parent):
        card = ctk.CTkFrame(parent, fg_color="#181b22", corner_radius=14, border_width=1, border_color="#262b36")
        card.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=0)

        # Título do Card
        lbl = ctk.CTkLabel(
            card, 
            text="🎙️ Gravação", 
            font=ctk.CTkFont(family="Segoe UI", size=17, weight="bold"),
            text_color="#f3f4f6"
        )
        lbl.pack(anchor="w", padx=18, pady=(16, 4))

        sub = ctk.CTkLabel(
            card, 
            text="Atalho global de início e fim: F6", 
            font=ctk.CTkFont(size=12),
            text_color="#6b7280"
        )
        sub.pack(anchor="w", padx=18, pady=(0, 14))

        # Botão Principal de Gravar
        self.btn_record = ctk.CTkButton(
            card,
            text="🔴 Iniciar Gravação (F6)",
            font=ctk.CTkFont(size=15, weight="bold"),
            height=46,
            corner_radius=10,
            fg_color="#dc2626",
            hover_color="#b91c1c",
            command=self.toggle_recording
        )
        self.btn_record.pack(fill="x", padx=18, pady=8)

        # Opções de Gravação
        opts_frame = ctk.CTkFrame(card, fg_color="#20242e", corner_radius=10)
        opts_frame.pack(fill="both", expand=True, padx=18, pady=(10, 16))

        opt_title = ctk.CTkLabel(
            opts_frame, 
            text="O que capturar:", 
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#d1d5db"
        )
        opt_title.pack(anchor="w", padx=14, pady=(10, 6))

        c1 = ctk.CTkCheckBox(opts_frame, text="Cliques & Rolagem do Mouse", variable=self.var_record_mouse)
        c1.pack(anchor="w", padx=14, pady=5)

        c2 = ctk.CTkCheckBox(opts_frame, text="Movimento contínuo do Mouse", variable=self.var_record_moves)
        c2.pack(anchor="w", padx=14, pady=5)

        c3 = ctk.CTkCheckBox(opts_frame, text="Teclas digitadas (Teclado)", variable=self.var_record_keys)
        c3.pack(anchor="w", padx=14, pady=5)

        # Contagem Regressiva
        cd_frame = ctk.CTkFrame(opts_frame, fg_color="transparent")
        cd_frame.pack(fill="x", padx=14, pady=(12, 10))

        ctk.CTkLabel(cd_frame, text="Contagem regressiva:", font=ctk.CTkFont(size=12)).pack(side="left")
        cd_spin = ctk.CTkOptionMenu(
            cd_frame, 
            values=["0s", "1s", "2s", "3s", "5s"],
            width=75,
            height=26,
            command=self.on_countdown_change
        )
        cd_spin.set("3s")
        cd_spin.pack(side="right")

    def build_playback_card(self, parent):
        card = ctk.CTkFrame(parent, fg_color="#181b22", corner_radius=14, border_width=1, border_color="#262b36")
        card.grid(row=0, column=1, sticky="nsew", padx=(8, 0), pady=0)

        # Título do Card
        lbl = ctk.CTkLabel(
            card, 
            text="▶️ Reprodução", 
            font=ctk.CTkFont(family="Segoe UI", size=17, weight="bold"),
            text_color="#f3f4f6"
        )
        lbl.pack(anchor="w", padx=18, pady=(16, 4))

        sub = ctk.CTkLabel(
            card, 
            text="Atalho: F7 | Parada de Emergência: ESC", 
            font=ctk.CTkFont(size=12),
            text_color="#6b7280"
        )
        sub.pack(anchor="w", padx=18, pady=(0, 14))

        # Botão Principal de Reproduzir
        self.btn_play = ctk.CTkButton(
            card,
            text="▶️ Reproduzir Macro (F7)",
            font=ctk.CTkFont(size=15, weight="bold"),
            height=46,
            corner_radius=10,
            fg_color="#2563eb",
            hover_color="#1d4ed8",
            command=self.toggle_playback
        )
        self.btn_play.pack(fill="x", padx=18, pady=8)

        # Configurações de Reprodução
        opts_frame = ctk.CTkFrame(card, fg_color="#20242e", corner_radius=10)
        opts_frame.pack(fill="both", expand=True, padx=18, pady=(10, 16))

        # Repetições / Loop
        rep_frame = ctk.CTkFrame(opts_frame, fg_color="transparent")
        rep_frame.pack(fill="x", padx=14, pady=(12, 6))

        ctk.CTkLabel(rep_frame, text="Repetições:", font=ctk.CTkFont(size=13, weight="bold")).pack(side="left")

        self.rep_entry = ctk.CTkEntry(rep_frame, textvariable=self.var_repetitions, width=60, height=28)
        self.rep_entry.pack(side="right")

        chk_inf = ctk.CTkCheckBox(
            opts_frame, 
            text="♾️ Loop Infinito (executa sem parar)", 
            variable=self.var_infinite_loop,
            command=self.toggle_infinite_loop
        )
        chk_inf.pack(anchor="w", padx=14, pady=(2, 10))

        # Velocidade
        spd_header = ctk.CTkFrame(opts_frame, fg_color="transparent")
        spd_header.pack(fill="x", padx=14, pady=(6, 2))
        ctk.CTkLabel(spd_header, text="Velocidade:", font=ctk.CTkFont(size=13, weight="bold")).pack(side="left")
        self.lbl_speed_val = ctk.CTkLabel(spd_header, text="1.0x (Tempo Real)", text_color="#60a5fa", font=ctk.CTkFont(size=12, weight="bold"))
        self.lbl_speed_val.pack(side="right")

        self.speed_slider = ctk.CTkSlider(
            opts_frame, 
            from_=0.25,  # type: ignore[arg-type]
            to=4.0,  # type: ignore[arg-type] 
            number_of_steps=15, 
            variable=self.var_speed,
            command=self.on_speed_slider_change
        )
        self.speed_slider.pack(fill="x", padx=14, pady=(0, 10))

        # Intervalo entre loops
        int_frame = ctk.CTkFrame(opts_frame, fg_color="transparent")
        int_frame.pack(fill="x", padx=14, pady=(4, 10))
        ctk.CTkLabel(int_frame, text="Pausa entre ciclos (s):", font=ctk.CTkFont(size=12)).pack(side="left")
        self.delay_entry = ctk.CTkEntry(int_frame, textvariable=self.var_delay_loops, width=60, height=26)
        self.delay_entry.pack(side="right")

    def build_bottom_panel(self):
        panel = ctk.CTkFrame(self, fg_color="#181b22", corner_radius=12)
        panel.pack(fill="x", padx=16, pady=(4, 16))

        # Barra de Progresso / Contagem de Ações
        top_info = ctk.CTkFrame(panel, fg_color="transparent")
        top_info.pack(fill="x", padx=16, pady=(12, 6))

        lbl_dur = ctk.CTkLabel(top_info, text="⏱️ Cronômetro: ", font=ctk.CTkFont(size=12, weight="bold"), text_color="#9ca3af")
        lbl_dur.pack(side="left")

        self.lbl_timer = ctk.CTkLabel(top_info, textvariable=self.timer_text, font=ctk.CTkFont(family="Consolas", size=14, weight="bold"), text_color="#60a5fa")
        self.lbl_timer.pack(side="left", padx=(0, 20))

        lbl_acts = ctk.CTkLabel(top_info, textvariable=self.actions_count_text, font=ctk.CTkFont(size=12), text_color="#9ca3af")
        lbl_acts.pack(side="left")

        # Barra de progresso visual de replay
        self.progress_bar = ctk.CTkProgressBar(panel, height=8, corner_radius=4, progress_color="#3b82f6")
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x", padx=16, pady=4)

        # Botões de Arquivo (Salvar, Carregar, Abrir Pasta)
        file_bar = ctk.CTkFrame(panel, fg_color="transparent")
        file_bar.pack(fill="x", padx=16, pady=(8, 12))

        btn_save = ctk.CTkButton(
            file_bar, 
            text="💾 Salvar Como...", 
            width=120, 
            height=30,
            fg_color="#334155", 
            hover_color="#475569",
            command=self.save_macro_dialog
        )
        btn_save.pack(side="left", padx=(0, 8))

        btn_load = ctk.CTkButton(
            file_bar, 
            text="📂 Carregar Arquivo", 
            width=130, 
            height=30,
            fg_color="#334155", 
            hover_color="#475569",
            command=self.load_macro_dialog
        )
        btn_load.pack(side="left", padx=(0, 8))

        btn_folder = ctk.CTkButton(
            file_bar, 
            text="📁 Abrir Pasta de Macros", 
            width=150, 
            height=30,
            fg_color="#1e293b", 
            hover_color="#334155",
            command=self.open_macros_folder
        )
        btn_folder.pack(side="left")

        self.lbl_cur_file = ctk.CTkLabel(
            file_bar, 
            text="Arquivo: macro_padrao.json", 
            font=ctk.CTkFont(size=11),
            text_color="#64748b"
        )
        self.lbl_cur_file.pack(side="right")

    # ==========================
    # LÓGICA DE CONTROLE
    # ==========================
    def toggle_always_on_top(self):
        self.attributes("-topmost", self.var_always_on_top.get())

    def on_countdown_change(self, choice):
        val = int(choice.replace("s", ""))
        self.var_countdown.set(val)

    def on_speed_slider_change(self, val):
        val = round(val, 2)
        if val == 1.0:
            txt = "1.0x (Tempo Real)"
        else:
            txt = f"{val}x {'(Acelerado)' if val > 1.0 else '(Desacelerado)'}"
        self.lbl_speed_val.configure(text=txt)

    def toggle_infinite_loop(self):
        if self.var_infinite_loop.get():
            self.rep_entry.configure(state="disabled")
        else:
            self.rep_entry.configure(state="normal")

    def set_status(self, text, bg_color, fg_color):
        self.status_text.set(text)
        self.status_badge.configure(fg_color=bg_color, text_color=fg_color)

    def update_stats_display(self):
        ev_count = len(self.core.events)
        stats = self.core.stats
        dur = stats.get("duration", 0.0)
        mins, secs = divmod(int(dur), 60)
        self.timer_text.set(f"{mins:02d}:{secs:02d}:{int((dur % 1)*100):02d}")
        self.actions_count_text.set(
            f"{ev_count} ações ({stats.get('clicks', 0)} cliques, {stats.get('keys', 0)} teclas, {stats.get('moves', 0)} movs)"
        )

    def update_timer_loop(self):
        if self.core.is_recording:
            elapsed = time.time() - self.core.start_time
            mins, secs = divmod(int(elapsed), 60)
            ms = int((elapsed % 1) * 100)
            self.timer_text.set(f"{mins:02d}:{secs:02d}:{ms:02d}")
            self.actions_count_text.set(f"{len(self.core.events)} ações capturadas...")
        self.after(50, self.update_timer_loop)

    # ==========================
    # GRAVAÇÃO
    # ==========================
    def toggle_recording(self):
        if self.core.is_recording:
            self.stop_recording()
        else:
            if self.core.is_playing:
                return
            self.start_recording_thread()

    def start_recording_thread(self):
        cd = self.var_countdown.get()
        
        def run_countdown():
            for i in range(cd, 0, -1):
                self.set_status(f"Gravando em {i}s...", "#854d0e", "#fef08a")
                time.sleep(1)
            
            # Aplica filtros
            self.core.record_moves = self.var_record_moves.get()
            self.core.record_clicks = self.var_record_mouse.get()
            self.core.record_scrolls = self.var_record_mouse.get()
            self.core.record_keys = self.var_record_keys.get()

            self.core.start_recording()
            self.set_status("● GRAVANDO (F6 para parar)", "#7f1d1d", "#fca5a5")
            self.btn_record.configure(text="⏹️ Parar Gravação (F6)", fg_color="#991b1b")
            self.btn_play.configure(state="disabled")

        threading.Thread(target=run_countdown, daemon=True).start()

    def stop_recording(self):
        self.core.stop_recording()
        self.set_status("Pronto", "#064e3b", "#34d399")
        self.btn_record.configure(text="🔴 Iniciar Gravação (F6)", fg_color="#dc2626")
        self.btn_play.configure(state="normal")
        self.update_stats_display()

        # Salva automaticamente na macro padrão
        try:
            self.core.save_macro(self.current_filepath)
        except Exception as e:
            print(f"Erro ao salvar: {e}")

    # ==========================
    # REPRODUÇÃO
    # ==========================
    def toggle_playback(self):
        if self.core.is_playing:
            self.core.abort_requested = True
        else:
            if self.core.is_recording or not self.core.events:
                if not self.core.events:
                    messagebox.showinfo("Aviso", "Nenhuma gravação encontrada! Grave primeiro ou carregue um arquivo.")
                return
            self.start_playback_thread()

    def on_emergency_stop(self):
        self.set_status("⏹️ Interrompido (ESC)", "#7f1d1d", "#fca5a5")
        self.btn_play.configure(text="▶️ Reproduzir Macro (F7)", fg_color="#2563eb")
        self.btn_record.configure(state="normal")
        self.progress_bar.set(0)

    def start_playback_thread(self):
        try:
            reps = 0 if self.var_infinite_loop.get() else int(self.var_repetitions.get())
        except ValueError:
            reps = 1

        speed = float(self.var_speed.get())
        try:
            delay_loop = float(self.var_delay_loops.get())
        except ValueError:
            delay_loop = 0.5

        def run_playback():
            self.core.is_playing = True
            self.core.abort_requested = False
            self.btn_record.configure(state="disabled")
            self.btn_play.configure(text="⏹️ Parar Macro (ESC)", fg_color="#dc2626")

            total_loops = float("inf") if reps == 0 else reps
            current_loop = 0
            total_events = len(self.core.events)
            total_duration = self.core.events[-1]["time"] if total_events > 0 else 1.0

            try:
                while current_loop < total_loops and not self.core.abort_requested:
                    current_loop += 1
                    status_lbl = f"Reproduzindo (Loop {current_loop}{'' if reps == 0 else f'/{reps}'})"
                    self.set_status(status_lbl, "#1e3a8a", "#93c5fd")

                    start_t = time.time()
                    for idx, ev in enumerate(self.core.events):
                        if self.core.abort_requested:
                            break

                        target_time = ev["time"] / speed
                        elapsed = time.time() - start_t
                        wait_t = target_time - elapsed

                        if wait_t > 0:
                            end_wait = time.time() + wait_t
                            while time.time() < end_wait:
                                if self.core.abort_requested:
                                    break
                                time.sleep(min(0.005, max(0, end_wait - time.time())))

                        if self.core.abort_requested:
                            break

                        # Atualiza barra de progresso
                        prog = (ev["time"] / total_duration) if total_duration > 0 else 1.0
                        self.progress_bar.set(prog)

                        # Executa ação
                        etype = ev["type"]
                        if etype == "move":
                            self.core.mouse_controller.position = (ev["x"], ev["y"])
                        elif etype == "click":
                            self.core.mouse_controller.position = (ev["x"], ev["y"])
                            btn = getattr(mouse.Button, ev["button"], mouse.Button.left)
                            if ev["pressed"]:
                                self.core.mouse_controller.press(btn)
                            else:
                                self.core.mouse_controller.release(btn)
                        elif etype == "scroll":
                            self.core.mouse_controller.position = (ev["x"], ev["y"])
                            self.core.mouse_controller.scroll(ev["dx"], ev["dy"])
                        elif etype == "key_press":
                            k = self.core.deserialize_key(ev["key"])
                            if k:
                                try:
                                    self.core.keyboard_controller.press(k)
                                except Exception:
                                    pass
                        elif etype == "key_release":
                            k = self.core.deserialize_key(ev["key"])
                            if k:
                                try:
                                    self.core.keyboard_controller.release(k)
                                except Exception:
                                    pass

                    if current_loop < total_loops and not self.core.abort_requested and delay_loop > 0:
                        time.sleep(delay_loop)

            finally:
                self.core.is_playing = False
                self.progress_bar.set(0)
                if not self.core.abort_requested:
                    self.set_status("Pronto", "#064e3b", "#34d399")
                self.btn_play.configure(text="▶️ Reproduzir Macro (F7)", fg_color="#2563eb")
                self.btn_record.configure(state="normal")

        threading.Thread(target=run_playback, daemon=True).start()

    # ==========================
    # ARQUIVOS
    # ==========================
    def save_macro_dialog(self):
        if not self.core.events:
            messagebox.showinfo("Aviso", "Não há nenhuma gravação para salvar!")
            return
        f = filedialog.asksaveasfilename(
            initialdir=MACROS_DIR,
            title="Salvar Macro Como",
            defaultextension=".json",
            filetypes=[("Arquivos JSON", "*.json")]
        )
        if f:
            self.current_filepath = f
            self.core.save_macro(f)
            self.lbl_cur_file.configure(text=f"Arquivo: {os.path.basename(f)}")
            messagebox.showinfo("Sucesso", "Macro salva com sucesso!")

    def load_macro_dialog(self):
        f = filedialog.askopenfilename(
            initialdir=MACROS_DIR,
            title="Carregar Arquivo de Macro",
            filetypes=[("Arquivos JSON", "*.json")]
        )
        if f:
            try:
                self.core.load_macro(f)
                self.current_filepath = f
                self.lbl_cur_file.configure(text=f"Arquivo: {os.path.basename(f)}")
                self.update_stats_display()
                messagebox.showinfo("Sucesso", f"Macro carregada com sucesso ({len(self.core.events)} ações)!")
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao carregar macro: {e}")

    def open_macros_folder(self):
        os.startfile(MACROS_DIR)


if __name__ == "__main__":
    app = AutoMacroApp()
    app.mainloop()
