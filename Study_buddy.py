import asyncio
import json
from datetime import datetime
from dotenv import load_dotenv
from openai.types.responses import ResponseTextDeltaEvent
from agents import Agent, Runner, trace, function_tool, SQLiteSession

from Lab1 import answer

load_dotenv(override=True)

flashcard: list[dict] = []

@function_tool
def add_flashcard(question: str, answer: str) -> str:
    """Save a flashcard with the question on the front and answers on the back"""
    flashcard.append({"question": question,"answer": answer, "created": datetime.now().isoformat() })
    return f"Flashcard #{len(flashcard)} saved!, You now have {len(flashcard)}"

    

