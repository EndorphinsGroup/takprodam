import os, requests, google.generativeai as genai

# Загрузка настроек
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
USER_ID = os.getenv('TELEGRAM_USER_ID')
TAK_TOKEN = os.getenv('TAKPRODAM_TOKEN')
GEMINI_KEY = os.getenv('GEMINI_API_KEY')

def send_msg(text):
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", 
                  json={"chat_id": USER_ID, "text": text, "parse_mode": "HTML"})

def main():
    headers = {"Authorization": f"Bearer {TAK_TOKEN}"}
    send_msg("⚙️ Запускаю проверку прав доступа...")

    # Пытаемся узнать, кто мы для сервера
    r = requests.get("https://api.takprodam.ru/v2/publisher/source/", headers=headers)
    
    if r.status_code == 401:
        send_msg("❌ <b>Ошибка 401:</b> Твой токен не принят сервером. Проверь, нет ли в GitHub Secrets лишних пробелов.")
        return
    if r.status_code == 403:
        send_msg("❌ <b>Ошибка 403:</b> Доступ запрещен. Твоему аккаунту админа ЗАПРЕЩЕНО пользоваться API. Нужно брать токен владельца.")
        return
    
    try:
        sources = r.json().get('data', [])
        if not sources:
            send_msg("⚠️ Токен верный, но список площадок пуст. API не видит товаров для админа.")
        else:
            sid = sources[0]['id']
            send_msg(f"✅ Успех! Найден ID: {sid}. Пытаюсь получить товары...")
            # Тут пойдет логика получения товаров...
    except:
        send_msg(f"💥 Сервер выдал странный ответ (не JSON). Код ответа: {r.status_code}")

if __name__ == "__main__":
    main()
