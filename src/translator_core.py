import os
import sys
import threading
import time
import tkinter as tk
from tkinter import ttk
import logging
import warnings
import numpy as np
import pyaudiowpatch as pyaudio
from dotenv import load_dotenv

# Silenciar advertencias
warnings.filterwarnings("ignore")
logging.getLogger("stanza").setLevel(logging.ERROR)

load_dotenv()

WHISPER_RATE = 16000
CHUNK_SIZE = 1024
DURATION_CHUNK = 4.0

SUPPORTED_LANGUAGES = {
    "Español": "es",
    "Francés": "fr",
    "Portugués": "pt",
    "Alemán": "de",
    "Italiano": "it",
    "Japonés": "ja",
    "Chino": "zh",
    "Ruso": "ru",
    "Árabe": "ar"
}

def get_loopback_devices():
    """Escanea y lista los dispositivos de audio de salida (WASAPI Loopback)"""
    p = pyaudio.PyAudio()
    devices = {}
    try:
        for i in range(p.get_device_count()):
            dev_info = p.get_device_info_by_index(i)
            if dev_info.get("maxInputChannels", 0) > 0 or dev_info.get("isLoopback") or "loopback" in dev_info.get("name", "").lower():
                name = dev_info.get("name", f"Dispositivo {i}")
                devices[name] = i
    except Exception:
        pass
    
    if not devices:
        try:
            default = p.get_default_output_device_info()
            devices[default.get("name", "Dispositivo Predeterminado")] = default["index"]
        except Exception:
            devices["Predeterminado"] = 0
            
    p.terminate()
    return devices

class LanguageSelectorApp:
    """Launcher interactivo con barra de progreso de carga"""
    def __init__(self, audio_devices):
        self.audio_devices = audio_devices
        self.root = tk.Tk()
        self.root.title("Subtítulos RT - Configuración")
        self.root.geometry("420x360")
        self.root.resizable(False, False)
        self.root.config(bg="#121212")
        
        try:
            self.root.iconbitmap("icon.ico")
        except Exception:
            pass
        
        self.root.protocol("WM_DELETE_WINDOW", self.force_exit)
        
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - 420) // 2
        y = (screen_height - 360) // 2
        self.root.geometry(f"420x360+{x}+{y}")
        
        self.selected_language_code = "es"
        self.selected_device_index = None
        self.started = False
        self.create_widgets()

    def create_widgets(self):
        tk.Label(
            self.root, text="Configuración de Subtítulos RT", 
            font=("Arial", 13, "bold"), fg="white", bg="#121212"
        ).pack(pady=15)
        
        tk.Label(
            self.root, text="Idioma de destino:", 
            font=("Arial", 9), fg="#999999", bg="#121212"
        ).pack(anchor="w", padx=30)
        
        self.lang_var = tk.StringVar(value="Español")
        ttk.Combobox(
            self.root, textvariable=self.lang_var, 
            values=list(SUPPORTED_LANGUAGES.keys()), 
            state="readonly", font=("Arial", 10), width=32
        ).pack(pady=5)
        
        tk.Label(
            self.root, text="Dispositivo de audio (Altavoces / Auriculares):", 
            font=("Arial", 9), fg="#999999", bg="#121212"
        ).pack(anchor="w", padx=30, pady=(10, 0))
        
        device_names = list(self.audio_devices.keys())
        default_dev = device_names[0] if device_names else ""
        
        self.dev_var = tk.StringVar(value=default_dev)
        ttk.Combobox(
            self.root, textvariable=self.dev_var, 
            values=device_names, 
            state="readonly", font=("Arial", 9), width=32
        ).pack(pady=5)
        
        # Estado de carga y Barra de progreso
        self.lbl_status = tk.Label(
            self.root, text="", 
            font=("Arial", 8, "italic"), fg="#007acc", bg="#121212"
        )
        self.lbl_status.pack(pady=(10, 2))

        self.progress = ttk.Progressbar(
            self.root, orient="horizontal", length=340, mode="determinate"
        )
        self.progress.pack(pady=5)

        self.btn_start = tk.Button(
            self.root, text="Iniciar Sistema", 
            font=("Arial", 10, "bold"), bg="#007acc", fg="white", 
            activebackground="#005999", activeforeground="white",
            relief="flat", width=28, height=2, command=self.start_loading
        )
        self.btn_start.pack(pady=10)

    def start_loading(self):
        self.btn_start.config(state="disabled")
        selected_lang_name = self.lang_var.get()
        self.selected_language_code = SUPPORTED_LANGUAGES.get(selected_lang_name, "es")
        
        selected_dev_name = self.dev_var.get()
        self.selected_device_index = self.audio_devices.get(selected_dev_name, None)
        
        # Hilo de carga para no congelar la UI
        threading.Thread(target=self.load_components, daemon=True).start()

    def update_progress(self, text, value):
        self.root.after(0, lambda: [
            self.lbl_status.config(text=text),
            self.progress.config(value=value)
        ])

    def load_components(self):
        try:
            self.update_progress("Configurando motor de traducción...", 20)
            import argostranslate.package
            import argostranslate.translate
            
            self.update_progress("Verificando paquetes de idioma...", 40)
            argostranslate.package.update_package_index()
            available = argostranslate.package.get_available_packages()
            
            for p in available:
                if p.from_code == "en" and p.to_code == self.selected_language_code:
                    download_path = p.download()
                    argostranslate.package.install_from_path(download_path)
                    break
                    
            self.update_progress("Cargando modelo de voz Whisper...", 75)
            import whisper
            # Carga del modelo
            whisper.load_model("tiny")
            
            self.update_progress("¡Todo listo! Iniciando...", 100)
            time.sleep(0.5)
            
            self.started = True
            self.root.after(0, self.root.destroy)
        except Exception as e:
            self.update_progress(f"Error al cargar: {str(e)}", 0)
            self.btn_start.config(state="normal")

    def force_exit(self):
        os._exit(0)

    def run(self):
        self.root.mainloop()
        if not self.started:
            os._exit(0)
        return self.selected_language_code, self.selected_device_index


class OptimizedSubtitleOverlay:
    def __init__(self, target_lang):
        self.target_lang = target_lang
        self.root = tk.Tk()
        self.root.title("Subtítulos RT")
        
        try:
            self.root.iconbitmap("icon.ico")
        except Exception:
            pass
        
        self.root.protocol("WM_DELETE_WINDOW", self.force_exit)
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.0)
        
        self.bg_color = "#000001"
        self.root.config(bg=self.bg_color)
        self.root.attributes("-transparentcolor", self.bg_color)
        
        self.make_click_through()
        
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.window_width = int(screen_width * 0.85)
        self.window_height = 150
        x_pos = (screen_width - self.window_width) // 2
        y_pos = screen_height - 210
        
        self.root.geometry(f"{self.window_width}x{self.window_height}+{x_pos}+{y_pos}")
        
        self.canvas = tk.Canvas(
            self.root, 
            width=self.window_width, 
            height=self.window_height, 
            bg=self.bg_color, 
            highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)
        
        self.line1 = ""
        self.line2 = ""
        self.target_y1 = 45
        self.target_y2 = 105
        self.fade_job = None
        
        self.draw_subtitles()

    def make_click_through(self):
        try:
            import ctypes
            hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
            ex_style = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
            ctypes.windll.user32.SetWindowLongW(hwnd, -20, ex_style | 0x00080000 | 0x00000020)
        except Exception:
            pass

    def draw_subtitles(self, y1_offset=0, y2_offset=0):
        self.canvas.delete("all")
        font_config = ("Impact", 28)
        wrap_width = self.window_width - 100
        center_x = self.window_width / 2
        
        y1 = self.target_y1 + y1_offset
        y2 = self.target_y2 + y2_offset
        
        texts_to_draw = []
        if self.line1:
            texts_to_draw.append((self.line1, y1, "#B0B0B0", "#111111"))
        if self.line2:
            texts_to_draw.append((self.line2, y2, "white", "black"))
            
        for text, y_pos, fg_color, outline_color in texts_to_draw:
            for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2), (-1, -1), (1, -1), (-1, 1), (1, 1)]:
                self.canvas.create_text(
                    center_x + dx, y_pos + dy,
                    text=text, font=font_config, fill=outline_color, anchor="center", justify="center", width=wrap_width
                )
            self.canvas.create_text(
                center_x, y_pos,
                text=text, font=font_config, fill=fg_color, anchor="center", justify="center", width=wrap_width
            )

    def smooth_slide_up(self, step=0):
        steps_total = 4
        if step <= steps_total:
            progress = step / steps_total
            offset = (1.0 - progress) * 18
            self.draw_subtitles(y1_offset=offset, y2_offset=offset)
            self.root.after(12, lambda: self.smooth_slide_up(step + 1))
        else:
            self.draw_subtitles(0, 0)

    def fade_in(self, step=0.2):
        current_alpha = self.root.attributes("-alpha")
        if current_alpha < 1.0:
            new_alpha = min(1.0, current_alpha + step)
            self.root.attributes("-alpha", new_alpha)
            self.fade_job = self.root.after(15, lambda: self.fade_in(step))

    def translate_and_update(self, english_text):
        import argostranslate.translate
        translated_text = english_text
        try:
            res = argostranslate.translate.translate(english_text, "en", self.target_lang)
            if res:
                translated_text = res
        except Exception as e:
            pass

        self.root.after(0, lambda: self.apply_text_update(translated_text))

    def apply_text_update(self, new_text):
        if not new_text or len(new_text.strip()) < 3:
            return
        if new_text == self.line2:
            return

        if self.line2 and new_text.startswith(self.line2):
            self.line2 = new_text
            self.draw_subtitles()
        else:
            if self.line2:
                self.line1 = self.line2
            self.line2 = new_text
            self.smooth_slide_up(0)

        if self.root.attributes("-alpha") < 0.2:
            if self.fade_job:
                self.root.after_cancel(self.fade_job)
            self.root.attributes("-alpha", 0.1)
            self.fade_in()
        else:
            self.root.attributes("-alpha", 1.0)

    def force_exit(self):
        os._exit(0)

    def run(self):
        self.root.mainloop()


def iniciar_audio_loop(device_index, overlay_callback):
    import whisper
    model = whisper.load_model("tiny")
    
    p = pyaudio.PyAudio()
    
    try:
        device_info = p.get_device_info_by_index(device_index)
    except Exception:
        device_info = p.get_default_output_device_info()

    native_rate = int(device_info.get("defaultSampleRate", 44100))
    channels = device_info.get("maxInputChannels", 2)
    if channels <= 0:
        channels = 2

    stream = p.open(
        format=pyaudio.paInt16,
        channels=channels,
        rate=native_rate,
        input=True,
        input_device_index=device_info["index"],
        frames_per_buffer=CHUNK_SIZE
    )

    audio_buffer = np.array([], dtype=np.float32)
    max_buffer_samples = int(WHISPER_RATE * 5.0)
    last_processed_text = ""

    try:
        while True:
            frames = []
            blocks_to_read = int(native_rate / CHUNK_SIZE * DURATION_CHUNK)
            
            for _ in range(blocks_to_read):
                data = stream.read(CHUNK_SIZE, exception_on_overflow=False)
                frames.append(data)
            
            audio_data = b"".join(frames)
            audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
            
            if channels > 1:
                audio_np = audio_np.reshape(-1, channels).mean(axis=1)

            if native_rate != WHISPER_RATE:
                target_length = int(len(audio_np) * WHISPER_RATE / native_rate)
                audio_np = np.interp(
                    np.linspace(0, len(audio_np) - 1, target_length),
                    np.arange(len(audio_np)),
                    audio_np
                ).astype(np.float32)

            volume_total = np.linalg.norm(audio_np)
            audio_buffer = np.concatenate((audio_buffer, audio_np))
            if len(audio_buffer) > max_buffer_samples:
                audio_buffer = audio_buffer[-max_buffer_samples:]

            if volume_total < 0.008:
                continue

            prompt_context = last_processed_text[-50:] if last_processed_text and not "a..." in last_processed_text else ""

            resultado = model.transcribe(
                audio_buffer, 
                fp16=False, 
                language="en",
                initial_prompt=prompt_context,
                condition_on_previous_text=False,
                temperature=0.0,
                beam_size=5,
                best_of=5,
                no_speech_threshold=0.6,
                compression_ratio_threshold=2.2
            )
            
            texto_actual = resultado["text"].strip()
            
            if "a... a..." in texto_actual.lower() or texto_actual.count("...") > 4:
                audio_buffer = np.array([], dtype=np.float32)
                last_processed_text = ""
                continue
            
            if texto_actual and texto_actual != last_processed_text:
                last_processed_text = texto_actual
                threading.Thread(target=overlay_callback, args=(texto_actual,), daemon=True).start()

    except Exception:
        pass
    finally:
        try:
            stream.stop_stream()
            stream.close()
            p.terminate()
        except Exception:
            pass

if __name__ == "__main__":
    audio_devices = get_loopback_devices()
    
    selector = LanguageSelectorApp(audio_devices)
    target_language, selected_device_index = selector.run()
    
    overlay = OptimizedSubtitleOverlay(target_language)
    
    audio_thread = threading.Thread(
        target=iniciar_audio_loop, 
        args=(selected_device_index, overlay.translate_and_update,), 
        daemon=True
    )
    audio_thread.start()
    
    overlay.run()