import os
from dotenv import load_dotenv
from src.llm_client import extract_structured_data
from src.schemas import StructuredOutput
from pydantic import ValidationError

# Load .env file
load_dotenv()

def run_test():
    print("🚀 Starting Extraction Test...\n")
    
    # Check if API Key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not found in environment.")
        return

    test_text = """
    Meeting Notes - 2024-05-15
    Participants: John Doe
    The project is moving forward. 
    We need to:
    1. Update the documentation
    2. Fix the login bug
    3. Review the security protocol
    """

    print(f"Input Text:\n{test_text}")
    print("-" * 30)

    try:
        # Perform extraction
        result = extract_structured_data(
            text=test_text,
            schema=StructuredOutput
        )
        
        print("✅ Extraction Successful!")
        print(f"Name: {result.name}")
        print(f"Date: {result.date}")
        print(f"Action Items: {result.action_items}")
        
    except ValidationError as e:
        print("❌ Validation Error:")
        print(e)
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")

if __name__ == "__main__":
    run_test()
