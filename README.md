# Assistmint

Voice assistant met wake word detection, speech-to-text, en LLM integratie via Ollama.

## Features

- **Wake Word**: "Hey Jarvis" via OpenWakeWord
- **Speech-to-Text**: Faster-Whisper (CPU/CUDA auto-detect)
- **Text-to-Speech**: Coqui TTS met interrupt mogelijkheid
- **LLM**: Ollama (lokaal draaiend)
- **Calendar**: Events toevoegen, bekijken, verwijderen
- **Session Memory**: Rolling window (`~/.assistmint_session.json`)
- **Learning Mode**: Corrigeer misherkenningen ("learn that" / "correct that")
- **Dictation Mode**: Dicteren naar actief venster met grammar commands
- **Terminal Commands**: Shell commands uitvoeren via voice

## Vereisten

- Python 3.11+
- Ollama draaiend op localhost:11434
- SoX (`sudo apt install sox`)
- xdotool (`sudo apt install xdotool`) - voor dictation
- Microfoon

## Installatie

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Gebruik

### Quickstart (aanbevolen)
```bash
./quickstart_assistant.sh [device_index]
```

### Handmatig
```bash
source venv/bin/activate
python main.py --model mistral:latest --voice
```

### CLI opties
| Optie | Beschrijving |
|-------|--------------|
| `--model, -m` | Ollama model (skip selectie) |
| `--device, -d` | Audio device index (skip selectie) |
| `--voice, -v` | Direct voice mode |
| `--type, -t` | Direct type mode |
| `--no-commands, -nc` | Skip TTS voor help (print only) |

### Volledige quickstart (geen prompts)
```bash
python main.py --model mistral:latest --device 2 --voice --no-commands
```

## Commando's (voice)

| Commando | Actie |
|----------|-------|
| "Help me" | Toon beschikbare commando's |
| "Add to calendar" | Event toevoegen |
| "Check my agenda" | Agenda bekijken |
| "Remove event" | Event verwijderen |
| "Learn that" / "Correct that" | Correctie toevoegen |
| "Show corrections" | Opgeslagen correcties tonen |
| "Clear session" / "Vergeet alles" | Conversatie history wissen |
| "Dictate" / "Dicteer" | Dicteermodus starten |
| "Stop" / "Klaar" | Dicteermodus stoppen |
| "Run command" / "Execute" | Terminal command uitvoeren |
| Luid spreken tijdens TTS | Interrupt/break off |
| Overige | Naar Ollama als vraag |

## Dictation Grammar

Tijdens dicteermodus kun je de volgende commando's gebruiken:

### Case (hoofdletters)
| Commando | Resultaat |
|----------|-----------|
| "capital X" / "hoofdletter X" | `X` |
| "lowercase X" / "kleine letter X" | `x` |
| "all caps word" | `WORD` |

### Interpunctie
| Commando | Resultaat |
|----------|-----------|
| "period" / "punt" | `.` |
| "comma" / "komma" | `,` |
| "question mark" / "vraagteken" | `?` |
| "exclamation mark" / "uitroepteken" | `!` |
| "colon" / "dubbele punt" | `:` |
| "semicolon" / "puntkomma" | `;` |

### Formatting
| Commando | Resultaat |
|----------|-----------|
| "new line" / "nieuwe regel" / "enter" | `\n` |
| "new paragraph" / "nieuwe paragraaf" | `\n\n` |
| "tab" | `\t` |
| "space" / "spatie" | ` ` |

### Symbolen
| Commando | Resultaat |
|----------|-----------|
| "at sign" / "apenstaartje" | `@` |
| "hashtag" / "hash" | `#` |
| "dollar sign" / "dollar" | `$` |
| "percent" / "procent" | `%` |
| "ampersand" / "en teken" | `&` |
| "asterisk" / "sterretje" | `*` |
| "underscore" / "liggend streepje" | `_` |
| "hyphen" / "min" / "dash" | `-` |
| "slash" / "schuine streep" | `/` |
| "backslash" | `\` |

### Brackets & Quotes
| Commando | Resultaat |
|----------|-----------|
| "open parenthesis" / "haakje openen" | `(` |
| "close parenthesis" / "haakje sluiten" | `)` |
| "open bracket" / "close bracket" | `[` `]` |
| "open brace" / "close brace" | `{` `}` |
| "quote" / "aanhalingsteken" | `"` |
| "single quote" / "apostrof" | `'` |

### Voorbeeld
```
"Hello comma my name is capital Marco period new line I am a developer"
```
Resultaat: `Hello, my name is MARCO.\nI am a developer`

## Interrupt

Spreek luid (>-25dB) voor 300ms tijdens TTS om de spraak te onderbreken.

## Config

Alle instellingen staan in `config.py`:

```python
# LLM
SYSTEM_PROMPT = "..."
MAX_TOKENS = 150
TEMPERATURE = 0.7

# Audio thresholds
SILENCE_SKIP_DB = -45
SPEECH_START_DB = -35
SILENCE_DURATION = 0.8
INTERRUPT_DB = -25
```

## Bestanden

| Bestand | Functie |
|---------|---------|
| `main.py` | Entry point en command routing |
| `config.py` | Alle configuratie |
| `speech_recognition.py` | Faster-Whisper STT |
| `text_to_speech.py` | Coqui TTS met interrupt |
| `ollama.py` | LLM interface + session memory |
| `wake_word.py` | OpenWakeWord detectie |
| `calendar_manager.py` | Agenda functionaliteit |
| `corrections.py` | Learning mode opslag |

## Data bestanden

- `~/.assistmint_session.json` - Conversatie history
- `~/.assistmint_corrections.json` - Geleerde correcties
