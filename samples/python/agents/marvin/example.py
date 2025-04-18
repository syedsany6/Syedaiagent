import os
import uuid
from agent import ExtractorAgent

# Set up API key (in a real application, you would use environment variables)
os.environ["OPENAI_API_KEY"] = "your-openai-api-key"  # Replace with your actual key

# Create the extractor agent
agent = ExtractorAgent()

# Generate a unique session ID
session_id = str(uuid.uuid4())

# Example 1: Process a simple text with contact information
sample_text = "Hi, my name is Jane Smith and I'm a Software Engineer at TechCorp. You can reach me at jane.smith@example.com or call me at (555) 123-4567."
print("\nInput text:")
print(sample_text)

response = agent.invoke(sample_text, session_id)

print("\nExtracted information:")
print(response["content"])

# Example 2: Text without contact information
no_contact_text = "I'm looking for information about machine learning algorithms."
print("\nInput text:")
print(no_contact_text)

response = agent.invoke(no_contact_text, session_id)

print("\nResponse:")
print(response["content"])

# Example 3: Partial information
partial_text = "Please contact our HR department at hr@company.com"
print("\nInput text:")
print(partial_text)

response = agent.invoke(partial_text, session_id)

print("\nResponse:")
print(response["content"])
