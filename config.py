# Assistmint Configuration
# Adjust these values for your environment

# === OLLAMA / LLM ===
SYSTEM_PROMPT = "Je ben een Nederlands Reschtgeleerd Professor in strafrecht!"

# Response length
MAX_TOKENS = 150        # Max woorden/characters (+- 4 tokens per woord) /tokens in antwoord. Lager = korter.

# Creativiteit vs Precisie
TEMPERATURE = 0.7         # 0.0 = deterministisch (altijd zelfde antwoord)
                          # 1.0 = creatief/random (kan onzin worden)
                          # 0.7 = goede balans voor gesprek

TOP_P = 0.97	          # "nucleus sampling" - alleen tokens met top 95% kans
                          # Lager = veiliger/voorspelbaarder
                          # Werkt samen met temperature

# Herhaling voorkomen
FREQUENCY_PENALTY = 0.7   # 0.0-2.0: straft woorden die al vaak voorkwamen
                          # Hoger = minder herhaling, maar kan onnatuurlijk worden

PRESENCE_PENALTY = 0.7    # 0.0-2.0: straft woorden die überhaupt al voorkwamen
                          # Hoger = meer nieuwe onderwerpen aanboren

# === SESSION ===
MAX_MESSAGES = 20  # Rolling window size

# === AUDIO THRESHOLDS ===
# Speech recognition
SILENCE_SKIP_DB = -45       # Skip transcription if quieter than this
SPEECH_START_DB = -35       # Consider speech started above this
SILENCE_DROP_DB = 16        # dB drop from peak = end of speech
SILENCE_DURATION = 0.9      # Seconden stilte voordat opname stopt
SILENCE_DURATION_EXT = 1.2  # Seconden stilte voor extended listen (langere vragen)

# TTS Interrupt
INTERRUPT_DB = -25          # Loud enough to interrupt TTS
INTERRUPT_DURATION = 0.3    # Seconds sustained before break
