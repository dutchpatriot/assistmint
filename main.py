import argparse
import time
from speech_recognition import list_microphones, select_microphone_and_samplerate, get_default_microphone, whisper_speech_to_text
from calendar_manager import add_event_to_calendar, check_calendar, remove_event, clear_calendar
from ollama import ask_ollama, select_ollama_model, set_model, load_session, clear_session
from text_to_speech import speak
from wake_word import listen_for_wake_word, init_wake_word
from corrections import apply_corrections, add_correction, list_corrections
from voice2json_intent import recognize_intent
from colors import cmd, v2j, learn, dictate
from config import DICTATE_EMOJIS

# Track last transcription for learning mode
_last_transcription = ""
# Quiet help mode (no TTS for commands)
quiet_help = False
# Use voice2json intent recognition
use_voice2json = True


def _show_dictation_help():
    """Display compact dictation help when entering dictation mode."""
    # ANSI colors
    R = "\033[0m"
    B = "\033[1m"
    DIM = "\033[2m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    MAGENTA = "\033[95m"
    WHITE = "\033[97m"
    BG_CYAN = "\033[46m"

    print(f"""
{B}{WHITE}{BG_CYAN}╔═══════════════════════════════════════════════════════════════════════╗
║  ✍️  DICTATION MODE - Say "stop" / "klaar" to end                      ║
╚═══════════════════════════════════════════════════════════════════════╝{R}
{CYAN}┌─────────────────────────────────────────────────────────────────────┐{R}
{CYAN}│{R} {B}{YELLOW}KEYBOARD:{R}  backspace  delete  enter  tab  ("three backspaces")  {CYAN}│{R}
{CYAN}├─────────────────────────────────────────────────────────────────────┤{R}
{CYAN}│{R} {B}{GREEN}SPELL:{R}     capital/lower alpha  letter alpha  capital/lower A   {CYAN}│{R}
{CYAN}│{R}            number 5 / digit five   (NATO + names: alpha/albert)   {CYAN}│{R}
{CYAN}├─────────────────────────────────────────────────────────────────────┤{R}
{CYAN}│{R} {B}{MAGENTA}CASE:{R}      capital X → X    lowercase X → x    all caps X → X    {CYAN}│{R}
{CYAN}├─────────────────────────────────────────────────────────────────────┤{R}
{CYAN}│{R} {B}{WHITE}PUNCTUATION:{R} period  comma  question mark  exclamation mark       {CYAN}│{R}
{CYAN}│{R}              colon  semicolon  new paragraph  space               {CYAN}│{R}
{CYAN}├─────────────────────────────────────────────────────────────────────┤{R}
{CYAN}│{R} {B}{WHITE}SYMBOLS:{R}   at sign @   hashtag #   slash /   backslash \\          {CYAN}│{R}
{CYAN}│{R}            underscore _   hyphen -   quote "   single quote '     {CYAN}│{R}
{CYAN}│{R}            open/close parenthesis ( )  bracket [ ]  brace {{ }}    {CYAN}│{R}
{CYAN}├─────────────────────────────────────────────────────────────────────┤{R}
{CYAN}│{R} {B}{WHITE}EMOJIS:{R}    house 🏠  heart ❤️  smile 😊  sun ☀️  star ⭐  fire 🔥     {CYAN}│{R}
{CYAN}│{R}            dog 🐕  cat 🐈  coffee ☕  pizza 🍕  + many more        {CYAN}│{R}
{CYAN}├─────────────────────────────────────────────────────────────────────┤{R}
{CYAN}│{R} {DIM}NATO: alpha/albert bravo/boy charlie delta/david echo foxtrot/fox{R}{CYAN}│{R}
{CYAN}│{R} {DIM}      golf/george hotel/henry india juliet/john kilo/king lima{R} {CYAN}│{R}
{CYAN}│{R} {DIM}      mike november oscar papa quebec/queen romeo sierra/sam{R}   {CYAN}│{R}
{CYAN}│{R} {DIM}      tango/tom uniform/uncle victor whiskey xray yankee zulu{R}  {CYAN}│{R}
{CYAN}└─────────────────────────────────────────────────────────────────────┘{R}
""")


def _show_help():
    """Display help menu."""
    # ANSI colors
    R = "\033[0m"       # Reset
    B = "\033[1m"       # Bold
    DIM = "\033[2m"     # Dim
    # Foreground
    WHITE = "\033[97m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    MAGENTA = "\033[95m"
    BLUE = "\033[94m"
    # Background
    BG_BLUE = "\033[44m"
    BG_BLACK = "\033[40m"

    print(f"""
{B}{WHITE}{BG_BLUE}╔══════════════════════════════════════════════════════════════════════════════════════╗
║                    {GREEN}★ ASSISTMINT ★{WHITE}  Voice Assistant                                  ║
║            {DIM}Whisper STT │ Voice2json Intent │ Ollama LLM{R}{B}{WHITE}{BG_BLUE}                           ║
╚══════════════════════════════════════════════════════════════════════════════════════╝{R}

{B}{CYAN}  ENGLISH                              NEDERLANDS{R}
{DIM}  ───────────────────────────────────────────────────────────────────────{R}

{YELLOW}  📅 CALENDAR{R}                           {YELLOW}📅 KALENDER{R}
     {WHITE}"Add to calendar"{R}                     {WHITE}"Voeg toe aan agenda"{R}
     {WHITE}"Check my calendar"{R}                   {WHITE}"Bekijk mijn agenda"{R}
     {WHITE}"Remove event"{R}                        {WHITE}"Verwijder afspraak"{R}
     {WHITE}"Clear my calendar"{R}                   {WHITE}"Wis mijn agenda"{R}

{GREEN}  🧠 SESSION{R}                            {GREEN}🧠 SESSIE{R}
     {WHITE}"Clear session"{R}                       {WHITE}"Vergeet alles"{R}
     {WHITE}"Forget everything"{R}                   {WHITE}"Wis sessie"{R}

{MAGENTA}  🎓 LEARNING{R}                           {MAGENTA}🎓 LEREN{R}
     {WHITE}"Learn that"{R} / {WHITE}"Correct that"{R}         {WHITE}"Leer dat"{R} / {WHITE}"Corrigeer dat"{R}
     {WHITE}"Show corrections"{R}                    {WHITE}"Toon correcties"{R}

{CYAN}  ✍️  DICTATION{R}                          {CYAN}✍️  DICTATIE{R}
     {WHITE}"Dictate"{R} → {DIM}"Stop" to end{R}             {WHITE}"Dicteer"{R} → {DIM}"Stop" / "Klaar"{R}

{BLUE}  💻 TERMINAL{R}                            {BLUE}💬 QUESTIONS{R}
     {WHITE}"Run command"{R} / {WHITE}"Terminal"{R}            {DIM}Just ask anything → Ollama{R}

{DIM}  ═══════════════════════════════════════════════════════════════════════{R}
  {B}{WHITE}DICTATION GRAMMAR{R}
  {YELLOW}Keyboard:{R}  {DIM}"backspace" "delete" "enter" "tab" + "three backspaces" "5 tabs"{R}
  {YELLOW}Case:{R}      {DIM}"capital X" "lowercase X" "all caps X" "hoofdletter X"{R}
  {YELLOW}Spell:{R}     {DIM}"capital/lower A" "letter alpha" "capital alpha" "number 5" "cijfer vijf"{R}
  {YELLOW}Punct:{R}     {DIM}"period/punt" "comma/komma" "question mark" "exclamation mark"{R}
  {YELLOW}Format:{R}    {DIM}"new paragraph" "space/spatie"{R}
  {YELLOW}Symbols:{R}   {DIM}"at sign" "hashtag" "slash" "backslash" "underscore" "hyphen" "asterisk"{R}
  {YELLOW}Brackets:{R}  {DIM}"open/close parenthesis" "open/close bracket" "open/close brace"{R}
  {YELLOW}Quotes:{R}    {DIM}"quote" "single quote" "aanhalingsteken" "apostrof"{R}
  {YELLOW}Emojis:{R}    {DIM}"house" 🏠  "heart" ❤️  "smile" 😊  "sun" ☀️  "fire" 🔥 + many more{R}
{DIM}  ═══════════════════════════════════════════════════════════════════════{R}
  {B}{WHITE}TERMINAL SPELL MODE{R}
  {DIM}Example: "letter lima letter sierra space hyphen letter lima letter alpha" → ls -la{R}
  {DIM}Or names: "letter london letter sam space hyphen letter london letter albert" → ls -la{R}
{DIM}  ═══════════════════════════════════════════════════════════════════════{R}
  {B}{WHITE}NATO + NAMES{R}
  {DIM}alpha/albert bravo/boy charlie delta/david echo foxtrot/fox golf/george{R}
  {DIM}hotel/henry india juliet/john kilo/king lima/london mike/michael november{R}
  {DIM}oscar papa/peter quebec/queen romeo/roger sierra/sam tango/tom uniform{R}
  {DIM}victor whiskey/william xray yankee/yellow zulu/zebra{R}
{DIM}  ═══════════════════════════════════════════════════════════════════════{R}
""")
    if not quiet_help:
        speak("Calendar: add to calendar, check my agenda. Session: clear session or vergeet alles. Dictation: say dictate to type. Or just ask me anything.", speed=1.4)


def _handle_learn_correction(selected_device, samplerate):
    """Handle learning mode - correct misrecognitions."""
    global _last_transcription
    if _last_transcription:
        print(learn("Learning mode activated"))
        speak("What should it be?", speed=1.5)
        correct_phrase = whisper_speech_to_text(selected_device, samplerate).strip()
        if correct_phrase:
            add_correction(_last_transcription, correct_phrase)
            speak(f"Got it. I'll remember that {_last_transcription} means {correct_phrase}.", speed=1.5)
        else:
            speak("Sorry, I didn't catch that.", speed=1.5)
    else:
        speak("Nothing to correct yet. Say something first.", speed=1.5)


def _handle_show_corrections():
    """Show stored corrections."""
    corrections = list_corrections()
    if corrections:
        speak(f"You have {len(corrections)} corrections stored.", speed=1.5)
    else:
        speak("No corrections stored yet.", speed=1.5)


def _handle_add_calendar(selected_device, samplerate):
    """Add event to calendar."""
    print(cmd("Calendar ADD"))
    speak("What is the event?", speed=1.5)
    event_name = whisper_speech_to_text(selected_device, samplerate).strip()

    speak("What time does the event start?", speed=1.5)
    start_time = whisper_speech_to_text(selected_device, samplerate).strip()

    speak("What time does the event end?", speed=1.5)
    end_time = whisper_speech_to_text(selected_device, samplerate).strip()

    speak("What date is the event on?", speed=1.5)
    event_date = whisper_speech_to_text(selected_device, samplerate).strip()

    add_event_to_calendar(event_name, start_time, end_time, date=event_date)


def _handle_check_calendar(selected_device, samplerate):
    """Check calendar for events."""
    print(cmd("Calendar CHECK"))
    speak("For which date or week?", speed=1.5)
    query = whisper_speech_to_text(selected_device, samplerate).strip()

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


def _handle_clear_calendar(selected_device, samplerate):
    """Clear calendar events."""
    print(cmd("Calendar CLEAR"))
    speak("For which date or week would you like to clear?", speed=1.5)
    query = whisper_speech_to_text(selected_device, samplerate).strip()

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


def _handle_remove_calendar(selected_device, samplerate):
    """Remove specific event from calendar."""
    print(cmd("Calendar REMOVE"))
    speak("What is the name of the event to remove?", speed=1.5)
    event_name = whisper_speech_to_text(selected_device, samplerate).strip()

    speak("What date is this event on?", speed=1.5)
    event_date = whisper_speech_to_text(selected_device, samplerate).strip()

    remove_event(event_name, event_date)


def _handle_dictation(selected_device, samplerate):
    """Handle dictation mode - type text into active window."""
    import subprocess
    import re

    _show_dictation_help()
    speak("Dictating. Say stop to end.", speed=1.5)

    # Collect all dictated text for summary
    transcript = []

    # NATO phonetic alphabet (+ common Whisper mishearings)
    nato = {
        "alpha": "a", "alfa": "a", "albert": "a",
        "bravo": "b", "beta": "b", "boy": "b",
        "charlie": "c", "charles": "c",
        "delta": "d", "david": "d",
        "echo": "e", "edward": "e",
        "foxtrot": "f", "fox": "f", "frank": "f",
        "golf": "g", "george": "g",
        "hotel": "h", "henry": "h",
        "india": "i", "indigo": "i",
        "juliet": "j", "julia": "j", "john": "j",
        "kilo": "k", "king": "k",
        "lima": "l", "london": "l", "louis": "l",
        "mike": "m", "michael": "m", "mary": "m",
        "november": "n", "nancy": "n", "nora": "n",
        "oscar": "o", "oliver": "o",
        "papa": "p", "peter": "p", "paul": "p",
        "quebec": "q", "queen": "q",
        "romeo": "r", "robert": "r", "roger": "r",
        "sierra": "s", "sugar": "s", "sam": "s",
        "tango": "t", "tom": "t", "tommy": "t",
        "uniform": "u", "uncle": "u",
        "victor": "v", "victoria": "v",
        "whiskey": "w", "whisky": "w", "william": "w",
        "xray": "x", "x-ray": "x",
        "yankee": "y", "yellow": "y", "young": "y",
        "zulu": "z", "zebra": "z", "zero letter": "z",
    }

    # Number words for spelling
    number_words = {
        "zero": "0", "nul": "0", "one": "1", "een": "1", "two": "2", "twee": "2",
        "three": "3", "drie": "3", "four": "4", "vier": "4", "five": "5", "vijf": "5",
        "six": "6", "zes": "6", "seven": "7", "zeven": "7", "eight": "8", "acht": "8",
        "nine": "9", "negen": "9"
    }

    # Number words for key repetition
    num_words = {
        "one": 1, "een": 1, "two": 2, "twee": 2, "three": 3, "drie": 3,
        "four": 4, "vier": 4, "five": 5, "vijf": 5, "six": 6, "zes": 6,
        "seven": 7, "zeven": 7, "eight": 8, "acht": 8, "nine": 9, "negen": 9,
        "ten": 10, "tien": 10
    }

    # Keyboard actions
    key_actions = {
        "backspace": "BackSpace", "backspaces": "BackSpace", "wissen": "BackSpace",
        "delete": "Delete", "deletes": "Delete", "verwijderen": "Delete",
        "enter": "Return", "enters": "Return", "nieuwe regel": "Return", "new line": "Return",
        "tab": "Tab", "tabs": "Tab", "tabje": "Tab",
    }

    # Punctuation and symbols
    replacements = {
        "period": ".", "punt": ".", "point": ".",
        "comma": ",", "komma": ",",
        "question mark": "?", "vraagteken": "?",
        "exclamation mark": "!", "uitroepteken": "!",
        "colon": ":", "dubbele punt": ":",
        "semicolon": ";", "puntkomma": ";",
        "new paragraph": "\n\n", "nieuwe paragraaf": "\n\n",
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

    # Emoji map
    emoji_map = {
        # Objects (+ plurals)
        "house": "🏠", "houses": "🏠", "home": "🏡", "homes": "🏡",
        "car": "🚗", "cars": "🚗", "phone": "📱", "phones": "📱",
        "computer": "💻", "computers": "💻", "book": "📖", "books": "📖",
        "clock": "🕐", "clocks": "🕐", "calendar": "📅", "mail": "📧", "email": "📧",
        "camera": "📷", "cameras": "📷", "music": "🎵", "movie": "🎬", "movies": "🎬",
        "key": "🔑", "keys": "🔑", "light": "💡", "lights": "💡",
        "money": "💰", "gift": "🎁", "gifts": "🎁", "balloon": "🎈", "balloons": "🎈",
        "rocket": "🚀", "rockets": "🚀", "plane": "✈️", "planes": "✈️",
        "train": "🚂", "trains": "🚂", "bus": "🚌", "bicycle": "🚲", "bicycles": "🚲",
        "boat": "⛵", "boats": "⛵", "umbrella": "☂️", "umbrellas": "☂️",
        # People & body
        "heart": "❤️", "hearts": "❤️", "love": "💕", "kiss": "💋", "kisses": "💋",
        "hand": "✋", "hands": "✋", "thumbs up": "👍", "thumbs down": "👎",
        "clap": "👏", "wave": "👋", "pray": "🙏", "muscle": "💪", "muscles": "💪",
        "eye": "👁️", "eyes": "👁️", "brain": "🧠", "baby": "👶", "babies": "👶",
        "man": "👨", "men": "👨", "woman": "👩", "women": "👩",
        # Faces
        "smile": "😊", "smiles": "😊", "laugh": "😂", "wink": "😉", "cry": "😢", "sad": "😢",
        "angry": "😠", "cool": "😎", "thinking": "🤔", "surprised": "😮", "love face": "😍",
        "sick": "🤒", "sleepy": "😴", "crazy": "🤪", "devil": "😈", "angel": "😇",
        # Animals (+ plurals)
        "dog": "🐕", "dogs": "🐕", "cat": "🐈", "cats": "🐈",
        "bird": "🐦", "birds": "🐦", "fish": "🐟", "butterfly": "🦋", "butterflies": "🦋",
        "bee": "🐝", "bees": "🐝", "pig": "🐷", "pigs": "🐷", "cow": "🐄", "cows": "🐄",
        "horse": "🐴", "horses": "🐴", "monkey": "🐵", "monkeys": "🐵",
        "elephant": "🐘", "elephants": "🐘", "lion": "🦁", "lions": "🦁",
        "tiger": "🐯", "tigers": "🐯", "bear": "🐻", "bears": "🐻",
        "rabbit": "🐰", "rabbits": "🐰", "snake": "🐍", "snakes": "🐍",
        "frog": "🐸", "frogs": "🐸", "chicken": "🐔", "chickens": "🐔",
        "penguin": "🐧", "penguins": "🐧", "whale": "🐋", "whales": "🐋",
        # Food & drink (+ plurals)
        "apple": "🍎", "apples": "🍎", "banana": "🍌", "bananas": "🍌",
        "orange": "🍊", "oranges": "🍊", "pizza": "🍕", "pizzas": "🍕",
        "burger": "🍔", "burgers": "🍔", "coffee": "☕", "beer": "🍺", "beers": "🍺",
        "wine": "🍷", "cake": "🎂", "cakes": "🎂", "ice cream": "🍦",
        "cookie": "🍪", "cookies": "🍪", "bread": "🍞", "cheese": "🧀",
        "egg": "🥚", "eggs": "🥚", "chicken leg": "🍗",
        # Nature & weather (+ plurals)
        "sun": "☀️", "moon": "🌙", "star": "⭐", "stars": "⭐",
        "cloud": "☁️", "clouds": "☁️", "rain": "🌧️", "snow": "❄️",
        "fire": "🔥", "rainbow": "🌈", "rainbows": "🌈",
        "flower": "🌸", "flowers": "🌸", "tree": "🌳", "trees": "🌳",
        "leaf": "🍃", "leaves": "🍃", "earth": "🌍", "ocean": "🌊",
        "mountain": "⛰️", "mountains": "⛰️", "thunder": "⚡",
        # Symbols
        "check": "✓", "checkmark": "✓", "cross": "✗", "warning": "⚠️", "stop sign": "🛑",
        "arrow": "➡️", "sparkle": "✨", "sparkles": "✨", "diamond": "💎", "diamonds": "💎",
        "crown": "👑", "crowns": "👑", "trophy": "🏆", "trophies": "🏆",
        "medal": "🏅", "medals": "🏅", "flag": "🚩", "flags": "🚩",
        "lock": "🔒", "bell": "🔔", "bells": "🔔", "magnifier": "🔍",
        # Dutch words (+ plurals)
        "huis": "🏠", "huizen": "🏠", "auto": "🚗", "autos": "🚗",
        "telefoon": "📱", "telefoons": "📱", "hart": "❤️", "harten": "❤️",
        "lach": "😊", "zon": "☀️", "maan": "🌙", "ster": "⭐", "sterren": "⭐",
        "bloem": "🌸", "bloemen": "🌸", "boom": "🌳", "bomen": "🌳",
        "hond": "🐕", "honden": "🐕", "kat": "🐈", "katten": "🐈",
        "vogel": "🐦", "vogels": "🐦", "vis": "🐟", "vissen": "🐟",
        "vuur": "🔥", "regen": "🌧️", "sneeuw": "❄️",
        "koffie": "☕", "bier": "🍺", "wijn": "🍷", "boek": "📖", "boeken": "📖",
    }

    # Known Whisper hallucinations (generated on silence/noise)
    whisper_hallucinations = [
        "you", "thank you", "thanks for watching", "thank you for watching",
        "subscribe", "like and subscribe", "see you next time", "bye",
        "thanks", "thank you so much", "you you", "you you you",
        "the", "a", "i", "it", "so", "and", "but", "or",
    ]

    def is_hallucination(t):
        """Check if text is likely a Whisper hallucination."""
        t_lower = t.lower().strip().rstrip('.')
        # Check known hallucinations
        if t_lower in whisper_hallucinations:
            return True
        # Check for repeated single word (e.g., "You You You")
        words = t_lower.split()
        if len(words) >= 2 and len(set(words)) == 1:
            return True
        # Check for very short meaningless output
        if len(t_lower) <= 2 and t_lower not in ["ok", "ja", "no"]:
            return True
        return False

    while True:
        text = whisper_speech_to_text(selected_device, samplerate, extended_listen=True).strip()

        if not text:
            continue

        # Skip Whisper hallucinations
        if is_hallucination(text):
            print(dictate(f"Skipped hallucination: '{text}'"))
            continue

        # === PROCESS ALL TRANSFORMATIONS FIRST ===

        # Process case instructions for words
        text = re.sub(r'\b(capital|uppercase|hoofdletter)\s+(\w+)', lambda m: m.group(2).upper(), text, flags=re.IGNORECASE)
        text = re.sub(r'\b(lowercase|kleine letter)\s+(\w+)', lambda m: m.group(2).lower(), text, flags=re.IGNORECASE)
        text = re.sub(r'\ball caps\s+(\w+)', lambda m: m.group(1).upper(), text, flags=re.IGNORECASE)

        # SPELL MODE - NATO alphabet
        for word, letter in nato.items():
            text = re.sub(r'\b(upper|capital|hoofdletter)\s+' + word + r'\b', lambda m, l=letter: l.upper(), text, flags=re.IGNORECASE)
            text = re.sub(r'\b(lower|kleine)\s+' + word + r'\b', lambda m, l=letter: l, text, flags=re.IGNORECASE)
        for word, letter in nato.items():
            text = re.sub(r'\bletter\s+' + word + r'\b', lambda m, l=letter: l, text, flags=re.IGNORECASE)

        # Direct letter spelling: "upper A" → "A", "lower b" → "b"
        text = re.sub(r'\b(upper|capital|hoofdletter)\s+([a-z])\b', lambda m: m.group(2).upper(), text, flags=re.IGNORECASE)
        text = re.sub(r'\b(lower|kleine)\s+([a-z])\b', lambda m: m.group(2).lower(), text, flags=re.IGNORECASE)

        # Numbers: "number 5" / "digit five" / "cijfer vijf" → "5"
        for word, digit in number_words.items():
            text = re.sub(r'\b(number|digit|cijfer)\s+' + word + r'\b', lambda m, d=digit: d, text, flags=re.IGNORECASE)
        text = re.sub(r'\b(number|digit|cijfer)\s+(\d)\b', lambda m: m.group(2), text, flags=re.IGNORECASE)

        # Keyboard actions (actual key presses via xdotool)
        # Handle numbered key actions: "three backspaces", "5 tabs", etc.
        for num_word, num_val in num_words.items():
            for key_word, key_name in key_actions.items():
                pattern = r'\b' + num_word + r'\s+' + key_word + r'\b'
                if re.search(pattern, text, flags=re.IGNORECASE):
                    for _ in range(num_val):
                        subprocess.run(["xdotool", "key", key_name], check=False)
                    print(dictate(f"Key: {key_name} x{num_val}"))
                    text = re.sub(pattern, '', text, flags=re.IGNORECASE)

        # Handle digit + key: "3 backspaces", "5 tabs"
        for key_word, key_name in key_actions.items():
            pattern = r'\b(\d+)\s+' + key_word + r'\b'
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if match:
                num_val = int(match.group(1))
                for _ in range(num_val):
                    subprocess.run(["xdotool", "key", key_name], check=False)
                print(dictate(f"Key: {key_name} x{num_val}"))
                text = re.sub(pattern, '', text, flags=re.IGNORECASE)

        # Handle single key actions
        for word, key in key_actions.items():
            pattern = r'\b' + word + r'\b'
            if re.search(pattern, text, flags=re.IGNORECASE):
                count = len(re.findall(pattern, text, flags=re.IGNORECASE))
                for _ in range(count):
                    subprocess.run(["xdotool", "key", key], check=False)
                    print(dictate(f"Key: {key}"))
                text = re.sub(pattern, '', text, flags=re.IGNORECASE)

        # Clean up extra spaces
        text = re.sub(r'\s+', ' ', text).strip()

        # Punctuation and grammar
        for word, symbol in replacements.items():
            text = re.sub(r'\b' + word + r'\b', lambda m, s=symbol: s, text, flags=re.IGNORECASE)

        # Emoji replacements (if enabled)
        if DICTATE_EMOJIS:
            for word, emoji in emoji_map.items():
                text = re.sub(r'\b' + word + r'\b', emoji, text, flags=re.IGNORECASE)

        # Clean up again after all replacements
        text = text.strip()

        # === NOW CHECK FOR STOP COMMAND (after all processing) ===
        text_lower = text.lower().strip()

        # Only stop if the ENTIRE processed text is a stop word (not embedded)
        stop_words = ["stop", "klaar", "done", "einde", "stop.", "klaar.", "done.", "einde."]
        if text_lower in stop_words:
            speak("Dictation ended.", speed=1.5)
            break

        # If nothing left to type after processing, stay in dictation mode
        if not text:
            continue

        # Type the processed text
        print(dictate(f"Typing: {text}"))
        subprocess.run(["xdotool", "type", "--", text + " "], check=False)
        transcript.append(text)

    # Show transcript summary and copy to clipboard
    if transcript:
        full_text = " ".join(transcript)
        print(f"\n{dictate('═' * 60)}")
        print(dictate("DICTATION TRANSCRIPT:"))
        print(f"{dictate('─' * 60)}")
        print(full_text)
        print(f"{dictate('─' * 60)}")
        print(dictate(f"Words: {len(full_text.split())} | Characters: {len(full_text)}"))
        print(f"{dictate('═' * 60)}\n")

        # Copy to clipboard
        try:
            subprocess.run(["xclip", "-selection", "clipboard"], input=full_text.encode(), check=True)
            print(dictate("📋 Copied to clipboard!"))
            speak(f"Done. {len(full_text.split())} words copied to clipboard.", speed=1.5)
        except FileNotFoundError:
            print(dictate("Install xclip to enable clipboard: sudo apt install xclip"))
            speak(f"Done. {len(full_text.split())} words dictated.", speed=1.5)
    else:
        speak("No text was dictated.", speed=1.5)


def _handle_open_browser():
    """Handle opening browser."""
    import subprocess
    print(cmd("Opening browser"))
    # Try common browsers in order of preference
    browsers = ["firefox", "google-chrome", "chromium-browser", "brave-browser"]
    for browser in browsers:
        try:
            subprocess.Popen([browser], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            speak("Opening browser.", speed=1.5)
            return
        except FileNotFoundError:
            continue
    speak("No browser found.", speed=1.5)


def _handle_terminal(selected_device, samplerate):
    """Handle terminal command execution."""
    import subprocess
    import re
    from voice2json_intent import recognize_intent

    # Known Whisper hallucinations
    hallucinations = ["you", "thank you", "thanks", "you you", "you you you", "the", "a", "i"]

    print(cmd("TERMINAL command"))
    speak("What command?", speed=1.5)
    command = whisper_speech_to_text(selected_device, samplerate, extended_listen=True).strip()

    # Skip hallucinations
    if command.lower().strip().rstrip('.') in hallucinations:
        print(cmd(f"Skipped hallucination: '{command}'"))
        speak("I didn't catch that. Try again.", speed=1.5)
        return

    if command:
        # Process case instructions for words
        command = re.sub(r'\b(capital|uppercase|hoofdletter)\s+(\w+)', lambda m: m.group(2).upper(), command, flags=re.IGNORECASE)
        command = re.sub(r'\b(lowercase|kleine letter)\s+(\w+)', lambda m: m.group(2).lower(), command, flags=re.IGNORECASE)
        command = re.sub(r'\ball caps\s+(\w+)', lambda m: m.group(1).upper(), command, flags=re.IGNORECASE)

        # SPELL MODE - NATO phonetic alphabet (+ common Whisper mishearings)
        nato = {
            "alpha": "a", "alfa": "a", "albert": "a",
            "bravo": "b", "beta": "b", "boy": "b",
            "charlie": "c", "charles": "c",
            "delta": "d", "david": "d",
            "echo": "e", "edward": "e",
            "foxtrot": "f", "fox": "f", "frank": "f",
            "golf": "g", "george": "g",
            "hotel": "h", "henry": "h",
            "india": "i", "indigo": "i",
            "juliet": "j", "julia": "j", "john": "j",
            "kilo": "k", "king": "k",
            "lima": "l", "london": "l", "louis": "l",
            "mike": "m", "michael": "m", "mary": "m",
            "november": "n", "nancy": "n", "nora": "n",
            "oscar": "o", "oliver": "o",
            "papa": "p", "peter": "p", "paul": "p",
            "quebec": "q", "queen": "q",
            "romeo": "r", "robert": "r", "roger": "r",
            "sierra": "s", "sugar": "s", "sam": "s",
            "tango": "t", "tom": "t", "tommy": "t",
            "uniform": "u", "uncle": "u",
            "victor": "v", "victoria": "v",
            "whiskey": "w", "whisky": "w", "william": "w",
            "xray": "x", "x-ray": "x",
            "yankee": "y", "yellow": "y", "young": "y",
            "zulu": "z", "zebra": "z", "zero letter": "z",
        }
        for word, letter in nato.items():
            command = re.sub(r'\b(upper|capital|hoofdletter)\s+' + word + r'\b', lambda m, l=letter: l.upper(), command, flags=re.IGNORECASE)
            command = re.sub(r'\b(lower|kleine)\s+' + word + r'\b', lambda m, l=letter: l, command, flags=re.IGNORECASE)
        for word, letter in nato.items():
            command = re.sub(r'\bletter\s+' + word + r'\b', lambda m, l=letter: l, command, flags=re.IGNORECASE)
        command = re.sub(r'\b(upper|capital|hoofdletter)\s+([a-z])\b', lambda m: m.group(2).upper(), command, flags=re.IGNORECASE)
        command = re.sub(r'\b(lower|kleine)\s+([a-z])\b', lambda m: m.group(2).lower(), command, flags=re.IGNORECASE)
        # Numbers
        number_words = {
            "zero": "0", "nul": "0", "one": "1", "een": "1", "two": "2", "twee": "2",
            "three": "3", "drie": "3", "four": "4", "vier": "4", "five": "5", "vijf": "5",
            "six": "6", "zes": "6", "seven": "7", "zeven": "7", "eight": "8", "acht": "8",
            "nine": "9", "negen": "9"
        }
        for word, digit in number_words.items():
            command = re.sub(r'\b(number|digit|cijfer)\s+' + word + r'\b', lambda m, d=digit: d, command, flags=re.IGNORECASE)
        command = re.sub(r'\b(number|digit|cijfer)\s+(\d)\b', lambda m: m.group(2), command, flags=re.IGNORECASE)
        # Symbols for commands
        cmd_symbols = {
            "hyphen": "-", "dash": "-", "min": "-",
            "underscore": "_", "liggend streepje": "_",
            "slash": "/", "schuine streep": "/",
            "backslash": "\\",
            "dot": ".", "period": ".", "punt": ".",
            "space": " ", "spatie": " ",
        }
        for word, symbol in cmd_symbols.items():
            command = re.sub(r'\b' + word + r'\b', lambda m, s=symbol: s, command, flags=re.IGNORECASE)

        # Filter non-ASCII and punctuation for TTS
        command_safe = ''.join(c for c in command if ord(c) < 128 and c not in '.?!,;:')
        command_safe = command_safe.strip()
        print(cmd(f"Command requested: {command}"))

        if not command_safe:
            speak("I didn't understand the command.", speed=1.5)
            return

        speak(f"Run {command_safe}, yes or no?", speed=1.5)
        confirm = whisper_speech_to_text(selected_device, samplerate).strip().lower()

        # Check for confirm/deny intent
        confirmed = False
        if use_voice2json:
            intent = recognize_intent(confirm, language="auto")
            if intent["action"] == "confirm":
                confirmed = True
            elif intent["action"] == "deny":
                speak("Cancelled.", speed=1.5)
                return

        # Fallback keyword check
        if not confirmed and any(w in confirm for w in ["yes", "ja", "yep", "do it", "go ahead"]):
            confirmed = True

        if confirmed:
            print(cmd(f"Executing: {command}"))
            try:
                result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
                output = result.stdout or result.stderr or "Command completed with no output."
                if len(output) > 200:
                    output = output[:200] + "... truncated"
                print(cmd(f"Output: {output}"))
                speak(output, speed=1.4)
            except subprocess.TimeoutExpired:
                speak("Command timed out after 30 seconds.", speed=1.5)
            except Exception as e:
                speak(f"Error: {str(e)}", speed=1.5)
        else:
            speak("Cancelled.", speed=1.5)


def process_voice_command(transcription, selected_device, samplerate):
    """Process a voice command after wake word detection."""
    global _last_transcription

    # Apply corrections from learning
    transcription = apply_corrections(transcription)
    transcription_lower = transcription.lower()
    print(cmd(f"Processing: {transcription_lower}"))

    # Try voice2json intent recognition first (if enabled)
    if use_voice2json:
        intent_result = recognize_intent(transcription_lower, language="auto")
        if intent_result["intent"]:
            print(v2j(f"Intent: {intent_result['intent']} ({intent_result['language']}) conf={intent_result['confidence']:.2f}"))
            action = intent_result["action"]

            # Handle recognized intents
            if action == "help":
                _show_help()
                return
            elif action == "clear_session":
                clear_session()
                speak("Session cleared.", speed=1.5)
                return
            elif action == "learn_correction":
                _handle_learn_correction(selected_device, samplerate)
                return
            elif action == "show_corrections":
                _handle_show_corrections()
                return
            elif action == "add_calendar":
                _handle_add_calendar(selected_device, samplerate)
                return
            elif action == "check_calendar":
                _handle_check_calendar(selected_device, samplerate)
                return
            elif action == "clear_calendar":
                _handle_clear_calendar(selected_device, samplerate)
                return
            elif action == "remove_calendar":
                _handle_remove_calendar(selected_device, samplerate)
                return
            elif action == "dictate":
                _handle_dictation(selected_device, samplerate)
                return
            elif action == "terminal":
                _handle_terminal(selected_device, samplerate)
                return
            elif action == "open_browser":
                _handle_open_browser()
                return
            # confirm/deny are handled in context, ollama is fallback
        else:
            print(v2j(f"No intent matched, using keyword fallback"))

    # Learning mode triggers
    learn_triggers = ["learn that", "correct that", "fix that", "that's wrong"]
    if any(trigger in transcription_lower for trigger in learn_triggers):
        if _last_transcription:
            print(learn("Learning mode activated"))
            speak("What should it be?", speed=1.5)
            correct_phrase = whisper_speech_to_text(selected_device, samplerate).strip()
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
    help_triggers = ["help me", "help", "what can you do", "commands", "commando's", "lijst", "list commands", "show commands", "options", "opties", "menu"]
    if any(t in transcription_lower for t in help_triggers) or transcription_lower in ["help", "commands", "menu"]:
        print(cmd(f"Matched help trigger in: '{transcription_lower}'"))
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
        print(cmd(f"Calendar ADD matched: has_cal={has_cal}, triggers=['add','put','create','new','schedule']"))
        speak("What is the event?", speed=1.5)
        event_name = whisper_speech_to_text(selected_device, samplerate).strip()

        speak("What time does the event start?", speed=1.5)
        start_time = whisper_speech_to_text(selected_device, samplerate).strip()

        speak("What time does the event end?", speed=1.5)
        end_time = whisper_speech_to_text(selected_device, samplerate).strip()

        speak("What date is the event on?", speed=1.5)
        event_date = whisper_speech_to_text(selected_device, samplerate).strip()

        add_event_to_calendar(event_name, start_time, end_time, date=event_date)

    elif has_cal and any(w in transcription_lower for w in ["what", "check", "show", "list", "today", "tomorrow"]):
        print(cmd(f"Calendar CHECK matched: has_cal={has_cal}, triggers=['what','check','show','list','today','tomorrow']"))
        speak("For which date or week?", speed=1.5)
        query = whisper_speech_to_text(selected_device, samplerate).strip()

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
        print(cmd(f"Calendar CLEAR matched: has_cal={has_cal}, triggers=['clear','delete all','remove all','empty']"))
        speak("For which date or week would you like to clear?", speed=1.5)
        query = whisper_speech_to_text(selected_device, samplerate).strip()

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
        print(cmd(f"Calendar REMOVE matched: has_cal={has_cal}, triggers=['remove','delete','cancel']"))
        speak("What is the name of the event to remove?", speed=1.5)
        event_name = whisper_speech_to_text(selected_device, samplerate).strip()

        speak("What date is this event on?", speed=1.5)
        event_date = whisper_speech_to_text(selected_device, samplerate).strip()

        remove_event(event_name, event_date)

    # Dictation mode
    elif any(w in transcription_lower for w in ["dictate", "diktate", "dik tate", "dicteer", "dicteren", "dictatie", "type this", "start typing"]):
        _handle_dictation(selected_device, samplerate)

    # Terminal command execution
    elif any(w in transcription_lower for w in ["run command", "execute", "terminal", "shell"]):
        _handle_terminal(selected_device, samplerate)

    else:
        # Default: send to Ollama as a question
        print(cmd(f"OLLAMA fallback: '{transcription[:50]}...'") if len(transcription) > 50 else print(cmd(f"OLLAMA fallback: '{transcription}'")))
        interrupted = ask_ollama(transcription)  # Use original case for Ollama
        if interrupted:
            print(cmd("Response interrupted - returning to listen"))
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
                    transcription = whisper_speech_to_text(selected_device, samplerate, extended_listen=True)

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
