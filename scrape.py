from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from dotenv import load_dotenv
from supabase import create_client
import os, time, random

load_dotenv()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

options = Options()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

products = supabase.table("shopify").select("shopify_id, title").execute().data

for product in products:
    title = product["title"]
    driver.get(f"https://www.aliexpress.com/w/wholesale-{title.replace(' ', '-')}.html")
    time.sleep(random.uniform(4, 6))

    prices = driver.find_elements(By.CSS_SELECTOR, "div.ls_kp")
    competitor_price = prices[0].text if prices else "无结果"
    print(f"{title} → {competitor_price}")

    supabase.table("shopify").update(
        {"competitor_price": competitor_price}
    ).eq("shopify_id", product["shopify_id"]).execute()

driver.quit()
print("✅ 竞品价格已全部更新")