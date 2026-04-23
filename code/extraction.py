import os
import pandas as pd
import pytesseract
from pdf2image import convert_from_bytes
import requests
import io
import time

# Configuration - Ensure these paths are correct for your machine
pytesseract.pytesseract.tesseract_cmd = r'D:\Python\tesseract.exe'
POPPLER_PATH = r'D:\Python\Release-25.12.0-0\poppler-25.12.0\Library\bin' # Update to your poppler bin path

def extract_all_routes():
    input_csv = 'data/routes.csv'
    output_dir = 'data/extracted_routes'
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created folder: {output_dir}")

    # Load Route IDs from your base scraper
    base_df = pd.read_csv(input_csv)
    route_ids = base_df['RouteID'].unique()

    for r_id in route_ids:
        for direction in ['Forward', 'Backward']:
            filename = f"Route_{r_id}_{direction}.csv"
            save_path = os.path.join(output_dir, filename)
            
            # Skip if already processed to save time
            if os.path.exists(save_path):
                print(f"Skipping {filename}, already exists.")
                continue

            pdf_url = f"https://www.cda.gov.pk/Assets/metro_transit_route/{r_id}_{direction}.pdf"
            print(f"Processing: {r_id} {direction}...")
            
            try:
                response = requests.get(pdf_url, timeout=20)
                if response.status_code != 200:
                    print(f"  - PDF not found for {r_id} {direction}")
                    continue

                images = convert_from_bytes(response.content, poppler_path=POPPLER_PATH)
                extracted_rows = []
                
                for image in images:
                    text = pytesseract.image_to_string(image, config='--psm 6')
                    lines = text.split('\n')
                    
                    for line in lines:
                        parts = line.split()
                        # Matching pattern: [Stop Name] [ArrivalTime] [DepartureTime]
                        if len(parts) >= 3 and ":" in parts[-1] and ":" in parts[-2]:
                            extracted_rows.append({
                                "StopName": " ".join(parts[:-2]),
                                "ArrivalTime": parts[-2],
                                "DepartureTime": parts[-1]
                            })
                
                if extracted_rows:
                    df = pd.DataFrame(extracted_rows)
                    df.to_csv(save_path, index=False)
                    print(f"  [✔] Saved {len(df)} stops to {filename}")
                
                # Sleep to avoid getting blocked by the CDA server
                time.sleep(1)

            except Exception as e:
                print(f"  [!] Error on {r_id}: {e}")

if __name__ == "__main__":
    extract_all_routes()