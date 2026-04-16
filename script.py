import os, requests, re, google.generativeai as genai

# Твои ключи из GitHub
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
USER_ID = os.getenv('TELEGRAM_USER_ID')
TAK_TOKEN = os.getenv('TAKPRODAM_TOKEN')
GEMINI_KEY = os.getenv('GEMINI_API_KEY')

# Твоя ссылка, которую ты прислала (я вытащу из неё ID сама)
TEST_LINK = "https://takprdm.ru/0W81dm826GCZIr00/"

genai.configure(api_key=GEMINI_KEY)
ai_model = genai.GenerativeModel('gemini-1.5-flash')

def get_source_id_from_link(link):
    """Хитрый способ вытащить ID площадки из партнерской ссылки"""
    try:
        # Переходим по ссылке и смотрим, куда она ведет (там в конце будет ID)
        r = requests.get(link, allow_redirects=True, timeout=10)
        # Ищем в конечном URL цифры после 'source_id=' или в параметрах
        match = re.search(r'source_id=(\d+)', r.url)
        if match:
            return match.group(1)
        # Если в URL нет, попробуем поискать в твоем профиле через API еще раз, зная что ты админ
        headers = {"Authorization": f"Bearer {TAK_TOKEN}"}
        src_res = requests.get("https://api.takprodam.ru/v2/publisher/source/", headers=headers).json()
        if src_res.get('data'):
            return src_res['data'][0]['id']
    except:
        pass
    return None

def main():
    # Сообщаем Лейле, что начали
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", 
                  json={"chat_id": USER_ID, "text": "🤖 Бот включился! Начинаю полную автоматическую проверку всех скидок..."})

    # 1. Вычисляем ID
    source_id = get_source_id_from_link(TEST_LINK)
    
    if not source_id:
        # Если совсем всё плохо, пробуем 'запасной' метод получения товаров
        url = "https://api.takprodam.ru/v2/publisher/product/"
    else:
        url = "https://api.takprodam.ru/v2/publisher/promotion/product/"

    # 2. Берем товары (все подряд, без твоих тыков)
    headers = {"Authorization": f"Bearer {TAK_TOKEN}"}
    params = {"source_id": source_id, "limit": 30} if source_id else {"limit": 30}
    
    try:
        res = requests.get(url, headers=headers, params=params).json()
        products = res.get('data', [])
        
        if not products:
            requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", 
                          json={"chat_id": USER_ID, "text": "🔎 На сайте сейчас нет новых акций. Проверю позже!"})
            return

        sent = 0
        for p in products:
            # Берем только хорошие скидки (от 40%)
            if p.get('discount_percent', 0) >= 40:
                market = p.get('marketplace_title', 'магазине')
                prompt = f"Оформи пост: {p['title']}, цена {p['price_discount']}р, скидка {p['discount_percent']}%, магазин {market}. Стиль: Эмодзи, Название на маркетплейсе, Цена, 👉 по ССЫЛКЕ."
                
                ai_res = ai_model.generate_content(prompt).text.strip()
                link_html = f'<a href="{p["tracking_link"]}">по ССЫЛКЕ</a>'
                final_text = ai_res.replace("👉 по ССЫЛКЕ", f"👉 {link_html}")
                
                requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", 
                              json={"chat_id": USER_ID, "text": final_text, "parse_mode": "HTML"})
                sent += 1
        
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", 
                      json={"chat_id": USER_ID, "text": f"✅ Готово! Я нашел и оформил {sent} лучших товаров для тебя."})
                      
    except Exception as e:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", 
                      json={"chat_id": USER_ID, "text": f"💥 Ошибка при поиске: {e}"})

if __name__ == "__main__":
    main()
