import os, requests

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
USER_ID = os.getenv('TELEGRAM_USER_ID')
TAK_TOKEN = os.getenv('TAKPRODAM_TOKEN')

def send(text):
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", 
                  json={"chat_id": USER_ID, "text": text})

def main():
    send("🕵️‍♂️ Начинаю поиск твоего ID площадки...")
    headers = {"Authorization": f"Bearer {TAK_TOKEN}"}
    
    # Способ 1: Ищем в списке площадок
    try:
        r = requests.get("https://api.takprodam.ru/v2/publisher/source/", headers=headers).json()
        sources = r.get('data', [])
        if sources:
            send(f"✅ Нашел через площадки! Твой ID: {sources[0]['id']}")
            return
    except: pass

    # Способ 2: Ищем в истории твоих кликов/комиссий
    try:
        r = requests.get("https://api.takprodam.ru/v2/publisher/commission/", headers=headers).json()
        commissions = r.get('data', [])
        if commissions:
            # Вытаскиваем ID из первой попавшейся комиссии
            sid = commissions[0].get('source', {}).get('id')
            if sid:
                send(f"✅ Нашел через историю комиссий! Твой ID: {sid}")
                return
    except: pass

    send("❌ К сожалению, твой личный токен 'пустой'. Это часто бывает у админов.")
    send("💡 Чтобы всё заработало, просто попроси ВЛАДЕЛЬЦА аккаунта (кто тебя пригласил) прислать его API-токен. Вставь его в GitHub вместо своего, и бот сразу начнет летать!")

if __name__ == "__main__":
    main()
