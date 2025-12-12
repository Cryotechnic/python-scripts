import time
import os
import cv2
import numpy as np
import pytesseract
from pytesseract import Output
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.colors import Color
from pypdf import PdfWriter, PdfReader
from io import BytesIO

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager

# --- CONFIGURATION DICTIONARY ---
# Format: "Output_Filename.pdf": {"url": "LINK", "slides": NUMBER_OF_SLIDES}
PRESENTATIONS = {
    "Name of presentation.pdf": {
        "url": "your-prezi-link-here",
        "slides": 1
    },
    # Add as many as you want...
}

# GLOBAL SETTINGS
WAIT_TIME = 5            # Seconds per slide
CROP_TOP = 80            # Header removal
CROP_BOTTOM = 80         # Footer removal

# Tesseract Path (Uncomment if needed)
pytesseract.pytesseract.tesseract_cmd = r'S:\Program Files\Tesseract-OCR\tesseract.exe'
# ---------------------

# --- HELPER FUNCTIONS (Image Processing) ---
def get_clean_image_for_ocr(pil_image):
    """Creates high-contrast binary version for OCR."""
    open_cv_image = np.array(pil_image) 
    gray = cv2.cvtColor(open_cv_image, cv2.COLOR_RGB2GRAY)
    binary = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY_INV, 31, 15
    )
    return Image.fromarray(binary)

from reportlab.lib.utils import ImageReader
def flask_image_reader(img_buffer):
    return ImageReader(img_buffer)

def create_overlay_pdf(original_img, ocr_img):
    """Draws original image + invisible OCR text."""
    img_width, img_height = original_img.size
    data = pytesseract.image_to_data(ocr_img, output_type=Output.DICT)
    
    pdf_buffer = BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=(img_width, img_height))
    
    # Draw Background (Original Image)
    img_buffer = BytesIO()
    original_img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    c.drawImage(flask_image_reader(img_buffer), 0, 0, width=img_width, height=img_height)

    # Draw Invisible Text
    c.setFillColor(Color(0, 0, 0, alpha=0)) 
    
    n_boxes = len(data['text'])
    for i in range(n_boxes):
        text = data['text'][i].strip()
        if not text:
            continue
        x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
        pdf_y = img_height - y - h
        c.setFont("Helvetica", h)
        c.drawString(x, pdf_y, text)

    c.save()
    pdf_buffer.seek(0)
    return pdf_buffer

# --- MAIN LOGIC ---
def process_presentation(name, config):
    url = config["url"]
    total_slides = config["slides"]
    
    print(f"\n--- Starting: {name} ({total_slides} slides) ---")
    
    options = webdriver.FirefoxOptions()
    # options.add_argument("--headless") 
    
    driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=options)
    final_pdf_writer = PdfWriter()
    temp_files = []

    try:
        print(f"Opening: {url}")
        driver.get(url)
        print("Waiting for Prezi to load (15s)...")
        time.sleep(15) 
        body = driver.find_element(By.TAG_NAME, "body")

        for i in range(total_slides):
            print(f"[{name}] Processing slide {i+1}/{total_slides}...")
            
            # Capture
            temp_filename = f"temp_{name}_slide_{i}.png"
            driver.save_screenshot(temp_filename)
            temp_files.append(temp_filename)
            
            with Image.open(temp_filename) as img:
                width, height = img.size
                
                # Crop
                crop_box = (0, CROP_TOP, width, height - CROP_BOTTOM)
                cropped_img = img.crop(crop_box)
                
                # OCR Prep & PDF Generation
                ocr_img = get_clean_image_for_ocr(cropped_img)
                page_pdf_bytes = create_overlay_pdf(cropped_img, ocr_img)
                
                page_reader = PdfReader(page_pdf_bytes)
                final_pdf_writer.add_page(page_reader.pages[0])
            
            body.send_keys(Keys.ARROW_RIGHT)
            time.sleep(WAIT_TIME)

        print(f"Saving {name}...")
        with open(name, "wb") as f:
            final_pdf_writer.write(f)
        print(f"Finished: {name}")

    except Exception as e:
        print(f"Error processing {name}: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        driver.quit()
        # Cleanup temp files for this specific presentation
        for file in temp_files:
            try:
                if os.path.exists(file):
                    os.remove(file)
            except Exception:
                pass

def main():
    total_jobs = len(PRESENTATIONS)
    print(f"Queue loaded with {total_jobs} presentations.\n")
    
    for index, (filename, data) in enumerate(PRESENTATIONS.items()):
        print(f"Job {index + 1} of {total_jobs}")
        process_presentation(filename, data)
        
    print("\nAll jobs complete!")

if __name__ == "__main__":
    main()