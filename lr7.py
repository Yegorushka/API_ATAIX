import json
from lr4 import get_request
from lr5 import find_prices, find_symbols, save_json, confirm_action
from lr6 import print_order_status


def create_sell_orders_2pc(symbols, prices):
    orders = []
    for i in range(len(symbols)):
        new_price = round(prices[i] * 1.02, 4)
        orders.append(get_request("/api/orders", "post", symbol=symbols[i], side="sell", price=new_price))
    return orders


if __name__ == "__main__":
    with open("orders_data.json", "r") as f:
        data = json.load(f)

    order_ids = [item["orderID"] for item in data if "orderID" in item]
    status_ids = [item["status"] for item in data if "status" in item]
    symbol_ids = [item["symbol"] for item in data if "symbol" in item]
    price_ids = [float(item["price"]) for item in data if "price" in item]
    side_ids = [item["side"] for item in data if "side" in item]

    print_order_status(order_ID=order_ids, side=side_ids, status=status_ids)

    print("-" * 50)
    print("Если ордер выполнен (filled), выполнится ордер на продажу на 2% дороже от купленной цены.")
    print("-" * 50)

    symbols_get = find_symbols(json.dumps(get_request("/api/symbols", "get")), "symbol")
    price_get = find_prices(json.dumps(get_request("/api/prices", "get")), "lastTrade")

    symbols_current, price_current = [], []
    print("Торговая пара   | Текущая цена  | Цена покупки по ордеру")
    for i in range(len(symbol_ids)):
        for j in range(len(symbols_get)):
            if symbol_ids[i] in symbols_get[j]:
                current_price = round(float(price_get[j]), 4)
                print(f"{symbols_get[j]:<15} | {current_price:>13} | {price_ids[i]:>10} USDT")
                symbols_current.append(symbol_ids[i])
                price_current.append(current_price)

    print("-" * 50)

    if price_current[0] * 1.1 < price_ids[0]:
        print(f"Цена покупки токена {symbols_current[0]} ({price_ids[0]}$) превышает текущую на более чем 10% ({price_current[0]}$).")
        suggested_price = round(price_current[0] * 1.02, 4)
        print(f"Возможна только продажа по текущей цене с наценкой 2%: {suggested_price}$")
        if confirm_action():
            orders_list = create_sell_orders_2pc(symbols_current, price_current)
            save_json(orders_list)
    else:
        print(f"Создание ордеров на продажу: ")
        for i in range(len(symbols_current)):
            print(f" - {symbols_current[i]} по цене {round(price_ids[i] * 1.02, 4)}$")
        if confirm_action():
            orders_list = create_sell_orders_2pc(symbol_ids, price_ids)
            save_json(orders_list)

    print("[+] Ордера успешно созданы.")
    print("[i] Для проверки результата посетите сайт ATAIX (вкладка 'Мои ордера').")
    print("[i] Данные сохранены в 'orders_data.json'.")
    print("=" * 50)
