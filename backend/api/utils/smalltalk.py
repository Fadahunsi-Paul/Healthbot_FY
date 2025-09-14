# utils/smalltalk.py
import random
import re

GREETINGS = ["hi", "hello", "hey", "good morning", "good afternoon", "good evening"]
FAREWELLS = ["bye", "goodbye", "see you", "take care", "later"]
IDENTITY = ["who are you", "what are you", "what can you do", "your name"]
THANKS = ["thanks", "thank you", "appreciate"]

RESPONSES = {
    "greeting": [
        "Hi there! 👋 I'm your AI Healthbot, here to assist you.",
        "Hello! 😊 How can I help with your health-related questions today?",
        "Hey! I'm your friendly Healthbot. Feel free to ask me anything about health.",
    ],
    "farewell": [
        "Goodbye! Take care of your health. 💙",
        "See you later! Stay healthy. 🌿",
        "Bye! Don’t forget to take care of yourself. ✨",
    ],
    "identity": [
        "I'm an AI Healthbot 🤖, here to answer your health-related questions.",
        "I'm your friendly AI Health assistant! 💡 Ask me about health and wellness.",
    ],
    "thanks": [
        "You're welcome! 🙌",
        "Glad I could help. 💙",
        "Anytime! Stay healthy. 🌿",
    ],
    "fallback": [
        "I'm here for you! 💡 Ask me anything about health and wellness.",
        "I might not understand that, but I'm your AI Healthbot 🤖 — try asking a health question!",
        "Let's focus on your health! 🌿 What’s your concern?",
        "I'm always ready to chat about your health. 💙",
    ],
}

def check_smalltalk(user_input: str):
    if not user_input:
        return None

    text = user_input.lower().strip()
    text = re.sub(r"[^\w\s]", "", text)

    # 1️⃣ Explicit matches
    if any(text.startswith(g) or text == g for g in GREETINGS):
        return random.choice(RESPONSES["greeting"])
    if any(text.startswith(f) or text == f for f in FAREWELLS):
        return random.choice(RESPONSES["farewell"])
    if any(p in text for p in IDENTITY):
        return random.choice(RESPONSES["identity"])
    if any(p in text for p in THANKS):
        return random.choice(RESPONSES["thanks"])

    # 2️⃣ Only fallback if it's too short or nonsense (not a full question)
    if len(text.split()) <= 2:  # like "hmm", "ok", "yo", "bro"
        return random.choice(RESPONSES["fallback"])

    # 3️⃣ Otherwise → assume it’s a health question (let classifier handle it)
    return None
