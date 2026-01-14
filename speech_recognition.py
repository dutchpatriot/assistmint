import sounddevice as sd
import queue
import time
import numpy as np
import tempfile
import wave
from config import SILENCE_SKIP_DB, SPEECH_START_DB, SILENCE_DROP_DB, SILENCE_DURATION, SILENCE_DURATION_EXT

# Lazy load - deferred to avoid startup delay
_device = None
_compute_type = None
_whisper_model = None
_WhisperModel = None

def get_device():
    global _device, _compute_type
    if _device is None:
        try:
            import torch
            if torch.cuda.is_available():
                print("[STT] Using CUDA (GPU)")
                _device, _compute_type = "cuda", "float16"
            else:
                print("[STT] Using CPU (no CUDA)")
                _device, _compute_type = "cpu", "int8"
        except ImportError:
            print("[STT] Using CPU (no torch)")
            _device, _compute_type = "cpu", "int8"
    return _device, _compute_type

def init_whisper(model_size="base"):
    """Initialize Whisper model. Sizes: tiny, base, small, medium, large-v2"""
    global _whisper_model, _WhisperModel
    if _whisper_model is None:
        # Lazy import
        if _WhisperModel is None:
            print("[STT] Loading faster-whisper library...")
            from faster_whisper import WhisperModel
            _WhisperModel = WhisperModel

        device, compute_type = get_device()
        print(f"[STT] Loading Whisper model '{model_size}' on {device}...")
        _whisper_model = _WhisperModel(model_size, device=device, compute_type=compute_type)
        print("[STT] Whisper ready!")
    return _whisper_model

def list_microphones():
    devices = sd.query_devices()
    input_devices = []
    for i, device in enumerate(devices):
        if device['max_input_channels'] > 0:
            dev = dict(device)
            dev['index'] = i
            input_devices.append(dev)
    for i, device in enumerate(input_devices):
        print(f"{i}: {device['name']} (device {device['index']})")
    return input_devices

def get_default_microphone(input_devices):
    """Get first available microphone without prompting."""
    selected_device = input_devices[0]
    samplerate = selected_device['default_samplerate']
    print(f"Using microphone: {selected_device['name']} ({samplerate} Hz)")
    return selected_device, samplerate

def select_microphone_and_samplerate(input_devices):
    choice = int(input("Select the microphone by entering the corresponding number: "))
    selected_device = input_devices[choice]
    samplerate = selected_device['default_samplerate']
    print(f"Selected microphone: {selected_device['name']}")
    print(f"Sample rate: {samplerate} Hz")
    return selected_device, samplerate

def whisper_speech_to_text(selected_device, samplerate, extended_listen=False):
    """Record audio and transcribe with Whisper.

    Args:
        extended_listen: If True, waits for longer pause before transcribing.
    """
    model = init_whisper()
    q = queue.Queue()
    audio_buffer = []

    def callback(indata, frames, time_info, status):
        if status:
            print(status)
        q.put(indata.copy())

    try:
        with sd.InputStream(samplerate=int(samplerate), blocksize=4096,
                           device=selected_device['index'], dtype='float32',
                           channels=1, callback=callback):

            if extended_listen:
                print("# Speak your question... (pause to finish)")
            else:
                print("# Say something!")

            peak_db = -60.0
            drop_start = None
            speech_started = False
            silence_threshold = SILENCE_DURATION_EXT if extended_listen else SILENCE_DURATION

            while True:
                try:
                    data = q.get(timeout=0.3)
                except queue.Empty:
                    continue

                audio_buffer.append(data)

                # Calculate dB
                rms = np.sqrt(np.mean(data ** 2)) if len(data) > 0 else 0
                current_db = 20 * np.log10(rms) if rms > 1e-10 else -60.0

                # Track peak (ignore clipped)
                if current_db > peak_db and current_db < -5:
                    peak_db = current_db
                    drop_start = None
                    if current_db > SPEECH_START_DB:
                        speech_started = True

                # Show dB meter
                bar_len = int((current_db + 60) / 60 * 20)
                bar = '█' * max(0, min(20, bar_len)) + '░' * (20 - max(0, min(20, bar_len)))
                print(f"\r[{bar}] {current_db:5.1f}dB ", end='', flush=True)

                # Check for silence after speech
                if speech_started and current_db < (peak_db - SILENCE_DROP_DB):
                    if drop_start is None:
                        drop_start = time.time()
                    elif (time.time() - drop_start) > silence_threshold:
                        print()  # Newline after meter
                        break
                else:
                    drop_start = None

        # Convert buffer to numpy array
        if not audio_buffer:
            return ""

        audio_data = np.concatenate(audio_buffer, axis=0).flatten()

        # Check if there was actual audio (not just silence)
        rms = np.sqrt(np.mean(audio_data ** 2))
        avg_db = 20 * np.log10(rms) if rms > 1e-10 else -60.0
        if avg_db < SILENCE_SKIP_DB:  # Too quiet, probably no speech
            print(f"[STT] Skipping - too quiet ({avg_db:.1f}dB)")
            return ""

        # Save to temp WAV file (Whisper needs file input)
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            temp_path = f.name
            with wave.open(f.name, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)  # 16-bit
                wf.setframerate(int(samplerate))
                wf.writeframes((audio_data * 32767).astype(np.int16).tobytes())

        # Transcribe
        print("[STT] Transcribing...")
        segments, info = model.transcribe(temp_path, beam_size=5)
        text = " ".join([seg.text for seg in segments]).strip()

        # Cleanup
        import os
        os.unlink(temp_path)

        print(f"[STT] Result: {text}")
        return text

    except Exception as e:
        print(f"\nAn error occurred during audio processing: {e}")
    return ""

# Alias for compatibility
vosk_speech_to_text = whisper_speech_to_text
