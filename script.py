import os, requests, google.generativeai as genai

# Загрузка настроек
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
USER_ID = os.getenv('TELEGRAM_USER_ID')
TAK_TOKEN = os.getenv('TAKPRODAM_TOKEN')
GEMINI_KEY = os.getenv('GEMINI_API_KEY')

def send_test_message(text):
    """Служебная функция для проверки связи"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": USER_ID, "text": text})

def get_data():
    headers = {"Authorization": f"Bearer {TAK_TOKEN}"}
    
    # 1. Проверяем площадки
    src_res = requests.get("https://api.takprodam.ru/v2/publisher/source/", headers=headers).json()
    src_list = src_res.get('data', [])
    if not src_list:
        return "ERROR_NO_SOURCE", []
    
    source_id = src_list[0]['id']
    
    # 2. Берем товары БЕЗ ФИЛЬТРОВ (скидка от 0%)
    params = {"source_id": source_id, "limit": 10}
    prod_res = requests.get("https://api.takprodam.ru/v2/publisher/promotion/product/", headers=headers, params=params).json()
    return source_id, prod_res.get('data', [])

def main():
    # ШАГ 1: Проверяем, может ли бот вообще тебе писать
    send_test_message("🚀 Проверка связи! Я начал работу и ищу товары в Такпродам...")

    source_id, products = get_data()
    
    if source_id == "ERROR_NO_SOURCE":
        send_test_message("❌ Ошибка: В твоем аккаунте Такпродам не найдено ни одной площадки (Source).")
        return

    if not products:
        send_test_message(f"🔎 Площадка найдена (ID: {source_id}), но список товаров ПУСТ. Возможно, нужно добавить товары в 'Избранное' или подождать обновления базы.")
        return

    # ШАГ 2: Если товары есть, шлем первые 3 штуки для теста
    send_test_message(f"✅ Нашел {len(products)} товаров! Сейчас оформлю и пришлю первые несколько...")
    
    for p in products[:3]: # Берем только 3 для теста
        text = f"📦 {p['title']}\n💰 Цена: {p['price_discount']} ₽\n🔗 {p['tracking_link']}"
        send_test_message(text)

if __name__ == "__main__":
    main()
