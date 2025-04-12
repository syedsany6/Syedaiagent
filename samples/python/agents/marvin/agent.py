import logging
import os
import threading
from collections.abc import AsyncIterable
from typing import Annotated, Any, ClassVar

from pydantic import BaseModel, EmailStr, Field

import marvin

logger = logging.getLogger(__name__)

ClarifyingQuestion = Annotated[
    str, Field(description="A clarifying question to ask the user")
]


class ContactInfo(BaseModel):
    """Structured contact information extracted from text."""

    name: str = Field(description="Person's first and last name")
    email: EmailStr = Field(description="Email address")
    phone: str = Field(description="Phone number if present")
    organization: str | None = Field(
        None, description="Organization or company if mentioned"
    )
    role: str | None = Field(None, description="Job title or role if mentioned")


class ContactExtractionOutcome(BaseModel):  # could be made Generic
    """Represents the result of trying to extract contact info."""

    contact_info: ContactInfo  # could be T
    summary: str = Field(
        description="If is_complete is True, a confirmation summary of the extracted information.",
    )


class ExtractorAgent:
    """Contact information extraction agent using Marvin framework."""

    SUPPORTED_CONTENT_TYPES: ClassVar[list[str]] = [
        "text",
        "text/plain",
        "application/json",
    ]

    def __init__(self):
        """Initialize the extractor agent with the necessary instructions."""
        self.instructions = (
            "Politely interrogate the user for their contact information."
            " The schema of the result type implies what things you _need_ to get from the user."
        )

    async def invoke(self, query: str, sessionId: str) -> dict[str, Any]:
        """Process a user query with marvin

        Args:
            query: The user's input text.
            sessionId: The session identifier

        Returns:
            A dictionary describing the outcome and necessary next steps.
        """
        try:
            logger.debug(
                f"[Session: {sessionId}] PID: {os.getpid()} | PyThread: {threading.get_ident()} | Using/Creating MarvinThread ID: {sessionId}"
            )

            result = await marvin.run_async(
                query,
                context={
                    "your personality": self.instructions,
                    "reminder": "Use your memory to help fill out the form",
                },
                thread=marvin.Thread(id=sessionId),
                result_type=ContactExtractionOutcome | ClarifyingQuestion,
            )

            if isinstance(result, ContactExtractionOutcome):
                return {
                    "is_task_complete": True,
                    "require_user_input": False,
                    "content": result.summary,
                    "contact_info": result.contact_info,
                    "data": result,
                }
            else:
                return {
                    "is_task_complete": False,
                    "require_user_input": True,
                    "content": result,
                    "contact_info": None,
                    "data": None,
                }

        except Exception as e:
            logger.exception(f"Error during agent invocation for session {sessionId}")
            return {
                "is_task_complete": False,
                "require_user_input": True,
                "content": f"Sorry, I encountered an error processing your request: {str(e)}",
            }

    async def stream(self, query: str, sessionId: str) -> AsyncIterable[dict[str, Any]]:
        """Stream the response for a user query.

        Args:
            query: The user's input text.
            sessionId: The session identifier.

        Returns:
            An asynchronous iterable of response dictionaries.
        """
        yield {
            "is_task_complete": False,
            "require_user_input": False,
            "content": "Analyzing your text for contact information...",
        }

        yield await self.invoke(query, sessionId)
