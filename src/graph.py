from typing import Literal, TypedDict, List, Optional
from langgraph.graph import StateGraph, END
from src.schemas import ExtractorState, StructuredOutput
from src.llm_client import extract_structured_data
from pydantic import ValidationError

# Define the State as a TypedDict for LangGraph compatibility, 
# matching the fields in our ExtractorState model.
class AgentState(TypedDict):
    raw_text: str
    current_attempt: int
    validation_errors: List[str]
    attempt_count: int
    final_output: Optional[StructuredOutput]
    is_valid: bool
    warning_flag: bool

def extract_node(state: AgentState) -> AgentState:
    """Calls the LLM to extract data based on raw text and previous errors."""
    print(f"--- Attempt {state['attempt_count'] + 1}: Extracting Data ---")
    
    try:
        # Pass previous validation errors to the LLM for self-correction
        result = extract_structured_data(
            text=state["raw_text"],
            schema=StructuredOutput,
            errors=state["validation_errors"]
        )
        return {
            **state,
            "final_output": result,
            "attempt_count": state["attempt_count"] + 1,
            "current_attempt": state["attempt_count"] + 1
        }
    except Exception as e:
        # If the LLM call itself fails (e.g. rate limit), track that as an error
        return {
            **state,
            "validation_errors": [str(e)],
            "attempt_count": state["attempt_count"] + 1
        }

def validate_node(state: AgentState) -> AgentState:
    """Validates the LLM output against the Pydantic schema."""
    print("--- Validating Output ---")
    
    output = state.get("final_output")
    if not output:
        return {**state, "is_valid": False, "validation_errors": ["No output received from LLM"]}

    try:
        # Although Instructor handles basic validation, we re-verify or perform custom checks here
        # For this example, if the LLM returned it, it's likely valid, 
        # but we could add cross-field validation here.
        StructuredOutput.model_validate(output)
        return {**state, "is_valid": True, "validation_errors": []}
    except ValidationError as e:
        errors = [f"{err['loc']}: {err['msg']}" for err in e.errors()]
        return {**state, "is_valid": False, "validation_errors": errors}

def should_continue(state: AgentState) -> Literal["extract", "end"]:
    """Determines if the loop should retry or terminate."""
    if state["is_valid"]:
        return "end"
    
    if state["attempt_count"] >= 3:
        print("--- Max Attempts Reached ---")
        state["warning_flag"] = True
        return "end"
    
    print(f"--- Retrying due to errors: {state['validation_errors']} ---")
    return "extract"

# Initialize the Graph
builder = StateGraph(AgentState)

# Define Nodes
builder.add_node("extract", extract_node)
builder.add_node("validate", validate_node)

# Set Entry Point
builder.set_entry_point("extract")

# Define Edges
builder.add_edge("extract", "validate")
builder.add_conditional_edges(
    "validate",
    should_continue,
    {
        "extract": "extract",
        "end": END
    }
)

# Compile
graph = builder.compile()
