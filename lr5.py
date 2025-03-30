import json, re, sys, os
from lr4 import get_request

def find_name_currencies(text, word):   # Поиск уникальных валют на бирже
    words = re.findall(r'\b\w+\b', text)
    unique_currencies = set()
    for i in range(len(words) - 1):
        if words[i] == word:
            next_word = re.sub(r'[^a-zA-Zа-яА-Я]', '', words[i + 1])
            unique_currencies.add(next_word)
    return unique_currencies

def find_symbols(text, word):
    words = re.findall(r'\b\w+(?:/\w+)?\b', text)
    pair_sym = []
    for i in range(len(words) - 1):
        if words[i] == word:
            next_word = words[i + 1]
            pair_sym.append(next_word)
    return pair_sym

def find_prices(text, word):
    pattern = rf'{word}[\s\W]*([-+]?\d*\.\d+|\d+)'
    matches = re.findall(pattern, text)
    return matches

def save_json(orders_list):
    filename = "orders_data.json"
    if os.path.exists(filename):
        with open(filename, "r") as file:
            try:
                orders = json.load(file)
            except json.JSONDecodeError:
                orders = []
    else:
        orders = []
    for order in orders_list:
        order_data = {
            "orderID": order["result"]["orderID"],
            "price": order["result"]["price"],
            "quantity": order["result"]["quantity"],
            "symbol": order["result"]["symbol"],
            "created": order["result"]["created"],
            "status": order["result"].get("status", "NEW")
        }
        orders.append(order_data)
    with open(filename, "w") as file:
        json.dump(orders, file, indent=4)

if __name__ == "__main__":
    print("=" * 50)
    print(" Доступный баланс на бирже в токенах USDT ")
    print("=" * 50)
    name_currencies = find_name_currencies(json.dumps(get_request("/api/symbols", "get")), "base")
    for currency in name_currencies:
        balance_info = get_request(f"/api/user/balances/{currency}", "get")
        balance = re.search(r"'available':\s*'([\d.]+)'", str(balance_info))
        if balance:
            print(f"{currency:<10} | {balance.group(1):>10} USDT")
    print("=" * 50)
    
    currencies_less_0_6 = []
    price_less_0_6_list = {}
    symbols = find_symbols(json.dumps(get_request("/api/symbols", "get")), "symbol")
    price = find_prices(json.dumps(get_request("/api/prices", "get")), "lastTrade")
    print("\n Торговые пары с USDT, где цена ≤ 0.6 USDT ")
    print("=" * 50)
    for i in range(len(symbols)):
        if "USDT" in symbols[i] and float(price[i]) <= 0.6:
            print(f"{symbols[i]:<15} | {price[i]:>10} USDT")
            currencies_less_0_6.append(symbols[i])
            price_less_0_6_list[symbols[i]] = price[i]
    print("=" * 50)
    
    while True:
        current_cur = input("Выберите торговую пару (TRX, IMX, 1INCH) или exit --> ").upper()
        if current_cur + "/USDT" in currencies_less_0_6:
            price_less_0_6 = price_less_0_6_list[current_cur + "/USDT"]
            break
        elif current_cur == "EXIT":
            sys.exit()
        else:
            print("[!] Такой торговой пары нет в списке. Попробуйте еще раз.")
    
    print(f"\nВы выбрали: {current_cur} по цене {price_less_0_6} USDT")
    price_2pc = round(float(price_less_0_6) * 0.98, 4)
    price_5pc = round(float(price_less_0_6) * 0.95, 4)
    price_8pc = round(float(price_less_0_6) * 0.92, 4)
    print("\nСледующим шагом будет создано три ордера на покупку токена.")
    print(f"Цена покупки: -2% ({price_2pc}$), -5% ({price_5pc}$), -8% ({price_8pc}$)")
    print("\n[?] Если Вы согласны, напишите 'yes', если нет — 'exit'")
    
    while True:
        x = input("--> ")
        if x == "yes":
            break
        elif x == "exit":
            sys.exit()
    
    orders_list = []
    for price_level in [price_2pc, price_5pc, price_8pc]:
        order = get_request("/api/orders", "post", current_cur + "/USDT", price_level)
        orders_list.append(order)
    
    save_json(orders_list)
    print("\n[+] Ордера успешно созданы.")
    print("[i] Для проверки результата посетите сайт ATAIX (вкладка 'Мои ордера').")
    print("[i] Данные сохранены в 'orders_data.json'.")
    print("=" * 50)