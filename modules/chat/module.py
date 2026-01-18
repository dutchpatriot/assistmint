"""
Chat Module - General Q&A via Ollama LLM.

This is the fallback module that handles any input not matched by other modules.
Routes questions to Ollama for LLM-powered responses.
"""

import requests
import json
import os
import re
from datetime import datetime
from typing import Optional, Dict, Any, List

from core.modules.base import BaseModule, ModuleResult, ModuleContext, ModuleCapability
from core.audio.tts import speak, get_language, detect_language
from core.logger import session


def _fix_sentence_spacing(text: str) -> str:
    """Fix missing spaces after punctuation (some models output 'zin een.zin twee')."""
    if not text:
        return text
    # Add space after . ! ? if followed by letter/digit (not already spaced)
    text = re.sub(r'([.!?])([A-Za-z0-9])', r'\1 \2', text)
    # Also fix common issues: number.letter, letter.number
    text = re.sub(r'(\d)\.([A-Za-z])', r'\1. \2', text)
    # Remove [/INST] tags that some models leak
    text = re.sub(r'\s*\[/?INST\]\s*', ' ', text)
    return text.strip()

# Import config values
try:
    from config import (
        SYSTEM_PROMPT, SYSTEM_PROMPT_NL, MAX_MESSAGES,
        VERBOSE_SESSION, DEBUG_API, SESSION_ENABLED, DEFAULT_MODEL,
        DEFAULT_MODEL_NL, MODEL_AUTO_SWITCH, get_model_settings
    )
except ImportError:
    SYSTEM_PROMPT = "You are a helpful voice assistant."
    SYSTEM_PROMPT_NL = "Je bent een Nederlandse spraakassistent."
    MAX_MESSAGES = 6
    VERBOSE_SESSION = False
    DEBUG_API = False
    SESSION_ENABLED = True
    DEFAULT_MODEL = "qwen2.5:3b"
    DEFAULT_MODEL_NL = "fietje:latest"
    MODEL_AUTO_SWITCH = True

    def get_model_settings(model_name: str) -> dict:
        return {
            "max_tokens": 750,
            "temperature": 0.77,
            "top_p": 0.91,
            "frequency_penalty": 0.42,
            "presence_penalty": 0.38,
        }


SESSION_FILE = os.path.expanduser("~/.assistmint_session.json")


class ChatModule(BaseModule):
    """
    Chat module for general Q&A via Ollama.

    This is the fallback module - it accepts any input not handled
    by more specific modules.
    """

    def __init__(self):
        super().__init__()
        # Start with smallest model (qwen 1.9GB vs fietje 5.6GB)
        self._model = DEFAULT_MODEL
        self._messages: List[Dict] = []
        self._pending_calendar_event: Optional[Dict] = None

    @property
    def name(self) -> str:
        return "chat"

    @property
    def capabilities(self) -> ModuleCapability:
        return (
            ModuleCapability.TEXT_INPUT |
            ModuleCapability.TEXT_OUTPUT |
            ModuleCapability.EXTERNAL_API |
            ModuleCapability.MULTI_TURN
        )

    @property
    def description(self) -> str:
        return "General Q&A via Ollama LLM"

    @property
    def priority(self) -> int:
        return 10  # Low priority - fallback for unmatched input

    def on_load(self) -> None:
        """Load session history when module loads."""
        super().on_load()
        self.load_session()

    def on_unload(self) -> None:
        """Save session history when module unloads."""
        self.save_session()
        super().on_unload()

    def can_handle(self, text: str, intent: Optional[str] = None) -> float:
        """
        Chat module can handle anything, but with low confidence.

        Returns higher confidence for question-like inputs.
        """
        text_lower = text.lower()

        # Higher confidence for questions
        question_words = ["what", "who", "where", "when", "why", "how", "is", "are", "can", "could", "would"]
        if any(text_lower.startswith(w) for w in question_words):
            return 0.6

        # Higher confidence if it ends with a question mark
        if text.strip().endswith("?"):
            return 0.6

        # Default low confidence - will be used as fallback
        return 0.3

    def execute(self, context: ModuleContext) -> ModuleResult:
        """Send question to Ollama and return response."""
        text = context.text

        # Check if we're waiting for calendar confirmation
        if self._pending_calendar_event:
            return self._handle_calendar_confirmation(text, context)

        # Regular question - send to Ollama
        response = self.ask_ollama(text)

        if response:
            # Check for calendar action in response
            calendar_handled = self._execute_calendar_action(response)

            # ALWAYS clean response (remove tags even if parsing failed)
            clean_response = self._clean_calendar_response(response)

            return ModuleResult(
                text=clean_response,
                success=True,
                requires_confirmation=self._pending_calendar_event is not None
            )

        return ModuleResult(
            text="Sorry, I couldn't get a response.",
            success=False
        )

    def _handle_calendar_confirmation(self, text: str, context: ModuleContext) -> ModuleResult:
        """Handle calendar event confirmation."""
        text_lower = text.lower().strip()

        # Check for confirmation
        if any(w in text_lower for w in ["yes", "ja", "okay", "confirm", "do it"]):
            if self._add_pending_event():
                self._pending_calendar_event = None
                return ModuleResult(text="Added to your calendar.", success=True)
            else:
                return ModuleResult(text="Sorry, couldn't add the event.", success=False)

        # Check for denial
        if any(w in text_lower for w in ["no", "nee", "cancel", "stop", "nevermind"]):
            self._pending_calendar_event = None
            return ModuleResult(text="Okay, cancelled.", success=True)

        # Send to Ollama to continue conversation
        response = self.ask_ollama(text)
        return ModuleResult(text=response or "I didn't understand.", success=bool(response))

    # === Ollama API ===

    def set_model(self, model_name: str):
        """Set the Ollama model to use."""
        self._model = model_name
        session(f"Using model: {self._model}")

    def list_models(self) -> List[str]:
        """Fetch available models from Ollama."""
        try:
            response = requests.get("http://localhost:11434/api/tags")
            if response.status_code == 200:
                models = response.json().get("models", [])
                return [m["name"] for m in models]
        except requests.ConnectionError:
            session("Could not connect to Ollama.")
        return []

    def _get_system_prompt(self) -> str:
        """Get system prompt based on current language setting."""
        lang = get_language()
        today = datetime.now()
        date_info = f"\n\nToday is {today.strftime('%A, %B %d, %Y')}."

        if lang == "nl":
            session("[LLM] Using Dutch system prompt")
            return SYSTEM_PROMPT_NL + f"\n\nVandaag is {today.strftime('%A %d %B %Y')}."

        session(f"[LLM] Using English system prompt (lang={lang})")
        return SYSTEM_PROMPT + date_info

    def _get_model_for_language(self, text: str) -> str:
        """Select model based on detected language of input text."""
        if not MODEL_AUTO_SWITCH:
            return self._model

        # Detect language from input
        detected_lang = detect_language(text)

        if detected_lang == "nl":
            new_model = DEFAULT_MODEL_NL
        else:
            new_model = DEFAULT_MODEL

        # Unload old model if switching to save VRAM
        if new_model != self._model:
            session(f"[MODEL] Switching {self._model} → {new_model}")
            self._unload_current_model()
            self._model = new_model

        return new_model

    def _unload_current_model(self):
        """Unload current model from VRAM before switching."""
        try:
            import requests
            requests.post(
                "http://localhost:11434/api/generate",
                json={"model": self._model, "keep_alive": 0, "prompt": ""},
                timeout=5
            )
            session(f"[VRAM] Unloaded {self._model}")
        except Exception:
            pass

    def ask_ollama(self, question: str) -> Optional[str]:
        """Send a question to Ollama and return the answer."""
        # Auto-switch model based on language
        model_to_use = self._get_model_for_language(question)

        # Add user message to history
        self._messages.append({"role": "user", "content": question})

        # Trim if over limit
        if MAX_MESSAGES > 0 and len(self._messages) > MAX_MESSAGES:
            self._messages = self._messages[-MAX_MESSAGES:]

        # Get per-model settings
        settings = get_model_settings(model_to_use)
        session(f"[MODEL] Using {model_to_use} with temp={settings['temperature']}, top_p={settings['top_p']}")

        url = "http://localhost:11434/v1/chat/completions"
        payload = {
            "model": model_to_use,
            "messages": [
                {"role": "system", "content": self._get_system_prompt()},
            ] + self._messages,
            "stream": False,
            "max_tokens": settings["max_tokens"],
            "stop": None,
            "frequency_penalty": settings["frequency_penalty"],
            "presence_penalty": settings["presence_penalty"],
            "temperature": settings["temperature"],
            "top_p": settings["top_p"]
        }
        headers = {"Content-Type": "application/json"}

        if DEBUG_API:
            print("API Call Information:")
            print(f"URL: {url}")
            print(f"Headers: {headers}")
            print(f"Payload: {json.dumps(payload, indent=4)}")

        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload))

            if DEBUG_API:
                print(f"Response Status Code: {response.status_code}")
                print(f"Response Content: {response.content.decode('utf-8')}")

            if response.status_code == 200:
                answer = response.json().get("choices", [{}])[0].get("message", {}).get("content", "")
                # Fix spacing issues (some models output "zin een.zin twee" without space)
                answer = _fix_sentence_spacing(answer)
                self._messages.append({"role": "assistant", "content": answer})
                self.save_session()
                return answer
            else:
                session("Error communicating with Ollama")
                return None

        except requests.ConnectionError:
            session("Connection error: Unable to reach Ollama")
            return None
        except requests.RequestException as e:
            session(f"API request failed: {e}")
            return None

    # === Session Management ===

    def load_session(self):
        """Load session from JSON file."""
        if not SESSION_ENABLED:
            self._messages = []
            return

        if os.path.exists(SESSION_FILE):
            try:
                with open(SESSION_FILE, 'r') as f:
                    self._messages = json.load(f)
                if VERBOSE_SESSION:
                    session(f"Loaded {len(self._messages)} messages")
            except:
                self._messages = []

    def save_session(self):
        """Save session to JSON file."""
        if not SESSION_ENABLED:
            return
        with open(SESSION_FILE, 'w') as f:
            json.dump(self._messages, f, indent=2)

    def clear_session(self):
        """Clear session history."""
        self._messages = []
        self.save_session()
        if VERBOSE_SESSION:
            session("Session cleared")

    # === Calendar Integration ===

    def has_pending_calendar(self) -> bool:
        """Check if there's a calendar event waiting for confirmation."""
        return self._pending_calendar_event is not None

    def clear_pending_calendar(self):
        """Clear pending calendar event."""
        self._pending_calendar_event = None

    def _execute_calendar_action(self, response_text: str) -> bool:
        """Check if LLM response contains a calendar action."""
        session("[CALENDAR] Checking response for calendar action...")

        # Check for CONFIRM (user said yes)
        if "[CALENDAR_CONFIRM]" in response_text and self._pending_calendar_event:
            session(f"[CALENDAR] Confirmed! Adding: {self._pending_calendar_event.get('event')}")
            self._add_pending_event()
            return True

        # Check for PENDING (new event)
        pattern = r'\[CALENDAR_PENDING\]\s*(\{.*?\})\s*\[/CALENDAR_PENDING\]'
        match = re.search(pattern, response_text, re.DOTALL)

        if match:
            try:
                data = json.loads(match.group(1))
                session(f"[CALENDAR] Pending: {data}")
                self._pending_calendar_event = data
                return True
            except json.JSONDecodeError as e:
                session(f"[CALENDAR] JSON parse error: {e}")
                return False

        return False

    def _add_pending_event(self) -> bool:
        """Add the pending calendar event."""
        if not self._pending_calendar_event:
            return False

        try:
            from calendar_manager import add_event_to_calendar_extended

            data = self._pending_calendar_event
            event_name = data.get("event", "Untitled")
            date = data.get("date")
            start_time = data.get("start")
            end_time = data.get("end")
            location = data.get("location")
            description = data.get("description")
            reminder = data.get("reminder", 30)

            if not date or not start_time:
                session("[CALENDAR] Missing date or start time")
                return False

            # Default end time: 1 hour after start
            if not end_time:
                h, m = map(int, start_time.split(":"))
                h = (h + 1) % 24
                end_time = f"{h:02d}:{m:02d}"

            # Convert 24h to 12h
            def to_12h(t):
                h, m = map(int, t.split(":"))
                period = "AM" if h < 12 else "PM"
                h = h % 12 or 12
                return f"{h}:{m:02d} {period}"

            add_event_to_calendar_extended(
                event_name=event_name,
                start_time=to_12h(start_time),
                end_time=to_12h(end_time),
                date=date,
                location=location,
                description=description,
                reminder_minutes=reminder
            )

            self._pending_calendar_event = None
            return True

        except Exception as e:
            session(f"[CALENDAR] Error adding: {e}")
            return False

    def _clean_calendar_response(self, response_text: str) -> str:
        """Remove calendar blocks from response for cleaner TTS."""
        clean = response_text

        # Remove all calendar-related tags and their content
        # Using [\s\S] instead of . to match newlines reliably
        clean = re.sub(r'\[CALENDAR_ADD\][\s\S]*?\[/CALENDAR_ADD\]', '', clean)
        clean = re.sub(r'\[CALENDAR_PENDING\][\s\S]*?\[/CALENDAR_PENDING\]', '', clean)
        clean = re.sub(r'\[CALENDAR_CONFIRM\][\s\S]*?\[/CALENDAR_CONFIRM\]', '', clean)

        # Remove orphan tags if LLM messed up formatting
        clean = re.sub(r'\[/?CALENDAR_\w+\]', '', clean)

        # Clean up whitespace
        clean = re.sub(r'\n\s*\n', '\n', clean).strip()

        return clean if clean else "Done."


# === Backward Compatibility Functions ===

# Global chat module instance
_chat_module: Optional[ChatModule] = None


def get_chat_module() -> ChatModule:
    """Get the global chat module instance."""
    global _chat_module
    if _chat_module is None:
        _chat_module = ChatModule()
        _chat_module.on_load()
    return _chat_module


def ask_ollama(question: str) -> bool:
    """Send question to Ollama (backward compatibility)."""
    module = get_chat_module()
    response = module.ask_ollama(question)
    if response:
        return speak(response)
    speak("An error occurred while trying to communicate with Ollama.", interruptable=False)
    return False


def select_ollama_model():
    """Let user select a model (backward compatibility)."""
    module = get_chat_module()
    models = module.list_models()

    if not models:
        print("No models found. Using default.")
        return module._model

    print("\n=== Available Ollama Models ===")
    for i, model in enumerate(models):
        print(f"  {i}: {model}")

    try:
        choice = input("Select model number (or press Enter for first): ").strip()
        if choice == "":
            module.set_model(models[0])
        else:
            module.set_model(models[int(choice)])
    except (ValueError, IndexError):
        module.set_model(models[0])

    print(f"Selected model: {module._model}\n")
    return module._model


def set_model(model_name: str):
    """Set model directly (backward compatibility)."""
    get_chat_module().set_model(model_name)


def load_session():
    """Load session (backward compatibility)."""
    get_chat_module().load_session()


def clear_session():
    """Clear session (backward compatibility)."""
    get_chat_module().clear_session()


def has_pending_calendar() -> bool:
    """Check for pending calendar (backward compatibility)."""
    return get_chat_module().has_pending_calendar()


def clear_pending_calendar():
    """Clear pending calendar (backward compatibility)."""
    get_chat_module().clear_pending_calendar()
