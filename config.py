# Assistmint Configuration
# Adjust these values for your environment

# === OLLAMA / LLM ===
# API endpoint - change if running Ollama on different host/port
OLLAMA_API_URL = "http://localhost:11434"

# Timeouts (seconds) - increase on slower systems
OLLAMA_CHECK_TIMEOUT = 2        # Fast check if Ollama is running
OLLAMA_LIST_TIMEOUT = 5         # List available models
OLLAMA_COMPLETION_TIMEOUT = 120 # Main chat completion (longer for complex responses)
OLLAMA_PARSE_TIMEOUT = 15       # Calendar/extraction parsing (simpler tasks)

# Default system prompt (English)
SYSTEM_PROMPT = """You are a helpful voice assistant. Keep responses short and clear.

ADDING CALENDAR EVENTS: When the user wants to schedule an event, extract details and ask for confirmation.

Example: User says "dentist appointment on February 22 at 1pm"
Your response must be EXACTLY this format:
[CALENDAR_PENDING]
{"event": "dentist appointment", "date": "2026-02-22", "start": "13:00", "end": "14:00", "location": null, "description": null, "reminder": 30}
[/CALENDAR_PENDING]
Dentist appointment on February 22 at 1pm. Say yes to confirm.

IMPORTANT:
- Use the ACTUAL values from what the user said, not placeholders like "title"
- Missing info: end=start+1h, location/description=null

When user confirms (yes/ja/okay), output ONLY:
[CALENDAR_CONFIRM]
[/CALENDAR_CONFIRM]
Added!"""

# Dutch system prompt
SYSTEM_PROMPT_NL = """Je bent een Nederlandse spraakassistent.

BELANGRIJKSTE REGEL: Antwoord UITSLUITEND in het Nederlands! Geen Engels! Nooit! Zelfs als de gebruiker Engels spreekt, antwoord je in het Nederlands.

Houd antwoorden kort en duidelijk.

AGENDA TOEVOEGEN: Wanneer de gebruiker een afspraak wil inplannen, extraheer de details en vraag bevestiging.

Voorbeeld: Gebruiker zegt "tandarts afspraak op 22 februari om 1 uur"
Jouw antwoord moet EXACT dit formaat hebben:
[CALENDAR_PENDING]
{"event": "tandarts afspraak", "date": "2026-02-22", "start": "13:00", "end": "14:00", "location": null, "description": null, "reminder": 30}
[/CALENDAR_PENDING]
Tandarts afspraak op 22 februari om 13:00. Zeg ja om te bevestigen.

BELANGRIJK:
- Gebruik de ECHTE waarden uit wat de gebruiker zei, niet "titel" of "locatie"
- Nederlandse tijd: "half 3" = 14:30, "kwart over 2" = 14:15, "kwart voor 3" = 14:45
- "1 uur 's middags" = 13:00, "3 uur" in context = 15:00
- Ontbrekende info: end=start+1u, location/description=null

Als gebruiker bevestigt (ja/yes/oké), output ALLEEN:
[CALENDAR_CONFIRM]
[/CALENDAR_CONFIRM]
Toegevoegd!"""

# === MODEL CONFIGURATION ===
# Default models
DEFAULT_MODEL = "qwen2.5:3b"                      # English/fallback (1.9GB)
DEFAULT_MODEL_NL = "bramvanroy/fietje-2b-chat:q4_K_M"  # Dutch (1.7GB - smallest!)
MODEL_AUTO_SWITCH = True           # Auto-switch based on detected language

# Per-model settings (override defaults)
# Keys: model name (or partial match like "qwen", "fietje")
MODEL_SETTINGS = {
    # Qwen models - good multilingual, needs moderate creativity
    "qwen2.5:3b": {
        "max_tokens": 750,
        "temperature": 0.77,
        "top_p": 0.91,
        "frequency_penalty": 0.42,
        "presence_penalty": 0.38,
    },
    "qwen2.5:7b": {
        "max_tokens": 750,
        "temperature": 0.75,
        "top_p": 0.90,
        "frequency_penalty": 0.40,
        "presence_penalty": 0.35,
    },
    "bramvanroy/fietje-2b-chat:q4_K_M": {
        "max_tokens": 750,
        "temperature": 0.75,
        "top_p": 0.90,
        "frequency_penalty": 0.40,
        "presence_penalty": 0.35,
    },

    # Fietje - Dutch model, needs stricter settings to reduce hallucination
    "fietje": {
        "max_tokens": 500,          # Shorter = less hallucination
        "temperature": 0.5,         # Lower = more deterministic
        "top_p": 0.85,              # Stricter sampling
        "frequency_penalty": 0.6,   # Higher = less repetition
        "presence_penalty": 0.5,    # Higher = more focused
    },
    # DeepSeek - reasoning model
    "deepseek": {
        "max_tokens": 1000,
        "temperature": 0.6,
        "top_p": 0.90,
        "frequency_penalty": 0.3,
        "presence_penalty": 0.3,
    },
}

# Default settings (used if model not in MODEL_SETTINGS)
MAX_TOKENS = 750
TEMPERATURE = 0.77
TOP_P = 0.91
FREQUENCY_PENALTY = 0.42
PRESENCE_PENALTY = 0.38

# Extraction settings (calendar, parsing - always deterministic)
EXTRACTION_MAX_TOKENS = 300
EXTRACTION_TEMPERATURE = 0.1


def get_model_settings(model_name: str) -> dict:
    """Get settings for a specific model, with fallback to defaults."""
    # Check exact match first
    if model_name in MODEL_SETTINGS:
        return MODEL_SETTINGS[model_name]

    # Check partial match (e.g., "fietje:latest" matches "fietje")
    for key in MODEL_SETTINGS:
        if key in model_name or model_name.startswith(key):
            return MODEL_SETTINGS[key]

    # Return defaults
    return {
        "max_tokens": MAX_TOKENS,
        "temperature": TEMPERATURE,
        "top_p": TOP_P,
        "frequency_penalty": FREQUENCY_PENALTY,
        "presence_penalty": PRESENCE_PENALTY,
    }

# === SESSION ===
SESSION_ENABLED = True      # Enable session persistence (save/load conversation history)
MAX_MESSAGES = 6            # Rolling window size (0 = unlimited, keeps all messages)

# === AUDIO SETTINGS ===
AUDIO_SAMPLE_RATE = 16000   # Sample rate for mic monitoring (16kHz = speech optimal)
AUDIO_BLOCKSIZE = 1600      # Audio buffer size (100ms at 16kHz)

# Speech recognition
SILENCE_SKIP_DB = -45       # Skip transcription if quieter than this
SPEECH_START_DB = -40       # Consider speech started above this
SILENCE_DROP_DB = 19        # dB drop from peak = end of speech
SILENCE_DURATION = 1.2      # Seconden stilte voordat opname stopt
SILENCE_DURATION_EXT = 2.0  # Seconden stilte voor extended listen (langere vragen)

# Noise reduction
NOISE_REDUCE = True         # AI noise suppression voor headphones/ruisige omgevingen
NOISE_REDUCE_STRENGTH = 0.8 # 0.0-1.0: How aggressive (0.8 = strong, 0.5 = mild)

# Whisper STT
# Single model (used when no per-language models configured)
WHISPER_MODEL = "medium"       # Options: tiny, base, small, medium, large (RTX 3070: use small/base)

# Per-language models (optional - set to None to use WHISPER_MODEL for all)
# Can be model names ("small", "medium") or paths to local models
WHISPER_MODEL_EN = None       # English-optimized model (None = use WHISPER_MODEL)
WHISPER_MODEL_NL = None       # Dutch-optimized model (None = use WHISPER_MODEL)
# Example with local models:
# WHISPER_MODEL_EN = "/path/to/whisper-en-model"
# WHISPER_MODEL_NL = "/path/to/whisper-nl-model"

WHISPER_BEAM_SIZE = 4         # Higher = better quality, slower (1-10)
WHISPER_SAMPLE_RATE = 16000   # Whisper vereist 16kHz - niet aanpassen!
STT_BLOCKSIZE = 4096          # Audio buffer voor spraakopname
STT_QUEUE_TIMEOUT = 0.3       # Audio queue timeout (seconds) - lower = more responsive

# Whisper anti-hallucination settings
# These help prevent Whisper from generating fake text on silence/noise
WHISPER_NO_SPEECH_THRESHOLD = 0.6       # 0.0-1.0: Probability threshold for "no speech"
WHISPER_LOG_PROB_THRESHOLD = -1.0       # Log probability threshold for valid speech
WHISPER_HALLUCINATION_SILENCE = 0.5     # Silence duration to trigger hallucination filter

# === GPU SETTINGS ===
USE_GPU = True              # Probeer GPU te gebruiken (met CPU fallback)
GPU_DEVICE_ID = 0        # CUDA device ID (None = auto-select beste GPU, 0/1/2 = specifieke GPU)
WHISPER_COMPUTE_TYPE = "float16"  # GPU: float16, CPU: int8 (auto-detect)

# === TTS SETTINGS (Piper) ===
# Voice models: ~/.local/share/piper/voices/
#   English: en_US-lessac-medium.onnx
#   Dutch:   nl_BE-nathalie-medium.onnx

# --- ENGLISH VOICE SETTINGS ---
TTS_SPEED_EN = 0.90          # Speech rate: 0.5=slow, 1.0=normal, 1.5=fast
TTS_PITCH_EN = 0.95          # Pitch: 0.8=lower, 1.0=normal, 1.2=higher
TTS_VOLUME_EN = 1.0          # Volume multiplier: 0.5=quiet, 1.0=normal, 2.0=loud

# --- DUTCH VOICE SETTINGS ---
TTS_SPEED_NL = 1.14           # Speech rate: 0.5=slow, 1.0=normal, 1.5=fast
TTS_PITCH_NL = 1.39           # Pitch: 0.8=lower, 1.0=normal, 1.2=higher
TTS_VOLUME_NL = 0.90         # Volume multiplier: 0.5=quiet, 1.0=normal, 2.0=loud

# --- LANGUAGE DETECTION ---
TTS_LANG_THRESHOLD = 0.15    # Dutch word ratio to trigger NL voice (0.15 = 15%)
FORCE_LANGUAGE = "nl"        # None=auto-detect, "en"=always English, "nl"=always Dutch

# Language switch commands (voice triggers)
LANG_SWITCH_EN = [
    # English commands
    "speak english", "switch to english", "english please", "in english", "english",
    # Dutch commands to switch to English
    "schakel naar engels", "spreek engels", "naar het engels", "in het engels", "engels",
]
LANG_SWITCH_NL = [
    # Dutch
    "spreek nederlands", "schakel naar nederlands", "in het nederlands",
    "nederlands alsjeblieft", "nederlands", "praat nederlands",
    # English commands for Dutch
    "speak dutch", "switch to dutch", "dutch please", "in dutch", "dutch",
    "go dutch", "use dutch", "change to dutch",
]
LANG_SWITCH_AUTO = ["auto language", "automatisch", "automatic language", "auto detect"]

# --- TTS BEHAVIOR ---
TTS_GRACE_PERIOD = 0.3       # Seconds to ignore mic after TTS starts (prevent self-interrupt)
TTS_LOG_LENGTH = 0           # Max chars in TTS log (0 = unlimited, shows full response)

# --- TTS INTERRUPT ---
INTERRUPT_DB = -28           # Volume threshold to trigger interrupt (higher = less sensitive)
INTERRUPT_DURATION = 0.3     # Seconds of sustained volume before TTS stops

# === WAKE WORD ===
WAKE_WORD = "hey_jarvis"    # Options: hey_jarvis, alexa, hey_mycroft, timer, weather
WAKE_THRESHOLD = 0.5        # 0.0-1.0: sensitivity (hoger = minder vals positief)
                            # 0.5 = gevoelig, 0.7 = strenger, 0.8 = heel streng
WAKE_WORD_WARMUP_DELAY = 1.0  # Seconds to wait for audio system warmup

# === STAY AWAKE MODE ===
# After a command, keep listening without requiring wake word
STAY_AWAKE_ENABLED = True       # True = blijf luisteren na commando, False = slaap meteen
STAY_AWAKE_TIMEOUT = 30.0       # Seconden stilte voordat hij alsnog gaat slapen (0 = nooit auto-sleep)
SLEEP_COMMANDS = ["sleep", "slaap", "ga slapen", "go to sleep", "welterusten"]  # Expliciete slaap-commando's

# === CALENDAR ===
CALENDAR_BACKEND = "evolution"  # "evolution" = GNOME/Evolution (syncs with Google), "google" = gcalcli, "local" = ~/.reminders
CALENDAR_ID = "dutchpatriot@gmail.com"  # Calendar name/email or "primary" for default
CALENDAR_DEFAULT_DURATION = 60  # Default event duration in minutes

CALENDAR_MAX_RETRIES = 5        # How many times to ask again if input not understood (0 = no retry)
CALENDAR_CANCEL_WORDS = ["cancel", "stop", "never mind", "annuleer", "stop maar", "laat maar"]
CALENDAR_ASK_LANGUAGE = True    # Ask "English or Dutch?" at start of calendar actions

# Language detection keywords (for calendar language prompt)
CALENDAR_LANG_EN = ["english", "engels", "en"]
CALENDAR_LANG_NL = ["dutch", "nederlands", "nl", "holland", "hollands"]

# Bilingual calendar prompts (en, nl)
CALENDAR_PROMPTS = {
    # Language selection
    "which_language": ("English or Dutch?", "Engels of Nederlands?"),
    # Add event
    "what_event": ("What is the event?", "Wat is de afspraak?"),
    "what_start_time": ("What time does the event start?", "Hoe laat begint de afspraak?"),
    "what_end_time": ("What time does the event end?", "Hoe laat eindigt de afspraak?"),
    "what_date": ("What date is the event on?", "Op welke datum is de afspraak?"),
    # Check/clear calendar
    "which_date_or_week": ("For which date or week?", "Voor welke datum of week?"),
    "which_date_to_clear": ("For which date or week would you like to clear?", "Welke datum of week wil je wissen?"),
    # Remove event
    "event_name_to_remove": ("What is the name of the event to remove?", "Wat is de naam van de afspraak om te verwijderen?"),
    "event_date_to_remove": ("What date is this event on?", "Op welke datum is deze afspraak?"),
    # Retry prompts
    "retry_time": ("Please say the time again, like '9 AM' or 'three thirty PM'.", "Zeg de tijd opnieuw, zoals '9 uur' of 'half vier'."),
    "retry_date": ("Please say the date again, like 'tomorrow' or 'January 15th'.", "Zeg de datum opnieuw, zoals 'morgen' of '15 januari'."),
    "retry_date_or_week": ("Please say a date like 'today', 'this week', or 'next Friday'.", "Zeg een datum zoals 'vandaag', 'deze week', of 'volgende vrijdag'."),
    # Errors
    "couldnt_understand_time": ("I couldn't understand the time.", "Ik begreep de tijd niet."),
    "couldnt_understand_date": ("I couldn't understand the date.", "Ik begreep de datum niet."),
    "couldnt_understand_week": ("I didn't understand the week query.", "Ik begreep de week vraag niet."),
    "cancelled": ("Okay, cancelled.", "Oké, geannuleerd."),
    "didnt_catch": ("I didn't catch that.", "Ik heb dat niet verstaan."),
    "lets_start_over": ("Let's start over.", "Laten we opnieuw beginnen."),
    "ask_again": ("Let me ask again.", "Ik vraag het nog een keer."),
}

# === DICTATION SLEEP MODE ===
# Words that trigger sleep (mic silenced, no transcription)
# Each phrase must be a SEPARATE item in the list!
DICTATE_SLEEP_WORDS = [
    "sleep", "Sleep!", "slaap", "ga slapen", "welterusten", "tot zo",
    "pause", "pauze", "pauzeer", "go to sleep"
]
# Wake uses WAKE_WORD above (e.g., "Hey Jarvis") - no transcription while sleeping

# === INLINE CAPS TRIGGERS ===
# Phrases that trigger inline UPPERCASE: "this is a test in all caps" → "THIS IS A TEST"
# Trigger can be at START or END of phrase
INLINE_CAPS_TRIGGERS = [
    # English + Whisper mishearings
    "write in caps", "right in caps", "ride in caps",
    "write in all caps", "right in all caps", "ride in all caps",
    "in all caps", "in caps", "all caps", "all capitals",
    # Dutch
    "schrijf in caps", "schrijf in hoofdletters",
    "in alle caps", "in hoofdletters", "met hoofdletters",
    "alles in hoofdletters", "alle caps"
]

# === TOGGLE CAPS LOCK TRIGGERS ===
# Phrases that toggle the real Caps Lock key (LED lights up!)
# Add Whisper mishearings as you discover them
TOGGLE_CAPS_TRIGGERS = [
    "toggle caps lock", "toggle caps", "toggle hoofdletters",
    "togglecapslock", "togel caps lock", "togel caps", "togelcapslock",
    "doggel caps lock", "doggelcapslock", "tokulkepslogon", "togelkepslog"
]

# === SCROLL SETTINGS ===
# Reverse scroll direction: "scroll up" = content moves UP (like pressing Page Up key)
# False = natural scrolling (content moves in direction of scroll wheel)
# True = traditional scrolling (content moves opposite to scroll wheel - like arrow keys)
SCROLL_REVERSE = True  # Set to False if you prefer natural scrolling

# === DISPLAY ===
USE_EMOJIS = False          # Emojis in terminal output (zet uit bij compatibiliteitsproblemen)
DICTATE_EMOJIS = False      # Emoji replacements in dictation ("heart" → ❤️)

# Log truncation (0 = unlimited, shows full text)
LOG_CMD_LENGTH = 0          # Max chars for command log (e.g., "OLLAMA fallback: ...")
LOG_OUTPUT_LENGTH = 0       # Max chars for terminal command output

# Terminal command execution
TERMINAL_TIMEOUT = 600      # Timeout in seconds (600 = 10 minutes, 0 = no timeout)
                            # Long commands like rsync need more time
TERMINAL_NEW_WINDOW = True  # True = open commands in new terminal window, False = show in same terminal

# === VRAM OPTIMIZATION ===
AUTO_UNLOAD_ENABLED = True      # Auto-unload models after inactivity to free VRAM
AUTO_UNLOAD_TIMEOUT = 60.0      # Seconds of inactivity before unloading (default: 60s)
AUTO_UNLOAD_CHECK_INTERVAL = 10.0  # How often to check for inactive models (seconds)
VRAM_LOW_MEMORY_MODE = False    # Aggressive VRAM saving (unload immediately after use)

# === DEBUG / VERBOSE ===
VERBOSE_SESSION = False     # Print session load/clear messages ("Loaded X messages")
DEBUG_API = False           # Print full API call details (URL, headers, payload, response)

# === INTENT ROUTER ===
# Controls how voice commands are routed to modules
INTENT_CONFIDENCE_THRESHOLD = 0.5   # Minimum confidence to use detected intent (0.0-1.0)
INTENT_FALLBACK_CONFIDENCE = 0.8    # Confidence score for fallback/unknown intents

# === VOICE2JSON (Optional - for intent recognition) ===
V2J_DOCKER_IMAGE = "synesthesiam/voice2json"  # Docker image for voice2json
V2J_DOCKER_CHECK_TIMEOUT = 5    # Timeout for Docker image check (seconds)
V2J_COMMAND_TIMEOUT = 10        # Timeout for voice2json commands (seconds)

# === MODULE-SPECIFIC SETTINGS ===

# -- Coding Module --
CODING_MAX_TOKENS = 2000            # Max tokens for code generation (longer than chat)
CODING_SPEAK_TRUNCATE_LENGTH = 300  # Truncate spoken output after this many chars

# -- Terminal Module --
TERMINAL_OUTPUT_TRUNCATE_LENGTH = 200  # Truncate terminal output for TTS
TERMINAL_LARGE_FILE_SIZE = "100M"      # Size threshold for "find large files" command

# -- Dictation Module --
DICTATION_POST_TYPE_DELAY = 1.5     # Seconds to wait after typing (keyboard settle time)
DICTATION_SUBPROCESS_TIMEOUT = 5    # Timeout for dictation subprocess commands

# === SUBPROCESS / EXTERNAL COMMANDS ===
SUBPROCESS_TIMEOUT = 30             # Default timeout for external commands (seconds)
EVOLUTION_TIMEOUT = 30              # Timeout for Evolution calendar client

# === MODEL MANAGER ===
MODEL_MANAGER_HISTORY_WINDOW = 6    # Keep last N messages per module (3 exchanges)
MODEL_MANAGER_HISTORY_MAX = 12      # Trim history if exceeds this
