import os, requests, google.generativeai as genai

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
USER_ID = os.getenv('TELEGRAM_USER_ID')
TAK_TOKEN = os.getenv('TAKPRODAM_TOKEN')
GEMINI_KEY = os.getenv('GEMINI_API_KEY')

genai.configure(api_key=GEMINI_KEY)
ai_model = genai.GenerativeModel('gemini-1.5-flash')

def main():
    headers = {"Authorization": f"Bearer {TAK_TOKEN}"}
    
    # Пытаемся получить список товаров БЕЗ указания ID площадки
    # Это 'общий' список, который иногда доступен админам
    url = "https://api.takprodam.ru/v2/publisher/product/"
    
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        products = data.get('data', [])
        
        if not products:
            # Если всё еще пусто, шлем тебе честный ответ от сервера
            requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", 
                          json={"chat_id": USER_ID, "text": f"🛑 Сервер ответил, но товаров не дал. Ответ: {data}"})
            return

        for p in products[:10]: # Берем первые 10 для теста
            market = p.get('marketplace_title', 'Маркетплейс')
            prompt = f"Оформи пост: {p['title']}, цена {p['price']}р. Название на {market}, Цена, 👉 по ССЫЛКЕ."
            text = ai_model.generate_content(prompt).text.strip()
            
            # Используем tracking_link, который уже есть в товаре
            link = f'<a href="{p["tracking_link"]}">по ССЫЛКЕ</a>'
            final_text = text.replace("👉 по ССЫЛКЕ", f"👉 {link}")
            
            requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", 
                          json={"chat_id": USER_ID, "text": final_text, "parse_mode": "HTML"})
            
    except Exception as e:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", 
                      json={"chat_id": USER_ID, "text": f"💥 Ошибка: {e}"})

if __name__ == "__main__":
    main()
