from src.graph import graph

def run_graph_test():
    print("🕸️ Starting LangGraph State Machine Test (Advanced Math & Logic)...\n")
    
    # Text with temporal contradictions and math that requires careful extraction
    test_text = """
    Project: Operation Deep Freeze
    Schedule: We start on Dec 1, 2024 and wrap everything up by Oct 15, 2024. 
    (Wait, that's impossible. Let's start on Oct 1 and end on Dec 1 instead).
    
    Billing:
    - Server Maintenance: 2 months at $500/month. Total: $1000.
    - Cloud Storage: 5 units at $45 each. Total: $225.
    - Consultant Fee: 10 hours at $150. Total: $1400. 
    (Wait, 10 * 150 should be 1500, let's fix that calculation).
    
    The final invoice total is $2725.
    """

    initial_state = {
        "raw_text": test_text,
        "current_attempt": 0,
        "validation_errors": [],
        "attempt_count": 0,
        "final_output": None,
        "is_valid": False,
        "warning_flag": False
    }

    print(f"Input Text:\n{test_text.strip()}\n")
    print("-" * 30)

    try:
        # Run the graph
        final_state = graph.invoke(initial_state)
        
        print("\n--- Final Graph State ---")
        print(f"Status: {'✅ Valid' if final_state['is_valid'] else '❌ Invalid'}")
        print(f"Total Attempts: {final_state['attempt_count']}")
        
        if final_state['final_output']:
            output = final_state['final_output']
            print(f"Project: {output.project_name}")
            print(f"Start: {output.start_date} | End: {output.end_date}")
            print("Items:")
            for item in output.items:
                print(f"  - {item.description}: {item.quantity} x {item.unit_price} = {item.total}")
            print(f"Grand Total: {output.grand_total}")
            
        if final_state['warning_flag']:
            print("⚠️ Warning: Max attempts reached without perfect validation.")
            
        if final_state['validation_errors']:
            print(f"Errors encountered: {final_state['validation_errors']}")

    except Exception as e:
        print(f"❌ Graph execution failed: {e}")

if __name__ == "__main__":
    run_graph_test()
