import marvin
from pydantic import BaseModel, Field
from typing import Any, AsyncIterable


class ContactInfo(BaseModel):
    """Structured contact information extracted from text."""

    name: str = Field(description="Person's full name")
    email: str | None = Field(None, description="Email address if present")
    phone: str | None = Field(None, description="Phone number if present")
    organization: str | None = Field(
        None, description="Organization or company if mentioned"
    )
    role: str | None = Field(None, description="Job title or role if mentioned")


class ExtractorAgent:
    """Contact information extraction agent using Marvin framework."""

    def __init__(self):
        """Initialize the extractor agent with the necessary instructions."""
        self.agent = marvin.Agent(
            name="Contact Extractor",
            instructions=(
                "You are a specialized assistant for extracting contact information from text. "
                "If the input doesn't contain contact information, politely explain this and ask for relevant input. "
                "Be precise and only extract what is explicitly mentioned in the text."
            ),
        )

    def invoke(self, query: str, sessionId: str) -> dict[str, Any]:
        """Process a user query and return a response with extracted contact information.

        Args:
            query: The user's input text that may contain contact information
            sessionId: A unique identifier for the user session

        Returns:
            A dictionary containing the response information
        """
        try:
            with marvin.Thread(id=sessionId):
                contact_info = self.agent.run(
                    f"Extract contact information from this text: {query}",
                    result_type=ContactInfo,
                )

            return {
                "is_task_complete": True,
                "require_user_input": False,
                "content": "Extracted contact information",
                "contact_info": contact_info,
            }

        except Exception as e:
            return {
                "is_task_complete": False,
                "require_user_input": True,
                "content": f"Error processing request: {str(e)}",
            }

    async def stream(self, query: str, sessionId: str) -> AsyncIterable[dict[str, Any]]:
        """Stream the response for a user query.

        Args:
            query: The user's input text that may contain contact information
            sessionId: A unique identifier for the user session

        Returns:
            An asynchronous iterable of response dictionaries
        """
        # Initial status update
        yield {
            "is_task_complete": False,
            "require_user_input": False,
            "content": "Analyzing your text for contact information...",
        }

        # Invoke the agent and return the final response
        response = self.invoke(query, sessionId)
        yield response

    SUPPORTED_CONTENT_TYPES = ["text", "text/plain", "application/json"]
