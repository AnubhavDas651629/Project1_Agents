import asyncio
import json
from datetime import datetime
from dotenv import load_dotenv
from openai.types.responses import ResponseTextDeltaEvent
from agents import Agent, Runner, trace, function_tool, SQLiteSession

from Lab1 import question

load_dotenv(override=True)

flashcard: list[dict] = []

@function_tool
def add_flashcard(question: str, answer: str) -> str:
    """Save a flashcard with the question on the front and answers on the back"""
    flashcard.append({"question": question,"answer": answer, "created": datetime.now().isoformat() })
    return f"Flashcard #{len(flashcard)} saved!, You now have {len(flashcard)}"

@function_tool
def list_flashcard() -> str:
    """List all flashcards that the student has created so far"""
    if not flashcard:
        return "No flashcards yet. Ask me to create some"
    lines = []
    for i, card in enumerate(flashcard,1):
        lines.append(f"  #{i} Q: {card['question']}")
        lines.append(f"       A: {card['answer']}")
    return "Your flashcard:\n" + "\n".join(lines)


