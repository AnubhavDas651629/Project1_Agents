import asyncio
import os
import json
from datetime import datetime
from dotenv import load_dotenv
from openai import AsyncOpenAI
from openai.types.responses import ResponseTextDeltaEvent
from agents import Agent, Runner, trace, function_tool, SQLiteSession, OpenAIChatCompletionsModel

load_dotenv(override=True)

flashcard: list[dict] = []

@function_tool
def add_flashcard(question: str, answer: str) -> str:
    """Save a flashcard with the question on the front and answers on the back"""
    flashcard.append({"question": question,"answer": answer, "created": datetime.now().isoformat() })
    return f"Flashcard #{len(flashcard)} saved!, You now have {len(flashcard)}"

@function_tool
def list_flashcard(topic: str = "") -> str:
    """List all flashcards that the student has created so far. Can optionally filter by topic."""
    if not flashcard:
        return "No flashcards yet. Ask me to create some"
    lines = []
    for i, card in enumerate(flashcard,1):
        if topic and topic.lower() not in card['question'].lower() and topic.lower() not in card['answer'].lower():
            continue
        lines.append(f"  #{i} Q: {card['question']}")
        lines.append(f"       A: {card['answer']}")
    if not lines:
        return f"No flashcards found matching '{topic}'."
    return "Your flashcard:\n" + "\n".join(lines)

@function_tool
def quiz_me(topic: str = "") -> str:
    """Pick a random flashcard and quiz the student (show only the question). Can optionally filter by topic."""
    if not flashcard:
        return "You have no flashcard - ask me to create some"
    import random
    matching = [c for c in flashcard if not topic or topic.lower() in c['question'].lower() or topic.lower() in c['answer'].lower()]
    if not matching:
        matching = flashcard
    card = random.choice(matching)
    return f"QUIZ TIME!\n\nQuestion: {card['question']}\n\n(Think about your answer, then tell me and I will check it.)\n\n[correct answer hidden: {card['answer']}]"

groq_client = AsyncOpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key= os.getenv("GROQ_API_KEY")
)

groq_model = OpenAIChatCompletionsModel(
    model="openai/gpt-oss-120b",
    openai_client=groq_client
)


study_buddy = Agent(
    name = "StudyBuddy",
    instructions="""You are a friendly, encouraging study buddy.
    Your job is to help the student learn any topic they want.

    You can:
    - Explain concepts in simple terms with examples
    - Create flashcards using your add_flashcard tool (do this whenever you teach something)
    - List their flashcards using the list_flashcards tool
    - Quiz them using the quiz_me tool

    When the student answers a quiz, compare their answer to the correct answer
    that was returned by the quiz_me tool and tell them if they got it right.

    Keep your explanations concise but clear. Use analogies where helpful.
    Always be positive and encouraging!""",

    model = groq_model,
    tools = [add_flashcard, list_flashcard, quiz_me]
    )

session = SQLiteSession("study-buddy-session-001")

async def run_with_streaming(user_input:str):
    with trace(f"StudyBuddy: {user_input[:40]}"):
        result = Runner.run_streamed(study_buddy, input=user_input, session=session)
        async for event in result.stream_events():
            if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
                print(event.data.delta, end="", flush=True)
        print()

async def run_without_streaming(user_input:str):
    with trace(f"StudyBuddy: {user_input[:40]}"):
        result = await Runner.run(study_buddy, input=user_input, session=session)
    print(result.final_output)

async def main():
    print("=" * 50)
    print("  📚  STUDY BUDDY  — Your AI Study Partner")
    print("=" * 50)
    print("Ask me to explain a topic, make flashcards,")
    print("or quiz you! Type 'quit' to exit.\n")

    use_streaming = True

    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "q"):
            print("\nHappy Studying! ")
            break

        print("\nStudyBuddy: ", end="")
        if use_streaming:
            await run_with_streaming(user_input)
        else:
            await run_without_streaming(user_input)
        print()


if __name__ == "__main__":
    asyncio.run(main())