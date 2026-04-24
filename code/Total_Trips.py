import pandas as pd
import pytesseract
from pdf2image import convert_from_bytes
import requests
import io
import re
import os
from PIL import Image, ImageOps

# --- Configuration ---
pytesseract.pytesseract.tesseract_cmd = r'D:\Python\tesseract.exe'
POPPLER_PATH = r'D:\Python\Release-25.12.0-0\poppler-25.12.0\Library\bin'

def extract_trip_from_pdf(route_id, direction):
    """Downloads PDF and uses optimized OCR to find 'Total Trips'."""
    url = f"https://www.cda.gov.pk/Assets/metro_transit_route/{route_id}_{direction}.pdf"
    
    # Using a browser-like header to prevent server-side blocking
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        
        # Verify the content is a valid PDF
        if not response.content.startswith(b'%PDF'):
            return "N/A"

        # DPI=300 and Grayscale for accurate character recognition
        images = convert_from_bytes(response.content, first_page=1, last_page=1, 
                                    poppler_path=POPPLER_PATH, dpi=300)
        
        if images:
            img = images[0].convert('L')
            img = ImageOps.autocontrast(img)
            
            # Crop to the top-left summary table
            width, height = img.size
            header_crop = img.crop((0, 0, width // 2, height // 4)) 
            
            # Extract text with Page Segmentation Mode 6
            raw_text = pytesseract.image_to_string(header_crop, config='--psm 6')
            
            # Extract number following the 'Total Trips' pattern
            for line in raw_text.split('\n'):
                if "Total" in line and "Trips" in line:
                    numbers = re.findall(r'\d+', line)
                    if numbers:
                        return numbers[-1]
                        
    except Exception:
        pass
    
    return "0"

def run_total_trips_batch():
    input_file = 'data/routes.csv'
    output_file = 'data/Total_Trips.csv'

    if not os.path.exists(input_file):
        print(f"❌ Error: {input_file} not found.")
        return

    # Load unique Route IDs from your base scraper data
    df_base = pd.read_csv(input_file)
    unique_ids = df_base['RouteID'].unique()
    
    results = []
    print(f"🚀 Starting Extraction for {len(unique_ids)} routes (Forward & Backward)...")

    for r_id in unique_ids:
        for direction in ['Forward', 'Backward']:
            print(f"  Processing {r_id}_{direction}...", end=" ", flush=True)
            
            trip_count = extract_trip_from_pdf(r_id, direction)
            print(f"Result: {trip_count}")
            
            results.append({
                "Route_ID": r_id,
                "Direction": direction,
                "Total_Trips": trip_count
            })

    # Save to the specific CSV file
    df_final = pd.DataFrame(results)
    df_final.to_csv(output_file, index=False)
    print(f"\n✅ SUCCESS! Trip data saved to {output_file}")

if __name__ == "__main__":
    run_total_trips_batch()