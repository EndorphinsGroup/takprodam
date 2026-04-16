import os, requests, google.generativeai as genai

# Твои секреты из GitHub
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
USER_ID = os.getenv('TELEGRAM_USER_ID')
TAK_TOKEN = os.getenv('TAKPRODAM_TOKEN')
GEMINI_KEY = os.getenv('GEMINI_API_KEY')

# Настройка нейросети
genai.configure(api_key=GEMINI_KEY)
ai_model = genai.GenerativeModel('gemini-1.5-flash')

def main():
    headers = {"Authorization": f"Bearer {TAK_TOKEN}"}
    
    # 1. Сначала мы просто 'нагло' просим список всех товаров, 
    # пытаясь зацепиться за любую доступную площадку
    try:
        # Пробуем получить список площадок еще раз
        src_res = requests.get("https://api.takprodam.ru/v2/publisher/source/", headers=headers).json()
        sources = src_res.get('data', [])
        
        if not sources:
            # ЕСЛИ ПУСТО (как у нас и было):
            # Мы отправим тебе сообщение, что нужно сделать одно маленькое действие в самом Такпродам
            requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", 
                          json={"chat_id": USER_ID, "text": "❌ Лейла, твой API-токен не видит площадок. \n\nЧтобы это исправить: зайди в Такпродам -> 'Источники' -> 'Добавить источник' и добавь свой канал. Как только его одобрят, бот сразу увидит его!"})
            return

        # Если площадка нашлась, берем товары
        source_id = sources[0]['id']
        params = {"source_id": source_id, "limit": 20}
        products = requests.get("https://api.takprodam.ru/v2/publisher/promotion/product/", headers=headers, params=params).json().get('data', [])

        for p in products:
            if p.get('discount_percent', 0) >= 40:
                prompt = f"Оформи пост: {p['title']}, цена {p['price_discount']}р, скидка {p['discount_percent']}%. Стиль: Эмодзи, Название на маркетплейсе, Цена, 👉 по ССЫЛКЕ."
                text = ai_model.generate_content(prompt).text.strip()
                # Формируем красивую ссылку
                link = f'<a href="{p["tracking_link"]}">по ССЫЛКЕ</a>'
                final_text = text.replace("👉 по ССЫЛКЕ", f"👉 {link}")
                
                requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", 
                              json={"chat_id": USER_ID, "text": final_text, "parse_mode": "HTML"})
    except Exception as e:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", 
                      json={"chat_id": USER_ID, "text": f" Ошибка в коде: {e}"})

if __name__ == "__main__":
    main()
