import time
import img2pdf
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

# --- CONFIGURATION ---
PREZI_URL = "YOUR_PREZI_URL_HERE"
TOTAL_SLIDES = 20  # You must count the steps manually beforehand
WAIT_TIME = 3      # Seconds to wait for animation (increase if internet is slow)
OUTPUT_PDF = "presentation.pdf"
# ---------------------

def capture_prezi():
    # 1. Setup the Browser
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    # options.add_argument("--headless") # Keep commented out to see what's happening
    
    driver = webdriver.Chrome(options=options)
    
    try:
        print(f"Opening: {PREZI_URL}")
        driver.get(PREZI_URL)
        
        # 2. Initial Load Wait (Give it time to load the heavy WebGL engine)
        print("Waiting for Prezi to load...")
        time.sleep(15) 
        
        # Optional: Try to locate the 'fullscreen' button or just work in maximized window
        # For simplicity, we interact with the 'body' to send keystrokes
        body = driver.find_element(By.TAG_NAME, "body")
        
        image_files = []

        # 3. Loop through slides
        for i in range(TOTAL_SLIDES):
            print(f"Capturing slide {i+1}/{TOTAL_SLIDES}...")
            
            # Save screenshot
            filename = f"slide_{i:03d}.png"
            driver.save_screenshot(filename)
            image_files.append(filename)
            
            # Navigate Next
            body.send_keys(Keys.ARROW_RIGHT)
            
            # Wait for the transition/zoom animation to settle
            time.sleep(WAIT_TIME)

        print("Capture complete. Generating PDF...")
        
        # 4. Convert to PDF
        with open(OUTPUT_PDF, "wb") as f:
            f.write(img2pdf.convert(image_files))
            
        print(f"Success! Saved to {OUTPUT_PDF}")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    capture_prezi()