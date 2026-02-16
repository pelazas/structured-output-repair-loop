import os
from dotenv import load_dotenv
from src.graph import graph
from src.input_handler import load_input

# Load environment variables (API Keys)
load_dotenv()

def run_project_test(file_path: str):
    print(f"🚀 Processing: {file_path}")
    print("=" * 50)
    
    if not os.path.exists(file_path):
        print(f"❌ Error: File '{file_path}' not found.")
        return

    # 1. Load and extract text using our unified input handler
    try:
        raw_text = load_input(file_path)
    except Exception as e:
        print(f"❌ Failed to read file: {e}")
        return

    # 2. Prepare initial state for LangGraph
    initial_state = {
        "raw_text": raw_text,
        "current_attempt": 0,
        "validation_errors": [],
        "attempt_count": 0,
        "final_output": None,
        "is_valid": False,
        "warning_flag": False
    }

    # 3. Run the Extract -> Validate -> Repair state machine
    try:
        final_state = graph.invoke(initial_state)
        
        print("\n--- Execution Summary ---")
        print(f"Final Status: {'✅ VALID' if final_state['is_valid'] else '❌ INVALID'}")
        print(f"Total Attempts: {final_state['attempt_count']}")
        
        if final_state['final_output']:
            output = final_state['final_output']
            print("\n--- Extracted Data ---")
            print(f"Project Name: {output.project_name}")
            print(f"Start Date:   {output.start_date}")
            print(f"End Date:     {output.end_date}")
            print("\nInvoiced Items:")
            for item in output.items:
                print(f"  - {item.description:25} | {item.quantity} x ${item.unit_price:>8.2f} = ${item.total:>10.2f}")
                print(f"    Reasoning: {item.math_reasoning}")
            print("-" * 30)
            print(f"Grand Total:  ${output.grand_total:>10.2f}")
            if output.correction_notes:
                print(f"\nCorrection Notes: {output.correction_notes}")
            
        if final_state['warning_flag']:
            print("\n⚠️ Warning: Maximum retry attempts reached.")
            
        if final_state['validation_errors']:
            print("\nFinal Validation Errors:")
            for err in final_state['validation_errors']:
                print(f"  - {err}")

    except Exception as e:
        print(f"❌ Graph execution failed: {e}")

if __name__ == "__main__":
    target = "data/project_2.txt"
    run_project_test(target)
