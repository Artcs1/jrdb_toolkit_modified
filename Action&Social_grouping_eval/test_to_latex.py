import csv
import sys

def create_latex_table(data, table_name, caption, label):
    """
    Create a LaTeX table from data.
    
    Parameters:
    - data: list of rows (including header)
    - table_name: name for the table
    - caption: table caption
    - label: table label for referencing
    """
    
    if not data or len(data) <= 1:  # No data rows
        return ""
    
    # Get number of columns from header
    num_cols = len(data[0])
    
    # Generate column alignment (left for first column, centered for rest)
    col_alignment = 'l' + 'c' * (num_cols - 1)
    
    # Find maximum values for each numeric column (skip first column - names)
    max_values = [None] * num_cols  # Initialize with None
    
    for col_idx in range(1, num_cols):  # Start from 1 to skip name column
        col_values = []
        for row in data[1:]:  # Skip header
            if len(row) > col_idx:
                try:
                    value = float(row[col_idx])
                    col_values.append(value)
                except ValueError:
                    pass  # Skip non-numeric values
        
        if col_values:
            max_values[col_idx] = max(col_values)
    
    # Generate LaTeX table
    latex_output = []
    latex_output.append("\\begin{table}[htbp]")
    latex_output.append("\\centering")
    latex_output.append(f"\\caption{{{caption}}}")
    latex_output.append(f"\\label{{{label}}}")
    latex_output.append(f"\\begin{{tabular}}{{{col_alignment}}}")
    latex_output.append("\\hline")
    
    # Header row - escape underscores
    header = [col.replace('_', '\\_') for col in data[0]]
    latex_output.append(" & ".join(header) + " \\\\")
    latex_output.append("\\hline")
    
    # Data rows
    for row in data[1:]:
        formatted_row = []
        
        for col_idx, cell in enumerate(row):
            if col_idx == 0:  # First column (names)
                # Clean up the first column (remove common prefixes/suffixes)
                name = cell.replace('results_full_', '').replace('results_', '')
                name = name.replace('.txt', '').replace('.csv', '')
                # Escape underscores for LaTeX
                name = name.replace('_', '\\_')
                formatted_row.append(name)
            else:  # Numeric columns
                try:
                    value = float(cell)
                    # Check if this is the maximum value for this column
                    if max_values[col_idx] is not None and abs(value - max_values[col_idx]) < 1e-9:
                        formatted_row.append(f"\\textbf{{{cell}}}")
                    else:
                        formatted_row.append(cell)
                except ValueError:
                    # Not a number, just escape underscores
                    formatted_row.append(cell.replace('_', '\\_'))
        
        # Ensure row has the same number of columns as header
        if len(formatted_row) < num_cols:
            formatted_row.extend([''] * (num_cols - len(formatted_row)))
        elif len(formatted_row) > num_cols:
            formatted_row = formatted_row[:num_cols]
        
        latex_output.append(" & ".join(formatted_row) + " \\\\")
    
    latex_output.append("\\hline")
    latex_output.append("\\end{tabular}")
    latex_output.append("\\end{table}")
    
    return "\n".join(latex_output)


def csv_to_latex(input_file, output_file='table.tex'):
    """
    Convert a CSV file to LaTeX tables, separating results_ and results_full_ entries.
    
    Parameters:
    - input_file: path to the CSV file
    - output_file: path to save the LaTeX output
    """
    
    # Read the CSV file
    try:
        with open(input_file, 'r') as f:
            reader = csv.reader(f)
            data = list(reader)
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.")
        return
    except Exception as e:
        print(f"Error reading file: {e}")
        return
    
    if not data:
        print("Error: CSV file is empty.")
        return
    
    # Separate data into two groups
    header = data[0]
    results_data = [header]
    results_full_data = [header]
    
    for row in data[1:]:
        if len(row) > 0:
            name = row[0]
            if name.startswith('results_full_'):
                results_full_data.append(row)
            elif name.startswith('results_'):
                results_data.append(row)
    
    # Generate LaTeX tables
    latex_output = []
    
    # Table 1: results_
    if len(results_data) > 1:  # Has data beyond header
        table1 = create_latex_table(
            results_data, 
            "results", 
            "Results (Standard)", 
            "tab:results_standard"
        )
        latex_output.append(table1)
    
    # Add spacing between tables
    if len(results_data) > 1 and len(results_full_data) > 1:
        latex_output.append("\n\n")
    
    # Table 2: results_full_
    if len(results_full_data) > 1:  # Has data beyond header
        table2 = create_latex_table(
            results_full_data, 
            "results_full", 
            "Results (Full)", 
            "tab:results_full"
        )
        latex_output.append(table2)
    
    # Save to file
    latex_code = "\n".join(latex_output)
    try:
        with open(output_file, 'w') as f:
            f.write(latex_code)
        print(f"LaTeX tables successfully saved to '{output_file}'")
        print(f"Table 1 (results_): {len(results_data)-1} rows")
        print(f"Table 2 (results_full_): {len(results_full_data)-1} rows")
        print("\nPreview:")
        print(latex_code)
    except Exception as e:
        print(f"Error writing output file: {e}")

# Main execution
if __name__ == "__main__":
    # Check if filename is provided as command line argument
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else 'table.tex'
    else:
        # Default or prompt for filename
        input_file = input("Enter the CSV/TXT file path: ").strip()
        output_file = input("Enter output file name (default: table.tex): ").strip()
        if not output_file:
            output_file = 'table.tex'
    
    csv_to_latex(input_file, output_file)
