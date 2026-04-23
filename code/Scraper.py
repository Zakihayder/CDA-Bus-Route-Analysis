import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def scrape_cda_final():
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920,1080")
    # chrome_options.add_argument("--headless") # Optional: run without browser window
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    url = "https://www.cda.gov.pk/cdaTransitMap#gsc.tab=0"
    
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 20)

        # 1. Wait for the tab pane seen in your screenshot to be visible
        wait.until(EC.visibility_of_element_located((By.ID, "pills-home")))

        route_data = []
        # 2. Target the specific table from your screenshot
        table = driver.find_element(By.CSS_SELECTOR, "table.table-bordered")
        rows = table.find_elements(By.TAG_NAME, "tr")
        
        current_id = ""
        current_name = ""

        for row in rows:
            cols = row.find_elements(By.TAG_NAME, "td")
            
            # Check for main row (has 6 columns based on your screenshot)
            if len(cols) >= 5:
                # Based on image_f9c1da.png:
                # col[1] = Route ID (FR-01)
                # col[2] = Route Name (NUST... to Khanna Pul)
                # col[3] = Direction
                # col[4] = Headway (01:00:00)
                current_id = cols[1].text.strip()
                current_name = cols[2].text.strip()
                direction = cols[3].text.strip()
                headway = cols[4].text.strip()
            
            # Check for the second direction row (usually 2-3 columns)
            elif len(cols) >= 2:
                direction = cols[0].text.strip()
                headway = cols[1].text.strip()
            
            else:
                continue

            if current_id and "FR-" in current_id:
                route_data.append({
                    "RouteID": current_id,
                    "RouteName": current_name,
                    "Direction": direction,
                    "Headway": headway
                })

        # Save Logic
        output_dir = 'data'
        if not os.path.exists(output_dir): os.makedirs(output_dir)
        
        df = pd.DataFrame(route_data)
        df.to_csv(os.path.join(output_dir, 'routes.csv'), index=False)
        print(f"Success! Scraped {len(df)} route entries.")

    except Exception as e:
        print(f"Scraping failed: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    scrape_cda_final()