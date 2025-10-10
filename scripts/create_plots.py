import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import os
import re
import traceback

# --- Helper Functions (Unchanged) ---
def get_nice_interval(data_range):
    if data_range <= 0: return 0.1
    raw_interval = data_range / 7
    nice_intervals = [0.01, 0.02, 0.025, 0.05, 0.1, 0.2, 0.25, 0.5, 1.0]
    for interval in nice_intervals:
        if interval >= raw_interval:
            return interval
    return 0.1

def generate_filename(column_name):
    # --- This is the original logic for generating the base filename ---
    filename = ''
    parts = re.findall(r'\b[A-Z]{2,}\b', column_name)
    if not parts:
        parts = re.findall(r'\b[A-Za-z]+(?:\s+[A-Za-z]+)*\b', column_name)
        if parts: 
            filename = '_'.join(parts[0].split()[:2]) + '.png'
        else: 
            filename = 'plot.png'
    else:
        filename = '_'.join(parts) + '.png'

    # --- Here is the new condition ---
    # If the original column name contains '++', insert '++' into the generated filename.
    if '++' in column_name:
        filename = filename.replace('.png', '++.png')
        
    return filename
def get_user_input(prompt):
    response = input(prompt)
    if response.lower() == 'back':
        return 'BACK'
    return response

# --- Plotting Functions ---
def create_single_bar_plot(df, xaxis_col, yaxis_col, output_filepath, y_min_interactive=None, y_max_interactive=None, tick_interval_interactive=None):
    """Generates a single bar chart with no geomean label."""
    y_data = pd.to_numeric(df[yaxis_col], errors='coerce').fillna(0)
    x_labels = df[xaxis_col].astype(str)
    
    clipping_threshold = y_max_interactive
    clipped_y_data = y_data.clip(upper=clipping_threshold)

    fig, ax = plt.subplots(figsize=(10.61, 4.42), layout='constrained')
    geomean_color = '#90EE90'
    default_color = '#ADD8E6'
    colors = [geomean_color if 'Geomean' in label else default_color for label in x_labels]

    rects = ax.bar(x_labels, clipped_y_data, color=colors, edgecolor='black', linewidth=1.2, alpha=0.8)

    ax.set_ylim(bottom=y_min_interactive, top=y_max_interactive)
    if tick_interval_interactive > 0:
        ax.yaxis.set_major_locator(mticker.MultipleLocator(tick_interval_interactive))
    
    ax.set_ylabel("Speedup", fontsize=14)
    ax.set_xlabel("Traces", fontsize=14)
    plt.xticks(rotation=45, ha='right')
    ax.yaxis.grid(True, linestyle='--', alpha=0.7)
    
    ax.set_xlim(-0.8, len(x_labels) - 0.1) # Reduce blank space on left/right of bars
    
    for i, rect in enumerate(rects):
        original_value = y_data.iloc[i]
        if original_value > clipping_threshold:
            ax.annotate(f'{original_value:.2f}',
                        xy=(rect.get_x() + rect.get_width() / 2, rect.get_height()),
                        xytext=(0, 3), textcoords="offset points",
                        ha='center', va='bottom', weight='bold', fontsize=8)

    plt.savefig(output_filepath)


def create_grouped_bar_plot(df, xaxis_col, yaxis_cols, output_filepath_base, y_min_interactive=None, y_max_interactive=None, tick_interval_interactive=None):
    x = np.arange(len(df[xaxis_col]))
    #x_labels = df[xaxis_col].astype(str)
    width = 0.8 / len(yaxis_cols)
    fig, ax = plt.subplots(figsize=(10.61, 4.42), layout='constrained')
    color_palette = ['#729fcf', '#b4c7dc', '#dee6ef', '#8ecae6', '#355269', '#3949ab', '#7986cb', '#1a237e']
    for i, y_col in enumerate(yaxis_cols):
        offset = width * (i - (len(yaxis_cols) - 1) / 2)
        y_data = pd.to_numeric(df[y_col], errors='coerce').fillna(0)
        color = color_palette[i % len(color_palette)]
        cleaned_label = y_col.replace("'s Geomean", "").replace(" Geomean", "").strip()
        rects = ax.bar(x + offset, y_data, width, label=cleaned_label, color=color, edgecolor='black', linewidth=0.5)

    if y_min_interactive is not None and y_max_interactive is not None:
        ax.set_ylim(bottom=y_min_interactive, top=y_max_interactive)
    if tick_interval_interactive is not None and tick_interval_interactive > 0:
        ax.yaxis.set_major_locator(mticker.MultipleLocator(tick_interval_interactive))
    
    ax.set_ylabel('Value', fontsize=14) # Corrected Label
    ax.set_xlabel("Replacement Policies at L2 and LLC", fontsize=14)
    ax.set_xticks(x, df[xaxis_col].astype(str))
    plt.xticks(rotation=45, ha='right')
    ax.legend(loc='upper right')
    ax.yaxis.grid(True, linestyle='--', alpha=0.7)
    
    ax.margins(x=0.01)
    
    cleaned_names = [col.replace("'s Geomean", "").replace(" ", "").strip() for col in yaxis_cols]
    output_filename = '_'.join(cleaned_names) + '.png'
    output_filepath = os.path.join(output_filepath_base, 'plot_preview.png')
    plt.savefig(output_filepath)
    return os.path.join(output_filepath_base, output_filename)

# --- Main Interactive Script Logic ---
if __name__ == "__main__":
    
    state_machine = { 'current_state': 0, 'history': [], 'data': {} }

    def run_state(state_func):
        global state_machine
        result = state_func(state_machine['data'])
        if result == 'BACK':
            if state_machine['history']: state_machine['current_state'] = state_machine['history'].pop()
        elif result == 'FINISHED': state_machine['current_state'] = 999
        elif result is not None:
            state_machine['history'].append(state_machine['current_state'])
            state_machine['current_state'] += 1
            state_machine['data'].update(result)

    def state_0_welcome(data):
        print("--- Interactive Plot Generator ---"); return {}

    def state_1_select_plot_type(data):
        response = get_user_input("\nDo you want a 'single' or 'grouped' bar chart? ")
        if response in ['single', 'grouped']: return {'plot_type': response}
        elif response == 'BACK': return 'BACK'
        else: print("Invalid input.")

    def state_2_select_sheet(data):
        file_name = 'rnd.xlsx'
        if not os.path.exists(file_name):
            print(f"Error: The file '{file_name}' was not found."); return None
        try:
            xls = pd.ExcelFile(file_name, engine='openpyxl')
            sheet_names = [sheet for sheet in xls.sheet_names if not sheet.startswith('raw_')]
            print("\n--- Available Sheets ---")
            for i, sheet in enumerate(sheet_names): print(f"[{i+1}] {sheet}")
            response = get_user_input("Please choose a sheet number to plot: ")
            if response == 'BACK': return 'BACK'
            choice = int(response) - 1
            if 0 <= choice < len(sheet_names):
                return {'sheet_name': sheet_names[choice], 'file_name': file_name}
            else: print("Invalid choice.")
        except (ValueError, IndexError): print("Invalid input.")
        except Exception as e:
            print(f"An error occurred while opening the Excel file: {e}"); return None

    def state_3_get_header_row(data):
        response = get_user_input("\nWhich row contains column headers? (e.g., 3): ")
        if response == 'BACK': return 'BACK'
        try: return {'header_row': int(response) - 1}
        except ValueError: print("Please enter a valid number.")

    def state_4_multi_plot_loop(data):
        try:
            output_directory = os.path.join("..", "results", "Graph", data['sheet_name'].replace(" ", "_").replace(".", ""))
            os.makedirs(output_directory, exist_ok=True)
            print(f"\nOutput will be saved in: {output_directory}")

            while True:
                df_preview = pd.read_excel(data['file_name'], sheet_name=data['sheet_name'], header=data['header_row'], nrows=0, engine='openpyxl')
                columns = [str(c).replace('\n', ' ').strip() for c in df_preview.columns]
                print("\n--- Available Columns ---")
                for i, col in enumerate(columns): print(f"[{i}] {col}")
                
                response = get_user_input("Enter the number for the X-axis column: ")
                if response == 'BACK': continue
                xaxis_col_index = int(response)

                yaxis_col_indices = []
                if data['plot_type'] == 'single':
                    response = get_user_input("Enter number for the Y-axis column: ")
                    if response == 'BACK': continue
                    yaxis_col_indices.append(int(response))
                else: # grouped
                    response = get_user_input("How many Y-axis columns to group? ")
                    if response == 'BACK': continue
                    for i in range(int(response)):
                        res_bar = get_user_input(f"Enter column number for bar #{i+1}: ")
                        if res_bar == 'BACK': break
                        yaxis_col_indices.append(int(res_bar))
                    if res_bar == 'BACK': continue
                
                response = get_user_input("\nEnter the starting data row number: ")
                if response == 'BACK': continue
                start_row = int(response)
                response = get_user_input("Enter the ending data row number: ")
                if response == 'BACK': continue
                end_row = int(response)

                header, skiprows, nrows = data['header_row'], start_row - 1, end_row - start_row + 1
                
                # --- THIS IS THE FIX ---
                # Load the data by telling pandas where the header is directly.
                df_full = pd.read_excel(data['file_name'], sheet_name=data['sheet_name'], header=header, engine='openpyxl')
                df_full.columns = [str(c).replace('\n', ' ').strip() for c in df_full.columns]

                # Slice the dataframe based on the original Excel row numbers.
                start_slice = start_row - (header + 2) # Adjust for 0-indexing and header position
                end_slice = start_slice + nrows
                if start_slice < 0:
                     print("\nError: 'starting row' must be after the 'header row'."); continue
                df_original = df_full.iloc[start_slice : end_slice].copy()
                # --- END FIX ---
                
                cleaned_columns = df_original.columns.tolist()
                yaxis_cols = [cleaned_columns[i] for i in yaxis_col_indices]
                xaxis_col = cleaned_columns[xaxis_col_index]

                while True:
                    df = df_original.copy()
                    preview_path = os.path.join(output_directory, "plot_preview.png")

                    if data['plot_type'] == 'single':
                        if 'Geomean' not in df[xaxis_col].astype(str).values:
                            numeric_data = pd.to_numeric(df[yaxis_cols[0]], errors='coerce')
                            if not numeric_data.dropna().empty:
                                geomean_value = np.exp(np.log(numeric_data.dropna()).mean())
                                geomean_row = pd.DataFrame({xaxis_col: ['Geomean'], yaxis_cols[0]: [geomean_value]})
                                df = pd.concat([df, geomean_row], ignore_index=True)

                        y_col_data = pd.to_numeric(df[yaxis_cols[0]], errors='coerce').dropna()
                        min_val = y_col_data.min()
                        prompt_min = f"\nThe min speedup is {min_val:.4f}. Enter Y-axis minimum (or Enter): "
                        response = get_user_input(prompt_min)
                        y_min_final = float(response) if response else min_val
                        top_7 = y_col_data.sort_values(ascending=False).head(7)
                        print("\n--- Top 7 Values ---\n" + top_7.to_string(header=False) + "\n--------------------")
                        response = get_user_input("Enter desired Y-axis maximum: ")
                        y_max_final = float(response)
                        response = get_user_input("Enter desired Y-axis tick interval: ")
                        tick_interval_final = float(response)
                        
                        create_single_bar_plot(df, xaxis_col, yaxis_cols[0], preview_path, y_min_final, y_max_final, tick_interval_final)
                        final_filename = generate_filename(yaxis_cols[0])
                        final_path = os.path.join(output_directory, final_filename)
                    else:
                        print("\n--- Data Statistics for Y-Axis Columns ---")
                        for col in yaxis_cols:
                            col_data = pd.to_numeric(df[col], errors='coerce').dropna()
                            if not col_data.empty: print(f"- '{col}': Min={col_data.min():.4f}, Max={col_data.max():.4f}")
                        
                        response = get_user_input("\nEnter overall Y-axis minimum: ")
                        y_min_final = float(response) if response else None
                        response = get_user_input("Enter overall Y-axis maximum: ")
                        y_max_final = float(response) if response else None
                        response = get_user_input("Enter overall Y-axis tick interval: ")
                        tick_interval_final = float(response) if response else None
                        
                        final_path = create_grouped_bar_plot(df, xaxis_col, yaxis_cols, output_directory, y_min_final, y_max_final, tick_interval_final)
                    
                    print(f"\n>>>> A preview has been saved to: {preview_path}")
                    print(">>>> Please open the file to view it.")
                    action = get_user_input("What would you like to do? (save / change / discard): ").lower()

                    if action == 'save':
                        if os.path.exists(final_path): os.remove(final_path)
                        os.rename(preview_path, final_path)
                        print(f"Plot saved successfully as '{final_path}'")
                        break
                    elif action == 'change':
                        print("\n--- Let's adjust the settings. ---")
                        if os.path.exists(preview_path): os.remove(preview_path)
                        continue
                    else:
                        print("Discarding plot.")
                        if os.path.exists(preview_path): os.remove(preview_path)
                        break
                
                another_plot_response = get_user_input("\nCreate another plot from this sheet? (yes/no): ")
                if another_plot_response.lower() != 'yes':
                    break
            
            return 'FINISHED'
        except Exception as e:
            print(f"\nAn unexpected error occurred: {e}")
            traceback.print_exc()

    states = [
        state_0_welcome,
        state_1_select_plot_type,
        state_2_select_sheet,
        state_3_get_header_row,
        state_4_multi_plot_loop,
    ]
    
    while state_machine['current_state'] < len(states):
        current_function = states[state_machine['current_state']]
        run_state(current_function)

