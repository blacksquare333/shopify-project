```python
import os
import requests
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
SHOPIFY_STORE = os.getenv('SHOPIFY_STORE')
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_access_token():
    url = f"https://{SHOPIFY_STORE}/admin/oauth/access_token"
    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "client_credentials",
    }
    response = requests.post(url, json=payload)

    if response.status_code !=200:
        print(f"❌ 换token失败,状态码: {response.status_code}")
        print(f"返回内容:{response.text}")
        return None
    
    token = response.json().get("access_token")
    print(f"获取token成功: {token}")
    return token

def get_products(access_token):
    url = f"https://{SHOPIFY_STORE}/admin/api/2026-04/products.json"
    headers = {
        "X-Shopify-Access-Token": access_token,
        "Content-Type": "application/json",
    }
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"❌ 获取产品失败,状态码: {response.status_code}")
        print(f"返回内容:{response.text}")
        return None

    products = response.json().get("products")
    print(f"获取产品成功: {len(products)} 个产品")
    
   
    supabase_buffer =[]
    for product in products:
            prompt = f"write a product advertising description in English under 50 words for:{product['title']}"
            
            response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages":[{"role": "user", "content": prompt}]
                }
                )

            description = response.json()['choices'][0]['message']['content']
            print(f"生成产品描述成功: {description}")

            
            supabase_buffer.append({ 
                "shopify_id": product["id"],
                "title": product["title"],
                "description": description,
                "price": product["variants"][0]["price"],
                "status": product["status"],
        
            })
            

    if supabase_buffer:
        supabase.table("shopify").upsert(supabase_buffer, on_conflict="shopify_id").execute()
        print(f"批量导入{len(supabase_buffer)}条数据")     

if __name__ == "__main__":
    if not all([CLIENT_ID, CLIENT_SECRET, SHOPIFY_STORE]):
        print("❌ 请确保在 .env 文件中设置了 CLIENT_ID、CLIENT_SECRET 和 SHOPIFY_STORE")
    else:
        token = get_access_token()
        if token:
            get_products(token)
