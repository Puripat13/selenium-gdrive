from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd
import os
from datetime import datetime

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

driver = webdriver.Chrome(options=options)
driver.get('https://nationalthaiwater.onwr.go.th/waterquality')

WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, ".MuiTable-root tbody tr"))
)

all_data = []
current_date = datetime.today().strftime("%d/%m/%Y")
start_time = time.time() 
while True:
    time.sleep(2)

    tables = driver.find_elements(By.CSS_SELECTOR, ".MuiTable-root")
    
    if len(tables) < 2:
        print("ไม่พบตารางข้อมูลที่ต้องการ")
        break

    data_table = tables[1]
    table_rows = data_table.find_elements(By.CSS_SELECTOR, "tbody tr")

    bad_words = ["<5, >9", "9-May", "5-9"]

    for row in table_rows:
        cols = row.find_elements(By.CSS_SELECTOR, "td")
        data = [col.text.strip() for col in cols if col.text.strip() != ''] 
        
        if not data or len(data) < 3:
            continue

        if data[0] in bad_words:
            continue

        data.append(current_date)
        all_data.append(data)

    next_button_xpath = "//span[@title='Next Page']/button"
    try:
        next_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, next_button_xpath))
        )
        
        if next_button.is_enabled():
            driver.execute_script("arguments[0].click();", next_button)
            print("กด Next Page แล้ว...")
            time.sleep(2)
        else:
            print("ไม่มีหน้าถัดไปแล้ว")
            break

    except Exception:
        print("ไม่พบปุ่ม Next Page หรือปุ่มไม่สามารถกดได้")
        break

if all_data:
    max_columns = max(len(row) for row in all_data)
    all_data = [row + [''] * (max_columns - len(row)) for row in all_data]
    column_names = [f"Column_{i+1}" for i in range(max_columns)]
    
    file_path = "waterquality_report.csv"
    file_exists = os.path.exists(file_path)

    df = pd.DataFrame(all_data, columns=column_names)

    df.to_csv(file_path, mode='a', index=False, encoding="utf-8-sig", header=not file_exists)
    print(f"บันทึกข้อมูลลงไฟล์ {file_path} สำเร็จ!")

driver.quit()
end_time = time.time()
print(f"⏱️ ใช้เวลาในการรันทั้งหมด: {end_time - start_time:.2f} วินาที")

from upload_to_gdrive import upload_file_to_drive as upload_file_to_gdrive

try:
    upload_file_to_gdrive("waterquality_report.csv", "YOUR_FOLDER_ID_HERE")
except Exception as e:
    print("❌ อัปโหลด Google Drive ล้มเหลว:", e)
