import requests
import json
import os
from text_to_speech import speak

# Global variable to store selected model
selected_model = "mistral"

# Session memory
SESSION_FILE = os.path.expanduser("~/.assistmint_session.json")
MAX_MESSAGES = 30
messages = []

def load_session():
    """Load session from JSON file."""
    global messages
    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, 'r') as f:
                messages = json.load(f)
            print(f"[SESSION] Loaded {len(messages)} messages")
        except:
            messages = []
    return messages

def save_session():
    """Save session to JSON file."""
    with open(SESSION_FILE, 'w') as f:
        json.dump(messages, f, indent=2)

def clear_session():
    """Clear session history."""
    global messages
    messages = []
    save_session()
    print("[SESSION] Cleared")

def list_ollama_models():
    """Fetch available models from Ollama."""
    try:
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            models = response.json().get("models", [])
            return [m["name"] for m in models]
    except requests.ConnectionError:
        print("Could not connect to Ollama. Make sure it's running.")
    return []

def set_model(model_name):
    """Set model directly without prompting."""
    global selected_model
    selected_model = model_name
    print(f"Using model: {selected_model}")
    return selected_model

def select_ollama_model():
    """Let user select a model from available Ollama models."""
    global selected_model
    models = list_ollama_models()

    if not models:
        print("No models found. Using default: mistral")
        return "mistral"

    print("\n=== Available Ollama Models ===")
    for i, model in enumerate(models):
        print(f"  {i}: {model}")

    try:
        choice = input("Select model number (or press Enter for first): ").strip()
        if choice == "":
            selected_model = models[0]
        else:
            selected_model = models[int(choice)]
    except (ValueError, IndexError):
        selected_model = models[0]

    print(f"Selected model: {selected_model}\n")
    return selected_model

def ask_ollama(question):
    """Send a question to Ollama and return the answer."""
    global messages

    # Add user message to history
    messages.append({"role": "user", "content": question})

    # Trim if over limit
    if len(messages) > MAX_MESSAGES:
        messages = messages[-MAX_MESSAGES:]

    url = "http://localhost:11434/v1/chat/completions"  # Ollama API
    payload = {
        "model": selected_model,  # Use selected model
        "messages": [
            {"role": "system", "content": "You are a helpful voice assistant. Keep responses short and concise - 1-2 sentences max. No lists or lengthy explanations unless explicitly asked."},
        ] + messages,
        "stream": False,
        "max_tokens": 150,  # Keep responses short for voice
        "stop": None,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "temperature": 0.7,
        "top_p": 0.95
    }
    headers = {"Content-Type": "application/json"}

    # Print the API call details for debugging
    print("API Call Information:")
    print(f"URL: {url}")
    print(f"Headers: {headers}")
    print(f"Payload: {json.dumps(payload, indent=4)}")

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        print(f"Response Status Code: {response.status_code}")
        print(f"Response Content: {response.content.decode('utf-8')}")

        if response.status_code == 200:
            answer = response.json().get("choices", [{}])[0].get("message", {}).get("content", "Sorry, I couldn't get a response.")
            # Add assistant response to history
            messages.append({"role": "assistant", "content": answer})
            save_session()
            return speak(answer, speed=1.5)
        else:
            speak("An error occurred while trying to communicate with Ollama.", speed=1.5, interruptable=False)
            return False
    except requests.ConnectionError:
        print("Connection error: Unable to reach the Ollama API.")
        speak("Please make sure Ollama is running.", speed=1.5, interruptable=False)
        return False
    except requests.RequestException as e:
        print(f"API request failed: {e}")
        speak("An error occurred while trying to communicate with Ollama.", speed=1.5, interruptable=False)
        return False

