import marvin
from pydantic import BaseModel, Field
from typing import Any, AsyncIterable


class ContactInfo(BaseModel):
    """Structured contact information extracted from text."""

    name: str = Field(description="Person's full name")
    email: str = Field(description="Email address")
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
                "If the input doesn't contain complete contact information, identify what's missing "
                "and ask specific questions to gather that information. "
                "Be precise and only extract what is explicitly mentioned in the text."
            ),
        )

        self.session_states: dict[str, ContactInfo] = {}

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
                # Check if we have partial information from a previous turn
                partial_info = self.session_states.get(sessionId)

                if partial_info:
                    # Extract new info, providing context from previous turn
                    prompt = (
                        f"Update this partial contact information with new details from: '{query}'\n"
                        f"Current information: {partial_info.model_dump_json()}"
                    )

                    # Try to extract a ContactInfo object
                    contact_info = self.agent.run(prompt, result_type=ContactInfo)
                else:
                    # Fresh extraction
                    contact_info = self.agent.run(
                        f"Extract contact information from this text: {query}",
                        result_type=ContactInfo,
                    )

                # Check if we have required fields
                if not contact_info.name or not contact_info.email:
                    # Store the partial information
                    self.session_states[sessionId] = contact_info

                    # Generate a request for more information
                    missing = []
                    if not contact_info.name:
                        missing.append("name")
                    if not contact_info.email:
                        missing.append("email")

                    missing_str = ", ".join(missing)
                    question = self.agent.run(
                        f"I need to collect contact information but I'm missing: {missing_str}. "
                        f"Based on what I know so far: {contact_info.model_dump_json()}, "
                        f"ask a natural question to get the missing information."
                    )

                    return {
                        "is_task_complete": False,
                        "require_user_input": True,
                        "content": question,
                        "contact_info": contact_info,
                    }
                else:
                    if sessionId in self.session_states:
                        del self.session_states[sessionId]

                    # Generate a summary of the complete contact info
                    content = (
                        "Great! I've collected the following contact information:\n\n"
                    )
                    content += f"👤 Name: {contact_info.name}\n"
                    content += f"📧 Email: {contact_info.email}\n"

                    if contact_info.phone:
                        content += f"📱 Phone: {contact_info.phone}\n"
                    if contact_info.organization:
                        content += f"🏢 Organization: {contact_info.organization}\n"
                    if contact_info.role:
                        content += f"🧑‍💼 Role: {contact_info.role}\n"

                    return {
                        "is_task_complete": True,
                        "require_user_input": False,
                        "content": content,
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
