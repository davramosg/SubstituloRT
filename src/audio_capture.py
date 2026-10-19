import soundcard as sc
import numpy as np
import time

SAMPLE_RATE = 16000
DURATION = 10

def probar_captura_soundcard():
    print("--- INICIANDO PRUEBA DE AUDIO (SOUNDCARD) ---")
    print("Reproduce un video de YouTube o un audio ahora mismo...")
    
    try:
        mics = sc.all_microphones(include_loopback=True)
        default_speaker = sc.default_speaker()
        
        print(f"Altavoz por defecto: {default_speaker.name}")
        
        target_mic = None
        for mic in mics:
            if default_speaker.name in mic.name and mic.isloopback:
                target_mic = mic
                break
        
        if not target_mic:
            for mic in mics:
                if mic.isloopback:
                    target_mic = mic
                    break
        
        if not target_mic:
            print("No se encontró ningún canal de loopback activo.")
            return

        print(f"Usando canal de audio: {target_mic.name}")
        print(f"Grabando durante {DURATION} segundos...")
        
        start_time = time.time()
        
        # Iniciamos la grabación del sistema
        with target_mic.recorder(samplerate=SAMPLE_RATE) as recorder:
            while time.time() - start_time < DURATION:
                # Usamos .record() en lugar de .recorded()
                data = recorder.record(numframes=1600)
                
                if len(data) > 0:
                    mono_data = np.mean(data, axis=1) if len(data.shape) > 1 else data
                    volume_norm = np.linalg.norm(mono_data) * 50
                    print(f"Escuchando audio del PC... Volumen: {'█' * int(min(volume_norm, 50))}")
                
                time.sleep(0.05)
                
    except Exception as e:
        print(f"Error al capturar audio: {e}")

    print("--- PRUEBA FINALIZADA ---")

if __name__ == "__main__":
    probar_captura_soundcard()
    