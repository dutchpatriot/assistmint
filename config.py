# Assistmint Configuration
# Adjust these values for your environment

# === OLLAMA / LLM ===
# Default system prompt (English)
SYSTEM_PROMPT = "You are a helpful voice assistant. Keep responses concise and conversational."

# Dutch system prompt (use with Fietje)
SYSTEM_PROMPT_NL = "Je bent een Nederlandse taalkundige, spreek alleen Nederlands met me!."

# Available models:
# - qwen2.5:0.5b (397MB, fast, good multilingual including Dutch)
# - qwen2.5:1.5b (934MB, better quality)
# - qwen2.5:3b (1.9GB, best quality for small models)
# - bramvanroy/fietje-2b-chat:f16 (5.6GB, Dutch-specific)
DEFAULT_MODEL = "qwen2.5:7b"
DEFAULT_MODEL_NL = "qwen2.5:7b"  # 中文 → Nederlands, العربية, and more! 🌍

# Response length
MAX_TOKENS = 35        # Max woorden/characters (+- 4 tokens per woord) /tokens in antwoord. Lager = korter.


# Creativiteit vs Precisie
TEMPERATURE = 0.6         # 0.0 = deterministisch (altijd zelfde antwoord)
                          # 1.0 = creatief/random (kan onzin worden)
                          # 0.7 = goede balans voor gesprek

TOP_P = 0.97	          # "nucleus sampling" - alleen tokens met top 95% kans
                          # Lager = veiliger/voorspelbaarder
                          # Werkt samen met temperature

# Herhaling voorkomen
FREQUENCY_PENALTY = 0.35   # 0.0-2.0: straft woorden die al vaak voorkwamen
                          # Hoger = minder herhaling, maar kan onnatuurlijk worden

PRESENCE_PENALTY = 1.3    # 0.0-2.0: straft woorden die überhaupt al voorkwamen
                          # Hoger = meer nieuwe onderwerpen aanboren

# === SESSION ===
SESSION_ENABLED = False      # Enable session persistence (save/load conversation history)
MAX_MESSAGES = 6            # Rolling window size (0 = unlimited, keeps all messages)

# === AUDIO THRESHOLDS ===
# Speech recognition
SILENCE_SKIP_DB = -45       # Skip transcription if quieter than this
SPEECH_START_DB = -40       # Consider speech started above this
SILENCE_DROP_DB = 16        # dB drop from peak = end of speech
SILENCE_DURATION = 0.9      # Seconden stilte voordat opname stopt
SILENCE_DURATION_EXT = 1.2  # Seconden stilte voor extended listen (langere vragen)

# TTS Interrupt
INTERRUPT_DB = -28          # Loud enough to interrupt TTS
INTERRUPT_DURATION = 0.3    # Seconds sustained before break

# TTS Chunking (prevents babbling on long text)
TTS_MAX_CHARS = 150         # Max characters per TTS chunk (tacotron2 limit ~200)

# === WAKE WORD ===
WAKE_WORD = "hey_jarvis"    # Options: hey_jarvis, alexa, hey_mycroft, timer, weather
WAKE_THRESHOLD = 0.8        # 0.0-1.0: sensitivity (hoger = minder vals positief)
                            # 0.5 = gevoelig, 0.7 = strenger, 0.8 = heel streng

# === DISPLAY ===
USE_EMOJIS = False          # Emojis in terminal output (zet uit bij compatibiliteitsproblemen)
DICTATE_EMOJIS = False      # Emoji replacements in dictation ("heart" → ❤️)

# === DEBUG / VERBOSE ===
VERBOSE_SESSION = False     # Print session load/clear messages ("Loaded X messages")
DEBUG_API = False           # Print full API call details (URL, headers, payload, response)
