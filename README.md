# SubstituloRT

SubstitlesRT es un software Open source para traducir en tiempo real lo que se reproduzca en su maquina, sea una llamada de discord en ingles, una conferencia, pelicula o charla casual.

#Principales caracteristicas

-100% local, substitulosRt no utiliza apis o ias para funcionar, por su funcionamiento solo necesita las bibliotecas que se encuentran en equeriments.txt

-Velocidad, cuenta con un delay de 4 segundos entre texto

-Offline, despues del primer uso con la bajada de dependencias se puede usar completamente sin conexion a internet

-Motor de traducción neuronal "Argos translate" traduccion a tiempo real gratuita

-Overlay flotante

#caracteristicas tecnicas

-**Lenguaje:** Python

-**Transcripción de Audio:** OpenAI Whisper (`tiny`)

-**Traducción Offline:** Argos Translate

-**Captura de Audio:** PyAudioWPatch (WASAPI Loopback)

-**Interfaz Gráfica:** Tkinter / CustomTkinter UI

-**Empaquetado:** PyInstaller (`onedir`)

#modo de uso

1.Ejecutar proyecto de visual studio code

2.instalar dependencias

3.compilar y utilizar


#Dependencias necesarias

1. Crear entorno virtuas: " python -m venv venvvenv\Scripts\activate " sin comillas

2. ejecutar: " pip install openai-whisper argostranslate pyaudiowpatch numpy python-dotenv pillow"


#Ejecución

-"python src/translator_core.py"


#Ejemplo de uso
<img width="1397" height="887" alt="image" src="https://github.com/user-attachments/assets/65cc362e-5f75-4497-a128-c28e24fc34b8" />
