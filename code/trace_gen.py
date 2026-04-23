import pandas as pd
import pm4py
import os
import re
from datetime import datetime

def clean_time_string(time_str):
    """Fixes common OCR errors in time strings."""
    if pd.isna(time_str) or time_str == "":
        return "00:00:00"
    
    # 1. Replace the word 'Colon' or other symbols with actual colons
    cleaned = str(time_str).replace('Colon', ':').replace(';', ':').replace('.', ':')
    
    # 2. Remove any non-numeric and non-colon characters (like accidental letters)
    cleaned = re.sub(r'[^0-9:]', '', cleaned)
    
    # 3. Ensure it follows HH:MM:SS format
    # If OCR missed a colon, this is a fallback (basic validation)
    if len(cleaned.split(':')) < 3:
        return "00:00:00" 
        
    return cleaned

def generate_xes():
    input_dir = 'data/extracted_routes'
    output_xes = 'data/merged_event_log.xes'
    all_dfs = []

    print("Merging and cleaning CSVs for XES generation...")

    for file in os.listdir(input_dir):
        if file.endswith(".csv"):
            df = pd.read_csv(os.path.join(input_dir, file))
            parts = file.replace(".csv", "").split("_")
            # Case ID must be the route and direction [cite: 23]
            df['case:concept:name'] = f"{parts[1]}_{parts[2]}" 
            all_dfs.append(df)

    if not all_dfs:
        print("No CSVs found!")
        return

    event_log_df = pd.concat(all_dfs, ignore_index=True)

    # Apply the cleaning function to ArrivalTime
    event_log_df['ArrivalTime'] = event_log_df['ArrivalTime'].apply(clean_time_string)

    # Standard XES Column Mapping 
    event_log_df.rename(columns={
        'StopName': 'concept:name',
        'ArrivalTime': 'time:timestamp'
    }, inplace=True)

    # Convert to datetime with today's date
    today = datetime.now().strftime('%Y-%m-%d')
    
    # We use format='mixed' as suggested by your error to be safe
    event_log_df['time:timestamp'] = pd.to_datetime(
        today + ' ' + event_log_df['time:timestamp'], 
        format='mixed', 
        errors='coerce'
    )

    # Remove any rows where time failed to parse even after cleaning
    event_log_df.dropna(subset=['time:timestamp'], inplace=True)

    # Export to XES [cite: 44, 46]
    print(f"Exporting {len(event_log_df)} events to {output_xes}...")
    pm4py.write_xes(event_log_df, output_xes)
    print("SUCCESS: XES file created.")

if __name__ == "__main__":
    generate_xes()