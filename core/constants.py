"""
Core constants - NATO alphabet, numbers, hallucinations, etc.

Centralized location for all constant data used across modules.
"""

# NATO phonetic alphabet (+ common Whisper mishearings)
NATO_ALPHABET = {
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

# Number words for spelling (EN + NL)
NUMBER_WORDS = {
    "zero": "0", "nul": "0", "one": "1", "een": "1", "two": "2", "twee": "2",
    "three": "3", "drie": "3", "four": "4", "vier": "4", "five": "5", "vijf": "5",
    "six": "6", "zes": "6", "seven": "7", "zeven": "7", "eight": "8", "acht": "8",
    "nine": "9", "negen": "9"
}

# Number words for key repetition
NUM_WORDS_COUNT = {
    "one": 1, "een": 1, "two": 2, "twee": 2, "three": 3, "drie": 3,
    "four": 4, "vier": 4, "five": 5, "vijf": 5, "six": 6, "zes": 6,
    "seven": 7, "zeven": 7, "eight": 8, "acht": 8, "nine": 9, "negen": 9,
    "ten": 10, "tien": 10
}

# Keyboard actions mapping
KEY_ACTIONS = {
    "backspace": "BackSpace", "backspaces": "BackSpace", "wissen": "BackSpace",
    "delete": "Delete", "deletes": "Delete", "verwijderen": "Delete",
    "enter": "Return", "enters": "Return", "nieuwe regel": "Return", "new line": "Return",
    "tab": "Tab", "tabs": "Tab", "tabje": "Tab",
    # Space as key action (for spell mode)
    "space": "space", "spaces": "space", "spatie": "space", "spaties": "space",
    "spacebar": "space", "spijs": "space",  # Common Whisper mishearings
    # Navigation keys
    "home": "Home", "home key": "Home", "begin": "Home", "start": "Home",
    "end": "End", "end key": "End", "einde": "End", "eind": "End",
}

# Scroll actions (xdotool click - button 4/5 scroll wheel)
# Note: button 5 = scroll wheel down = view moves UP (see content above)
#       button 4 = scroll wheel up = view moves DOWN (see content below)
SCROLL_ACTIONS = {
    "scroll up": 5, "scroll down": 4,
    "omhoog scrollen": 5, "naar beneden scrollen": 4,
    "page up": 5, "page down": 4,
}

# Punctuation and symbols
PUNCTUATION = {
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

# Terminal command symbols
TERMINAL_SYMBOLS = {
    "hyphen": "-", "dash": "-", "min": "-",
    "underscore": "_", "liggend streepje": "_",
    "slash": "/", "schuine streep": "/",
    "backslash": "\\",
    "dot": ".", "period": ".", "punt": ".",
    "space": " ", "spatie": " ",
}

# Known Whisper hallucinations (generated on silence/noise/mumbling)
WHISPER_HALLUCINATIONS = [
    # YouTube-style hallucinations
    "you", "thank you", "thanks for watching", "thank you for watching",
    "subscribe", "like and subscribe", "see you next time", "bye",
    "thanks", "thank you so much", "you you", "you you you",
    "thank you thank you", "thank you thank you thank you",
    "you you you you", "thanks thanks", "thanks thanks thanks",
    # Dutch TV/media hallucinations (from training data)
    "tv gelderland", "tv gelderland 2021", "tv gelderland 2020", "tv gelderland 2019",
    "nos journaal", "rtl nieuws", "omroep gelderland", "omroep brabant",
    "ondertiteling", "ondertiteling tuvalu", "ondertitels", "copyright",
    # Single words / fillers
    "the", "a", "i", "it", "so", "and", "but", "or", "um", "uh", "oh",
    "hmm", "hm", "ah", "eh", "er", "mm", "mhm", "yeah", "yep", "nope",
    # Apologies (common hallucination)
    "i'm sorry", "sorry", "my apologies", "excuse me", "pardon",
    # Music/sound descriptions
    "music", "music playing", "applause", "laughter", "silence",
    "background music", "upbeat music", "soft music",
    # Repeated phrases
    "all right", "alright", "okay okay", "yes yes", "no no",
    # Mumbling artifacts
    "blah", "blah blah", "la la", "da da", "na na",
    # Empty acknowledgments
    "got it", "i see", "right", "right right", "sure", "sure sure",
    # Clock sounds / ticking (common Whisper artifact)
    "tick tick", "tick tock", "tick", "tock", "tic tic", "tic toc",
]

# Main loop hallucinations (same as base - yes/ja/no are valid for confirmations)
# Note: yes/ja/yeah/no/nee are NOT filtered because they're needed for confirmations
MAIN_HALLUCINATIONS = WHISPER_HALLUCINATIONS.copy()
# Remove confirmation words that might be in base list
for word in ["yeah", "yep", "nope"]:
    if word in MAIN_HALLUCINATIONS:
        MAIN_HALLUCINATIONS.remove(word)

# Emoji map for dictation
EMOJI_MAP = {
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
