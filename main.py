import argparse
import time
from speech_recognition import list_microphones, select_microphone_and_samplerate, get_default_microphone, vosk_speech_to_text
from calendar_manager import add_event_to_calendar, check_calendar, remove_event, clear_calendar
from ollama import ask_ollama, select_ollama_model, set_model, load_session, clear_session
from text_to_speech import speak
from wake_word import listen_for_wake_word, init_wake_word
from corrections import apply_corrections, add_correction, list_corrections

# Track last transcription for learning mode
_last_transcription = ""
# Quiet help mode (no TTS for commands)
quiet_help = False

def process_voice_command(transcription, selected_device, samplerate):
    """Process a voice command after wake word detection."""
    global _last_transcription

    # Apply corrections from learning
    transcription = apply_corrections(transcription)
    transcription_lower = transcription.lower()
    print(f"[CMD] Processing: {transcription_lower}")

    # Learning mode triggers
    learn_triggers = ["learn that", "correct that", "fix that", "that's wrong"]
    if any(trigger in transcription_lower for trigger in learn_triggers):
        if _last_transcription:
            print("[LEARN] Learning mode activated")
            speak("What should it be?", speed=1.5)
            correct_phrase = vosk_speech_to_text(selected_device, samplerate).strip()
            if correct_phrase:
                add_correction(_last_transcription, correct_phrase)
                speak(f"Got it. I'll remember that {_last_transcription} means {correct_phrase}.", speed=1.5)
            else:
                speak("Sorry, I didn't catch that.", speed=1.5)
        else:
            speak("Nothing to correct yet. Say something first.", speed=1.5)
        return

    # Show corrections
    if "show corrections" in transcription_lower or "list corrections" in transcription_lower:
        corrections = list_corrections()
        if corrections:
            speak(f"You have {len(corrections)} corrections stored.", speed=1.5)
        else:
            speak("No corrections stored yet.", speed=1.5)
        return

    # Clear session
    if "clear session" in transcription_lower or "forget everything" in transcription_lower or "vergeet alles" in transcription_lower:
        clear_session()
        speak("Session cleared.", speed=1.5)
        return

    # Help command
    if "help me" in transcription_lower or "help" == transcription_lower or "what can you do" in transcription_lower:
        print("[CMD] → Help")
        # Blue text: \033[94m, Reset: \033[0m
        blue = "\033[94m"
        reset = "\033[0m"
        print(f"""
{blue}╔════════════════════════════════════════════════════════════════════════════════╗
║                              AVAILABLE COMMANDS                                ║
╠════════════════════════════════════════════════════════════════════════════════╣
║ 📅 CALENDAR              │ 💬 QUESTIONS            │ 🎓 LEARNING               ║
║    • "Add to calendar"   │    • Just ask anything  │    • "Learn that"         ║
║    • "Check my agenda"   │                         │    • "Correct that"       ║
║    • "Remove event"      │                         │    • "Show corrections"   ║
╠════════════════════════════════════════════════════════════════════════════════╣
║ 🧠 SESSION               │ 💻 TERMINAL             │ 🛑 INTERRUPT              ║
║    • "Clear session"     │    • "Run command"      │    • Speak loudly to      ║
║    • "Vergeet alles"     │    • "Execute"          │      interrupt TTS        ║
╠════════════════════════════════════════════════════════════════════════════════╣
║ ✍️ DICTATION - "Dictate" / "Dicteer" → "Stop" to end                           ║
╠════════════════════════════════════════════════════════════════════════════════╣
║ DICTATION GRAMMAR                                                              ║
║ Case:    "capital X" "lowercase X" "all caps X" "hoofdletter X"                ║
║ Punct:   "period/punt" "comma/komma" "question mark" "exclamation mark"        ║
║ Format:  "new line" "new paragraph" "tab" "space"                              ║
║ Symbols: "at sign" "hashtag" "slash" "underscore" "hyphen" "asterisk"          ║
║ Brackets: "open/close parenthesis" "open/close bracket" "open/close brace"    ║
║ Quotes:  "quote" "single quote" "aanhalingsteken" "apostrof"                   ║
╚════════════════════════════════════════════════════════════════════════════════╝{reset}
""")
        if not quiet_help:
            speak("Calendar: say add to calendar, check my agenda, or remove event. Questions: just ask me anything. Learning: say learn that or correct that. Session: say clear session to forget everything.", speed=1.4)
        return

    # Store for potential learning
    _last_transcription = transcription

    # Calendar keywords (flexible matching, including common misspellings)
    cal_words = ["calendar", "calander", "agenda", "schedule", "event", "meeting"]
    has_cal = any(w in transcription_lower for w in cal_words)

    if has_cal and any(w in transcription_lower for w in ["add", "put", "create", "new", "schedule"]):
        print("[CMD] → Add to calendar")
        speak("What is the event?", speed=1.5)
        event_name = vosk_speech_to_text(selected_device, samplerate).strip()

        speak("What time does the event start?", speed=1.5)
        start_time = vosk_speech_to_text(selected_device, samplerate).strip()

        speak("What time does the event end?", speed=1.5)
        end_time = vosk_speech_to_text(selected_device, samplerate).strip()

        speak("What date is the event on?", speed=1.5)
        event_date = vosk_speech_to_text(selected_device, samplerate).strip()

        add_event_to_calendar(event_name, start_time, end_time, date=event_date)

    elif has_cal and any(w in transcription_lower for w in ["what", "check", "show", "list", "today", "tomorrow"]):
        print("[CMD] → Check calendar")
        speak("For which date or week?", speed=1.5)
        query = vosk_speech_to_text(selected_device, samplerate).strip()

        if "week" in query.lower():
            if "this week" in query.lower():
                check_calendar(date="this week", week=True)
            elif "next week" in query.lower():
                check_calendar(date="next week", week=True)
            elif "week of" in query.lower():
                specific_week_start = query.lower().replace("week of", "").strip()
                check_calendar(specific_week_start=specific_week_start, week=True)
            else:
                speak("I couldn't understand the week query.", speed=1.5)
        else:
            check_calendar(date=query)

    elif has_cal and any(w in transcription_lower for w in ["clear", "delete all", "remove all", "empty"]):
        print("[CMD] → Clear calendar")
        speak("For which date or week would you like to clear?", speed=1.5)
        query = vosk_speech_to_text(selected_device, samplerate).strip()

        if "week" in query.lower():
            if "this week" in query.lower():
                clear_calendar(date="this week", week=True)
            elif "next week" in query.lower():
                clear_calendar(date="next week", week=True)
            elif "week of" in query.lower():
                specific_week_start = query.lower().replace("week of", "").strip()
                clear_calendar(date=specific_week_start, week=True)
            else:
                speak("I couldn't understand the week query.", speed=1.5)
        else:
            clear_calendar(date=query)

    elif has_cal and any(w in transcription_lower for w in ["remove", "delete", "cancel"]):
        print("[CMD] → Remove event")
        speak("What is the name of the event to remove?", speed=1.5)
        event_name = vosk_speech_to_text(selected_device, samplerate).strip()

        speak("What date is this event on?", speed=1.5)
        event_date = vosk_speech_to_text(selected_device, samplerate).strip()

        remove_event(event_name, event_date)

    # Dictation mode
    elif any(w in transcription_lower for w in ["dictate", "dicteer", "type this", "start typing"]):
        print("[CMD] → Dictation mode")
        speak("Dictating. Say stop to end.", speed=1.5)

        import subprocess
        while True:
            text = vosk_speech_to_text(selected_device, samplerate, extended_listen=True).strip()
            text_lower = text.lower()

            # Stop triggers
            if any(w in text_lower for w in ["stop dictation", "stop dicteren", "stop typing", "klaar"]) or text_lower == "stop":
                speak("Dictation ended.", speed=1.5)
                break

            if text:
                # Process case instructions
                import re
                text = re.sub(r'\b(capital|uppercase|hoofdletter)\s+(\w+)', lambda m: m.group(2).upper(), text, flags=re.IGNORECASE)
                text = re.sub(r'\b(lowercase|kleine letter)\s+(\w+)', lambda m: m.group(2).lower(), text, flags=re.IGNORECASE)
                text = re.sub(r'\ball caps\s+(\w+)', lambda m: m.group(1).upper(), text, flags=re.IGNORECASE)

                # Punctuation and grammar
                replacements = {
                    "period": ".", "punt": ".", "point": ".",
                    "comma": ",", "komma": ",",
                    "question mark": "?", "vraagteken": "?",
                    "exclamation mark": "!", "uitroepteken": "!",
                    "colon": ":", "dubbele punt": ":",
                    "semicolon": ";", "puntkomma": ";",
                    "new line": "\n", "nieuwe regel": "\n", "enter": "\n",
                    "new paragraph": "\n\n", "nieuwe paragraaf": "\n\n",
                    "tab": "\t",
                    "space": " ", "spatie": " ",
                    "at sign": "@", "apenstaartje": "@",
                    "hashtag": "#", "hash": "#",
                    "dollar sign": "$", "dollar": "$",
                    "percent": "%", "procent": "%",
                    "ampersand": "&", "en teken": "&",
                    "asterisk": "*", "sterretje": "*",
                    "underscore": "_", "liggend streepje": "_",
                    "hyphen": "-", "min": "-", "dash": "-",
                    "slash": "/", "schuine streep": "/",
                    "backslash": "\\",
                    "open parenthesis": "(", "haakje openen": "(",
                    "close parenthesis": ")", "haakje sluiten": ")",
                    "open bracket": "[", "close bracket": "]",
                    "open brace": "{", "close brace": "}",
                    "quote": '"', "aanhalingsteken": '"',
                    "single quote": "'", "apostrof": "'",
                }
                for word, symbol in replacements.items():
                    text = re.sub(r'\b' + word + r'\b', symbol, text, flags=re.IGNORECASE)

                print(f"[DICTATE] Typing: {text}")
                # Type into active window
                subprocess.run(["xdotool", "type", "--", text + " "], check=False)
        return

    # Terminal command execution
    elif any(w in transcription_lower for w in ["run command", "execute", "terminal", "shell"]):
        print("[CMD] → Terminal command")
        speak("What command?", speed=1.5)
        command = vosk_speech_to_text(selected_device, samplerate, extended_listen=True).strip()

        if command:
            # Process case instructions
            import re
            # "capital X" / "uppercase X" / "hoofdletter X" → X
            command = re.sub(r'\b(capital|uppercase|hoofdletter)\s+(\w+)', lambda m: m.group(2).upper(), command, flags=re.IGNORECASE)
            # "lowercase X" / "kleine letter X" → x
            command = re.sub(r'\b(lowercase|kleine letter)\s+(\w+)', lambda m: m.group(2).lower(), command, flags=re.IGNORECASE)
            # "all caps WORD" → WORD
            command = re.sub(r'\ball caps\s+(\w+)', lambda m: m.group(1).upper(), command, flags=re.IGNORECASE)
            # Filter non-ASCII and punctuation for TTS
            command_safe = ''.join(c for c in command if ord(c) < 128 and c not in '.?!,;:')
            command_safe = command_safe.strip()
            print(f"[CMD] Command requested: {command}")
            if not command_safe:
                speak("I didn't understand the command.", speed=1.5)
                return
            speak(f"Run {command_safe}, yes or no?", speed=1.5)
            confirm = vosk_speech_to_text(selected_device, samplerate).strip().lower()

            if any(w in confirm for w in ["yes", "ja", "yep", "do it", "go ahead"]):
                print(f"[CMD] Executing: {command}")
                import subprocess
                try:
                    result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
                    output = result.stdout or result.stderr or "Command completed with no output."
                    # Truncate long output
                    if len(output) > 200:
                        output = output[:200] + "... truncated"
                    print(f"[CMD] Output: {output}")
                    speak(output, speed=1.4)
                except subprocess.TimeoutExpired:
                    speak("Command timed out after 30 seconds.", speed=1.5)
                except Exception as e:
                    speak(f"Error: {str(e)}", speed=1.5)
            else:
                speak("Cancelled.", speed=1.5)
        return

    else:
        # Default: send to Ollama as a question
        print("[CMD] → Ollama (no calendar match)")
        interrupted = ask_ollama(transcription)  # Use original case for Ollama
        if interrupted:
            print("[CMD] Response interrupted - returning to listen")
            speak("Okay.", speed=1.5, interruptable=False)

def main():
    parser = argparse.ArgumentParser(description='Assistmint Voice Assistant')
    parser.add_argument('--model', '-m', help='Ollama model to use (skip selection)')
    parser.add_argument('--device', '-d', type=int, help='Audio device index (skip selection)')
    parser.add_argument('--voice', '-v', action='store_true', help='Start directly in voice mode')
    parser.add_argument('--type', '-t', action='store_true', help='Start directly in type mode')
    parser.add_argument('--no-commands', '-nc', action='store_true', help='Skip TTS for help command (print only)')
    args = parser.parse_args()

    global quiet_help
    quiet_help = args.no_commands

    # Select or set Ollama model
    if args.model:
        set_model(args.model)
    else:
        select_ollama_model()

    # Load session history
    load_session()

    # Select microphone
    input_devices = list_microphones()
    if args.device is not None:
        selected_device = input_devices[args.device]
        samplerate = selected_device['default_samplerate']
        print(f"Using device {args.device}: {selected_device['name']} ({samplerate} Hz)")
    else:
        selected_device, samplerate = select_microphone_and_samplerate(input_devices)

    # Determine mode
    if args.voice:
        mode = 'voice'
    elif args.type:
        mode = 'type'
    else:
        mode = None

    while True:
        if mode is None:
            mode = input("Type 'voice' to speak or 'type' to enter commands: ").strip().lower()
        if mode == "voice":
            # Initialize wake word detection
            init_wake_word()
            print("\n" + "="*50)
            print("Voice mode active - say 'Hey Jarvis' to wake me up!")
            print("="*50 + "\n")

            while True:
                # Low-power wake word listening
                detected = listen_for_wake_word(selected_device, samplerate)
                if detected is None:
                    # Error occurred, wait before retry
                    time.sleep(1)
                    continue
                if detected:
                    # Wake word detected! Now listen for command
                    speak("Yes?", speed=1.5)

                    # Get the actual command with extended listening
                    print("Listening for your command...")
                    transcription = vosk_speech_to_text(selected_device, samplerate, extended_listen=True)

                    if transcription:
                        print(f"Command: {transcription}")
                        process_voice_command(transcription, selected_device, samplerate)

                    print("\n💤 Back to sleep... say 'Hey Jarvis' to wake me up\n")

        elif mode == "type":
            print("\nType mode - enter commands or questions directly")
            print("(type 'quit' to exit)\n")

            while True:
                command = input("You: ").strip()
                if command.lower() == 'quit':
                    break
                if command:
                    # Use same processing logic as voice
                    process_voice_command(command, selected_device, samplerate)

        else:
            print("Invalid mode selected. Please choose 'voice' or 'type'.")

if __name__ == "__main__":
    main()

