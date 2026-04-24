import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def scrape_cda_base():
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    url = "https://www.cda.gov.pk/cdaTransitMap#gsc.tab=0"
    
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 20)
        # Wait for the main table container
        wait.until(EC.visibility_of_element_located((By.ID, "pills-home")))

        route_data = []
        table = driver.find_element(By.CSS_SELECTOR, "table.table-bordered")
        rows = table.find_elements(By.TAG_NAME, "tr")
        
        current_id, current_name = "", ""

        for row in rows:
            cols = row.find_elements(By.TAG_NAME, "td")
            if len(cols) >= 5:
                current_id = cols[1].text.strip()
                current_name = cols[2].text.strip()
                direction = cols[3].text.strip()
                headway = cols[4].text.strip()
            elif len(cols) >= 2:
                direction = cols[0].text.strip()
                headway = cols[1].text.strip()
            else: continue

            if current_id and "FR-" in current_id:
                route_data.append({
                    "RouteID": current_id,
                    "RouteName": current_name,
                    "Direction": direction,
                    "Headway": headway
                })

        # Save the base data
        output_dir = 'data'
        if not os.path.exists(output_dir): os.makedirs(output_dir)
        df = pd.DataFrame(route_data)
        df.to_csv(os.path.join(output_dir, 'routes.csv'), index=False)
        print(f"✅ Step 1 Success! Saved {len(df)} routes to routes.csv")

    finally:
        driver.quit()

if __name__ == "__main__":
    scrape_cda_base()