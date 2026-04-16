import os, requests, google.generativeai as genai

# Настройки
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
USER_ID = os.getenv('TELEGRAM_USER_ID')
TAK_TOKEN = os.getenv('TAKPRODAM_TOKEN')
GEMINI_KEY = os.getenv('GEMINI_API_KEY')

genai.configure(api_key=GEMINI_KEY)
ai_model = genai.GenerativeModel('gemini-1.5-flash')

def get_data():
    headers = {"Authorization": f"Bearer {TAK_TOKEN}"}
    # 1. Находим ID площадки
    src = requests.get("https://api.takprodam.ru/v2/publisher/source/", headers=headers).json().get('data', [])
    if not src: return []
    source_id = src[0]['id']
    
    # 2. Берем товары
    params = {"source_id": source_id, "limit": 20, "marketplace": "Wildberries"}
    return requests.get("https://api.takprodam.ru/v2/publisher/promotion/product/", headers=headers, params=params).json().get('data', [])

def main():
    products = get_data()
    for p in products:
        if p.get('discount_percent', 0) >= 40:
            prompt = f"Оформи пост: {p['title']}, цена {p['price_discount']}р, скидка {p['discount_percent']}%. Стиль: Эмодзи, Название на WB, Цена, 👉 по ССЫЛКЕ."
            text = ai_model.generate_content(prompt).text.strip()
            final_text = text.replace("👉 по ССЫЛКЕ", f"👉 [по ССЫЛКЕ]({p['tracking_link']})")
            
            requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", 
                          json={"chat_id": USER_ID, "text": final_text, "parse_mode": "Markdown"})

if __name__ == "__main__":
    main()
