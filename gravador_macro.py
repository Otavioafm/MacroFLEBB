"""
Gravador e Repetidor de Teclado e Mouse
Autor: Antigravity
Data: 2026
"""

import os
import sys
import time
import json
from pynput import mouse, keyboard

ARQUIVO_GRAVACAO = "macro_gravada.json"

class MacroRecorderPlayer:
    def __init__(self, filename=ARQUIVO_GRAVACAO):
        self.filename = filename
        self.events = []
        self.is_recording = False
        self.is_playing = False
        self.abort_requested = False
        self.start_time = 0.0

        self.mouse_controller = mouse.Controller()
        self.keyboard_controller = keyboard.Controller()

        self.mouse_listener = None
        self.keyboard_listener = None

    # ==========================
    # SERIALIZAÇÃO DE TECLAS
    # ==========================
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

    # ==========================
    # LISTENERS DE GRAVAÇÃO
    # ==========================
    def on_move(self, x, y):
        if not self.is_recording:
            return
        t = time.time() - self.start_time
        self.events.append({
            "type": "mouse_move",
            "time": t,
            "x": x,
            "y": y
        })

    def on_click(self, x, y, button, pressed):
        if not self.is_recording:
            return
        t = time.time() - self.start_time
        self.events.append({
            "type": "mouse_click",
            "time": t,
            "x": x,
            "y": y,
            "button": button.name,
            "pressed": pressed
        })

    def on_scroll(self, x, y, dx, dy):
        if not self.is_recording:
            return
        t = time.time() - self.start_time
        self.events.append({
            "type": "mouse_scroll",
            "time": t,
            "x": x,
            "y": y,
            "dx": dx,
            "dy": dy
        })

    def on_press(self, key):
        if not self.is_recording:
            return
        # Tecla de atalho F6 para parar a gravação sem gravar o próprio F6
        if key == keyboard.Key.f6:
            return
        t = time.time() - self.start_time
        self.events.append({
            "type": "key_press",
            "time": t,
            "key": self.serialize_key(key)
        })

    def on_release(self, key):
        if not self.is_recording:
            return
        if key == keyboard.Key.f6:
            print("\n[!] Tecla F6 detectada. Encerrando gravação...")
            self.stop_recording()
            return False  # encerra listener
        t = time.time() - self.start_time
        self.events.append({
            "type": "key_release",
            "time": t,
            "key": self.serialize_key(key)
        })

    # ==========================
    # INICIAR / PARAR GRAVAÇÃO
    # ==========================
    def start_recording(self):
        self.events = []
        self.is_recording = True
        
        print("\n" + "="*50)
        print(" PREPARANDO PARA GRAVAR...")
        print(" A gravação começará em 3 segundos.")
        print(" Para PARAR a gravação a qualquer momento: Pressione F6")
        print("="*50)

        for i in range(3, 0, -1):
            print(f" Iniciando em {i}...")
            time.sleep(1)

        print("\n>>> GRAVANDO AGORA! (Faça seus movimentos de mouse e teclado) <<<")
        print(">>> Pressione [F6] quando terminar <<< \n")

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

        # Aguarda a finalização do teclado (quando apertar F6)
        self.keyboard_listener.join()
        if self.mouse_listener and self.mouse_listener.is_alive():
            self.mouse_listener.stop()

    def stop_recording(self):
        if not self.is_recording:
            return
        self.is_recording = False
        print(f"Gravação concluída! Total de ações gravadas: {len(self.events)}")
        self.save_to_file()

    def save_to_file(self):
        try:
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump(self.events, f, indent=2)
            print(f"[OK] Gravação salva com sucesso em '{self.filename}'!")
        except Exception as e:
            print(f"[ERRO] Falha ao salvar arquivo: {e}")

    def load_from_file(self):
        if not os.path.exists(self.filename):
            print(f"[AVISO] Nenhum arquivo '{self.filename}' encontrado.")
            return False
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                self.events = json.load(f)
            print(f"[OK] {len(self.events)} ações carregadas de '{self.filename}'.")
            return True
        except Exception as e:
            print(f"[ERRO] Falha ao carregar gravação: {e}")
            return False

    # ==========================
    # REPRODUÇÃO (PLAYBACK)
    # ==========================
    def play(self, repetitions=1, speed=1.0):
        if not self.events:
            if not self.load_from_file():
                print("[!] Não há gravação disponível para reproduzir.")
                return

        if not self.events:
            print("[!] A gravação está vazia.")
            return

        print("\n" + "="*50)
        print(" PREPARANDO REPRODUÇÃO")
        print(f" Ações: {len(self.events)}")
        print(f" Repetições: {'Infinito' if repetitions == 0 else repetitions}")
        print(f" Velocidade: {speed}x")
        print(" [!] DICA DE EMERGÊNCIA: Pressione [ESC] a qualquer momento para CANCELAR.")
        print(" A reprodução começará em 3 segundos...")
        print("="*50)

        for i in range(3, 0, -1):
            print(f" Iniciando em {i}...")
            time.sleep(1)

        self.is_playing = True
        self.abort_requested = False

        # Listener global para botão de emergência (ESC)
        def on_emergency_key(key):
            if key == keyboard.Key.esc:
                print("\n\n[!!!] BOTÃO DE EMERGÊNCIA [ESC] PRESSIONADO! INTERROMPENDO... [!!!]")
                self.abort_requested = True
                return False

        emergency_listener = keyboard.Listener(on_press=on_emergency_key)
        emergency_listener.start()

        loop_count = 0
        total_loops = float('inf') if repetitions == 0 else repetitions

        try:
            while loop_count < total_loops and not self.abort_requested:
                loop_count += 1
                if total_loops > 1:
                    print(f"\n--- Executando ciclo {loop_count} de {repetitions if repetitions > 0 else 'infinito'} ---")
                
                start_playback = time.time()

                for event in self.events:
                    if self.abort_requested:
                        break

                    target_time = event["time"] / speed
                    elapsed = time.time() - start_playback
                    wait_time = target_time - elapsed

                    if wait_time > 0:
                        # Sleep em pequenos intervalos para responder rápido ao ESC
                        end_wait = time.time() + wait_time
                        while time.time() < end_wait:
                            if self.abort_requested:
                                break
                            time.sleep(min(0.005, max(0, end_wait - time.time())))

                    if self.abort_requested:
                        break

                    # Executa o evento
                    ev_type = event["type"]

                    if ev_type == "mouse_move":
                        self.mouse_controller.position = (event["x"], event["y"])

                    elif ev_type == "mouse_click":
                        self.mouse_controller.position = (event["x"], event["y"])
                        btn = getattr(mouse.Button, event["button"], mouse.Button.left)
                        if event["pressed"]:
                            self.mouse_controller.press(btn)
                        else:
                            self.mouse_controller.release(btn)

                    elif ev_type == "mouse_scroll":
                        self.mouse_controller.position = (event["x"], event["y"])
                        self.mouse_controller.scroll(event["dx"], event["dy"])

                    elif ev_type == "key_press":
                        k = self.deserialize_key(event["key"])
                        if k is not None:
                            try:
                                self.keyboard_controller.press(k)
                            except Exception:
                                pass

                    elif ev_type == "key_release":
                        k = self.deserialize_key(event["key"])
                        if k is not None:
                            try:
                                self.keyboard_controller.release(k)
                            except Exception:
                                pass

            if not self.abort_requested:
                print("\n[OK] Reprodução concluída com sucesso!")
        finally:
            self.is_playing = False
            if emergency_listener.is_alive():
                emergency_listener.stop()


def exibir_menu():
    recorder = MacroRecorderPlayer()
    
    while True:
        print("\n" + "="*50)
        print("      GRAVADOR E REPETIDOR DE MOUSE E TECLADO")
        print("="*50)
        print(" [1] Gravar nova ação (F6 para parar)")
        print(" [2] Reproduzir gravação atual (1 vez)")
        print(" [3] Reproduzir múltiplas vezes ou em loop")
        print(" [4] Carregar gravação salva do arquivo")
        print(" [5] Sair")
        print("="*50)
        
        opcao = input(" Escolha uma opção (1-5): ").strip()

        if opcao == "1":
            recorder.start_recording()
        elif opcao == "2":
            recorder.play(repetitions=1, speed=1.0)
        elif opcao == "3":
            try:
                rep_input = input(" Quantas repetições? (Digite 0 para LOOP INFINITO): ").strip()
                rep = int(rep_input) if rep_input else 1
                spd_input = input(" Velocidade de reprodução? (Ex: 1.0 = normal, 2.0 = dobro): ").strip()
                spd = float(spd_input) if spd_input else 1.0
                if spd <= 0:
                    spd = 1.0
                recorder.play(repetitions=rep, speed=spd)
            except ValueError:
                print("[!] Valor inválido. Tente novamente.")
        elif opcao == "4":
            recorder.load_from_file()
        elif opcao == "5":
            print("\nEncerrando. Até mais!\n")
            sys.exit(0)
        else:
            print("[!] Opção inválida! Digite um número de 1 a 5.")

if __name__ == "__main__":
    exibir_menu()
