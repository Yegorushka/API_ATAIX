import json
import re
import requests

API_KEY = "___API___"


def get_request(endpoint, get_post_delete, symbol="", side="", price=""):
    url = f"https://api.ataix.kz{endpoint}"
    headers = {
        "accept": "application/json",
        "X-API-Key": API_KEY
    }
    data = {
        "symbol": symbol,
        "side": side,
        "type": "limit",
        "quantity": 1,
        "price": price
    }

    if get_post_delete == "get":
        response = requests.get(url, headers=headers, timeout=20)
    elif get_post_delete == "post":
        response = requests.post(url, headers=headers, json=data, timeout=20)
    elif get_post_delete == "delete":
        response = requests.delete(url, headers=headers, timeout=20)

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


if __name__ == "__main__":
    print("Список всех валют:")
    data_currency = get_request("/api/currencies", "get")
    find_currencies(json.dumps(data_currency), "currency")

    print("\nСписок всех торговых пар:")
    data_symbol = get_request("/api/symbols", "get")
    symbols = find_symbols(json.dumps(data_symbol), "symbol")

    print("\nСписок цены всех монет и токенов:")
    data_prices = get_request("/api/prices", "get")
    price = find_prices(json.dumps(data_prices), "lastTrade")

    for i in range(len(symbols)):
        print(f"{symbols[i]}: {price[i]}")
