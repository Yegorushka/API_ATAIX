import json, re, requests

API_KEY = ""

def get_request(endpoint):
    url = f"https://api.ataix.kz{endpoint}"
    headers = {
        "API-KEY": API_KEY,
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers, timeout=20)
    if response.status_code == 200:
        return response.json()
    else:
        return f"Ошибка: {response.status_code}, {response.text}"

def find_currencies(text, word):
    words = re.findall(r'\b\w+\b', text)
    count = 0
    for i in range(len(words) - 1):
        if words[i] == word:
            next_word = re.sub(r'[^a-zA-Zа-яА-Я]', '', words[i + 1])
            print(f"{next_word}")
            count += 1
    print(f"Количество валют: {count}")

def find_symbols(text, word):
    words = re.findall(r'\b\w+(?:/\w+)?\b', text)
    count = 0
    pair_sym = []
    for i in range(len(words) - 1):
        if words[i] == word:
            next_word = words[i + 1]
            print(f"{next_word}")
            count += 1
            pair_sym.append(next_word)
    print(f"Количество торговых пар: {count}")
    return pair_sym

def find_prices(text, word):
    pattern = rf'{word}[\s\W]*([-+]?\d*\.\d+|\d+)'
    matches = re.findall(pattern, text)
    price = []
    for match in matches:
        price.append(match)
    return price

print("Список всех валют:")
data_currency = get_request("/api/currencies")
find_currencies(json.dumps(data_currency), "currency")

print("\nСписок всех торговых пар:")
data_symbol = get_request("/api/symbols")
symbols = find_symbols(json.dumps(data_symbol), "symbol")

print("\nСписок цены всех монет и токенов:")
data_prices = get_request("/api/prices")
price = find_prices(json.dumps(data_prices), "lastTrade")

for i in range(len(symbols)):
    print(f"{symbols[i]}: {price[i]}")