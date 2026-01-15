import os
import time
import subprocess
import numpy as np
import sounddevice as sd
from TTS.api import TTS
import re
from config import INTERRUPT_DB, INTERRUPT_DURATION, TTS_MAX_CHARS
from colors import tts as tts_log

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


def split_into_chunks(text, max_chars=TTS_MAX_CHARS):
    """Split text into chunks on sentence boundaries to prevent TTS babbling."""
    if len(text) <= max_chars:
        return [text]

    chunks = []
    # Split on sentence boundaries
    sentences = re.split(r'(?<=[.!?])\s+', text)

    current_chunk = ""
    for sentence in sentences:
        # If single sentence is too long, split on commas/semicolons
        if len(sentence) > max_chars:
            sub_parts = re.split(r'(?<=[,;:])\s+', sentence)
            for part in sub_parts:
                if len(current_chunk) + len(part) + 1 <= max_chars:
                    current_chunk = (current_chunk + " " + part).strip()
                else:
                    if current_chunk:
                        chunks.append(current_chunk)
                    # If part itself is too long, force split
                    if len(part) > max_chars:
                        words = part.split()
                        current_chunk = ""
                        for word in words:
                            if len(current_chunk) + len(word) + 1 <= max_chars:
                                current_chunk = (current_chunk + " " + word).strip()
                            else:
                                if current_chunk:
                                    chunks.append(current_chunk)
                                current_chunk = word
                    else:
                        current_chunk = part
        elif len(current_chunk) + len(sentence) + 1 <= max_chars:
            current_chunk = (current_chunk + " " + sentence).strip()
        else:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = sentence

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def speak(text, speed=1.5, interruptable=True):
    """Function to speak the provided text with SoX tempo adjustment.

    Returns True if interrupted, False otherwise.
    Splits long text into chunks to prevent TTS babbling.
    """
    text = clean_text(text)

    print(tts_log(f"Speaking: {text[:100]}...") if len(text) > 100 else tts_log(f"Speaking: {text}"))

    if not text or text.isspace():
        return False

    # Split into chunks to prevent tacotron2 babbling
    chunks = split_into_chunks(text)
    output_file = "response.wav"

    for i, chunk in enumerate(chunks):
        if not chunk or chunk.isspace():
            continue

        try:
            tts.tts_to_file(text=chunk, file_path=output_file)
        except Exception as e:
            print(f"TTS error on chunk {i+1}: {e}")
            continue

        if not interruptable:
            os.system(f"play -q {output_file} tempo {speed}")
            continue

        # Interruptable playback with mic monitoring
        process = subprocess.Popen(
            ["play", "-q", output_file, "tempo", str(speed)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        start_time = time.time()
        loud_start = None

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
                    if db > INTERRUPT_DB:
                        if loud_start is None:
                            loud_start = time.time()
                        elif time.time() - loud_start > INTERRUPT_DURATION:
                            print(f"\n{tts_log(f'Break detected! (sustained {db:.1f}dB)')}")
                            process.terminate()
                            time.sleep(0.3)
                            return True  # Interrupted - stop all chunks
                    else:
                        loud_start = None
        except Exception as e:
            process.wait()

    time.sleep(0.3)
    return False

