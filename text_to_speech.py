import os
import time
import subprocess
import numpy as np
import sounddevice as sd
from TTS.api import TTS
import re

# Initialize Coqui TTS engine globally
tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=True, gpu=False)


def clean_text(text):
    """Replace unsupported characters with speakable alternatives."""
    # Remove markdown formatting
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # **bold** -> bold
    text = re.sub(r'\*([^*]+)\*', r'\1', text)      # *italic* -> italic
    text = re.sub(r'__([^_]+)__', r'\1', text)      # __bold__ -> bold
    text = re.sub(r'_([^_]+)_', r'\1', text)        # _italic_ -> italic
    text = re.sub(r'```[^`]*```', '', text)         # code blocks
    text = re.sub(r'`([^`]+)`', r'\1', text)        # inline code
    text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)  # headers
    text = re.sub(r'^\s*[-*]\s+', '', text, flags=re.MULTILINE)  # bullets
    text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)  # numbered lists

    # Replace special characters with spoken equivalents
    replacements = {
        '#': ' hashtag ',
        '@': ' at ',
        '&': ' and ',
        '%': ' percent ',
        '$': ' dollar ',
        '*': ' star ',
        '+': ' plus ',
        '=': ' equals ',
        '<': ' less than ',
        '>': ' greater than ',
        '/': ' slash ',
        '\\': ' backslash ',
        '|': ' pipe ',
        '~': ' tilde ',
        '^': ' caret ',
        '_': ' ',
        '{': ' ',
        '}': ' ',
        '[': ' ',
        ']': ' ',
        '`': ' ',
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)

    # Remove remaining non-ASCII characters (emojis etc)
    text = re.sub(r'[^\x00-\x7F]+', '', text)

    # Clean up multiple spaces
    text = re.sub(r'\s+', ' ', text).strip()

    return text

def speak(text, speed=1.5, interruptable=True):
    """Function to speak the provided text with SoX tempo adjustment.

    Returns True if interrupted, False otherwise.
    """
    text = clean_text(text)

    print(f"[TTS] Speaking: {text[:100]}..." if len(text) > 100 else f"[TTS] Speaking: {text}")

    if not text or text.isspace():
        return False

    output_file = "response.wav"
    try:
        tts.tts_to_file(text=text, file_path=output_file)
    except Exception as e:
        print(f"TTS error: {e}")
        return False

    if not interruptable:
        os.system(f"play -q {output_file} tempo {speed}")
        time.sleep(0.3)
        return False

    # Interruptable playback with mic monitoring
    process = subprocess.Popen(
        ["play", "-q", output_file, "tempo", str(speed)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    interrupted = False
    start_time = time.time()

    loud_start = None
    loud_threshold_db = -25
    loud_duration = 0.3  # 300ms sustained = break

    try:
        with sd.InputStream(samplerate=16000, channels=1, dtype='float32', blocksize=1600) as stream:
            while process.poll() is None:
                audio, _ = stream.read(1600)

                # Grace period - ignore first 0.3s
                if time.time() - start_time < 0.3:
                    continue

                rms = np.sqrt(np.mean(audio ** 2))
                db = 20 * np.log10(rms) if rms > 1e-10 else -60.0

                # Track sustained loud audio
                if db > loud_threshold_db:
                    if loud_start is None:
                        loud_start = time.time()
                    elif time.time() - loud_start > loud_duration:
                        print(f"\n[TTS] Break detected! (sustained {db:.1f}dB)")
                        process.terminate()
                        interrupted = True
                        break
                else:
                    loud_start = None  # Reset if quiet
    except Exception as e:
        # Fallback - just wait for process
        process.wait()

    time.sleep(0.3)
    return interrupted

