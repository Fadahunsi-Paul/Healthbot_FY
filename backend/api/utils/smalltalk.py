# utils/smalltalk.py
import random
import re

GREETINGS = ["hi", "hello", "hey", "good morning", "good afternoon", "good evening", "hi there", "hey there"]
FAREWELLS = ["bye", "goodbye", "see you", "take care", "later", "goodbye"]
IDENTITY = ["who are you", "what are you", "what can you do", "your name", "what is your name", "what's up", "what's going on"]
THANKS = ["thanks", "thank you", "appreciate", "thank you so much", "yes i am", "yes"]
CARE = ["how are you", "how are you doing", "how are you feeling", "how are you doing today"]

MEDICAL_KEYWORDS = {
    "malaria", "diabetes", "fever", "headache", "stomach", "pain", "symptoms",
    "causes", "treatment", "prevention", "vaccine", "infection", "cough", "cold",
    "disease", "sickness", "illness", "medication", "prescription", "doctor", "hospital",
    "health", "wellness", "fitness", "nutrition", "exercise", "sleep", "stress", "anxiety",
    "depression", "mental health", "well-being",
}

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
    "care": [
        "I'm doing well, thank you! How about you?",
        "I'm fine! Hope you're having a great day.",
        "I'm good, thanks for asking. How are you feeling?",
        "All good here! How are you doing today?"
    ],
    "fallback": [
        "I'm here for you! 💡 Ask me anything about health and wellness.",
        "I might not understand that, but I'm your AI Healthbot 🤖 — try asking a health question!",
        "Let's focus on your health! 🌿 What’s your concern?",
        "I'm always ready to chat about your health. 💙",
    ],
}

def _clean(text: str) -> str:
    text = (text or "").lower().strip()
    text = re.sub(r"[^\w\s]", "", text)
    return text

def check_smalltalk(user_input: str):
    if not user_input:
        return None

    text = _clean(user_input)
    words = text.split()

    # Exact matches for greetings/farewells/etc.
    if any(text == g or text.startswith(g + " ") for g in GREETINGS):
        return random.choice(RESPONSES["greeting"])
    if any(text == f or text.startswith(f + " ") for f in FAREWELLS):
        return random.choice(RESPONSES["farewell"])
    if any(p in text for p in IDENTITY):
        return random.choice(RESPONSES["identity"])
    if any(p in text for p in THANKS):
        return random.choice(RESPONSES["thanks"])
    if any(p in text for p in CARE):
        return random.choice(RESPONSES["care"])

    # Only treat short utterances as smalltalk if they do NOT contain medical keywords.
    if len(words) <= 2:
        if any(k in text for k in MEDICAL_KEYWORDS):
            return None
        return random.choice(RESPONSES["fallback"])

    return None
