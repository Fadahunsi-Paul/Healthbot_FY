
from typing import List, Dict

def build_context(history: List[Dict], question: str, max_messages: int = 6) -> str:
    if not history:
        return question

    recent = history[-max_messages:]
    weighted_parts = []

    for idx, msg in enumerate(recent):
        repeat = min(idx + 1, 3)
        formatted = f"{msg['sender'].capitalize()}: {msg['message']}"
        for _ in range(repeat):
            weighted_parts.append(formatted)

    weighted_parts.append(f"User: {question}")

    return " \n ".join(weighted_parts)
