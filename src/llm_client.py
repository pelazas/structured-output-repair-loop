import os
import instructor
from openai import OpenAI
from typing import Type, TypeVar, List, Optional, Any
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

T = TypeVar("T", bound=BaseModel)

class LLMClient:
    def __init__(self):
        # Using OpenAI client as the underlying engine for Instructor/Gemini
        # Adjust base_url and api_key as needed for your specific SDK setup
        self.api_key = os.getenv("OPENAI_API_KEY")
        
        # Initialize the Patch specifically for structured output
        # Instructor's patching allows LLMs to return complex Pydantic objects
        self.client = instructor.patch(
            OpenAI(api_key=self.api_key),
            mode=instructor.Mode.JSON
        )

    def _build_prompt(self, raw_text: str, previous_errors: Optional[List[str]] = None) -> str:
        """Constructs a prompt that includes feedback for self-correction."""
        prompt = f"Extract structured information from the following text:\n\n{raw_text}\n"
        
        if previous_errors:
            prompt += "\n### Previous Validation Errors found in your last output:\n"
            for error in previous_errors:
                prompt += f"- {error}\n"
            prompt += "\nPlease correct these errors in your new response."
            
        return prompt

    def extract_structured_data(
        self, 
        text: str, 
        response_model: Type[T], 
        errors: Optional[List[str]] = None,
        max_retries: int = 3
    ) -> T:
        """
        Extracts data using the specified Pydantic schema.
        Automatically handles schema adherence via Instructor.
        """
        prompt = self._build_prompt(text, errors)
        
        try:
            # Instructor handles the mapping of the model to the JSON schema
            # and performs retries if the JSON is malformed
            return self.client.chat.completions.create(
                model="gpt-4o-mini",  # Using a cheaper but capable model
                response_model=response_model,
                messages=[
                    {"role": "system", "content": "You are a precise data extraction assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_retries=max_retries
            )
        except Exception as e:
            # Graceful error handling for API issues
            print(f"Error during extraction: {e}")
            raise

def extract_structured_data(text: str, schema: Type[T], errors: Optional[List[str]] = None) -> T:
    """Helper function to perform extraction."""
    client = LLMClient()
    return client.extract_structured_data(text, schema, errors)
