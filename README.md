# Assistmint

Voice assistant met wake word detection, speech-to-text, en LLM integratie via Ollama.

## Features

- **Wake Word**: "Hey Jarvis" via OpenWakeWord
- **Speech-to-Text**: Faster-Whisper (CPU/CUDA auto-detect)
- **Text-to-Speech**: Coqui TTS met interrupt mogelijkheid
- **LLM**: Ollama (lokaal draaiend)
- **Calendar**: Events toevoegen, bekijken, verwijderen
- **Session Memory**: 30 berichten rolling window (`~/.assistmint_session.json`)
- **Learning Mode**: Corrigeer misherkenningen ("learn that" / "correct that")

## Vereisten

- Python 3.11+
- Ollama draaiend op localhost:11434
- SoX (`sudo apt install sox`)
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
- `--model, -m`: Ollama model (skip selectie)
- `--device, -d`: Audio device index (skip selectie)
- `--voice, -v`: Direct voice mode
- `--type, -t`: Direct type mode
- `--no-commands, -nc`: Skip TTS voor help (print only)

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
| Luid spreken tijdens TTS | Interrupt/break off |
| Overige | Naar Ollama als vraag |

## Interrupt

Spreek luid (>-25dB) voor 300ms tijdens TTS om de spraak te onderbreken.

## Bestanden

- `main.py` - Entry point en command routing
- `speech_recognition.py` - Faster-Whisper STT
- `text_to_speech.py` - Coqui TTS met interrupt
- `ollama.py` - LLM interface + session memory
- `wake_word.py` - OpenWakeWord detectie
- `calendar_manager.py` - Agenda functionaliteit
- `corrections.py` - Learning mode opslag

## Config bestanden

- `~/.assistmint_session.json` - Conversatie history
- `~/.assistmint_corrections.json` - Geleerde correcties
