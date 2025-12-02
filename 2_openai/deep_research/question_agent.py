from pydantic import BaseModel, Field
from agents import Agent

NUM_QUESTIONS = 3

INSTRUCTIONS = (
    "You are a helpful research assistant. "
    "Given a user's research query, you must generate exactly "
    f"{NUM_QUESTIONS} clarifying questions that will help focus and refine the research. "
    "Each question should:\n"
    "- Be specific and focused on the user's query\n"
    "- Be open-ended (avoid yes/no questions)\n"
    "- Avoid leading the user toward a particular answer\n"
)


class ClarificationQuestion(BaseModel):
    """A single clarifying question and why it is useful."""

    question: str = Field(
        description="The clarifying question that will be asked to the user."
    )
    reason: str = Field(
        description="Why this question is important for focusing and improving the research."
    )


class ClarificationQuestions(BaseModel):
    """A set of clarifying questions for a research query."""

    questions: list[ClarificationQuestion] = Field(
        description=f"Exactly {NUM_QUESTIONS} clarifying questions for the user's query."
    )


question_agent = Agent(
    name="QuestionAgent",
    instructions=INSTRUCTIONS,
    model="gpt-4o-mini",
    output_type=ClarificationQuestions,
)


