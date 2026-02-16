import click
import json
import yaml
from src.input_handler import load_input
from src.graph import graph

def format_output(state, format_type):
    """Formats the final output based on the requested format."""
    output = state.get("final_output")
    if not output:
        return "No structured output generated."

    data = output.model_dump()
    
    if format_type == "json":
        return json.dumps(data, indent=2)
    elif format_type == "yaml":
        return yaml.dump(data, sort_keys=False)
    else:  # Table/Text (Standard)
        lines = []
        lines.append(f"\n{'='*60}")
        lines.append(f"PROJECT: {data['project_name']}")
        lines.append(f"VENDOR:  {data['vendor']['name']} ({data['vendor']['email']})")
        lines.append(f"TAX ID:  {data['vendor']['tax_id']}")
        lines.append(f"DATES:   {data['start_date']} to {data['end_date']}")
        lines.append(f"{'-'*60}")
        lines.append(f"{'Description':<25} | {'Qty':<3} | {'Unit':<8} | {'Total':<10}")
        for item in data['items']:
            tax_mark = "*" if item.get('is_taxable') else " "
            lines.append(f"{item['description'][:25]:<25} | {item['quantity']:<3} | ${item['unit_price']:>7.2f} | ${item['total']:>9.2f}{tax_mark}")
        lines.append(f"{'-'*60}")
        lines.append(f"SUBTOTAL:     ${sum(i['total'] for i in data['items']):>36.2f}")
        lines.append(f"DISCOUNT:    -${data.get('discount_amount', 0):>36.2f}")
        lines.append(f"TAX ({data['tax_rate']*100:>2.0f}%):     +${data['tax_amount']:>36.2f}")
        lines.append(f"GRAND TOTAL:  ${data['grand_total']:>36.2f}")
        lines.append(f"{'='*60}")
        if data.get('correction_notes'):
            lines.append(f"\nNOTES: {data['correction_notes']}")
        return "\n".join(lines)

@click.command()
@click.option('--text', help='Direct text input to process.')
@click.option('--file', type=click.Path(exists=True), help='Path to a .txt, .pdf, or .docx file.')
@click.option('--format', 'output_format', type=click.Choice(['json', 'yaml', 'table']), default='table', help='Output format.')
def main(text, file, output_format):
    """Structured Data Extractor CLI using LangGraph and Instructor."""
    
    input_data = text if text else file
    if not input_data:
        click.echo("Error: Please provide either --text or --file.")
        return

    try:
        raw_text = load_input(input_data)
    except Exception as e:
        click.echo(f"Error loading input: {e}")
        return

    click.echo(f"Processing input (Attempts limit: 3)...")
    
    initial_state = {
        "raw_text": raw_text,
        "current_attempt": 0,
        "validation_errors": [],
        "attempt_count": 0,
        "final_output": None,
        "is_valid": False,
        "warning_flag": False
    }

    try:
        final_state = graph.invoke(initial_state)
        
        # Display Results meta-data
        click.echo(f"Extraction Status: {'DONE' if final_state['is_valid'] else 'FAILED'}")
        click.echo(f"Total Attempts:    {final_state['attempt_count']}")

        if final_state['warning_flag']:
            click.secho("WARNING: Maximum attempts reached. Data may be inconsistent.", fg="yellow", bold=True)

        if final_state['validation_errors']:
            click.secho("\nValidation Errors Encountered:", fg="red")
            for error in final_state['validation_errors']:
                click.echo(f" - {error}")

        # Display formatted output
        click.echo(format_output(final_state, output_format))

    except Exception as e:
        click.echo(f"Execution Error: {e}")

if __name__ == '__main__':
    main()
