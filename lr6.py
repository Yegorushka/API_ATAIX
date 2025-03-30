import json
from lr4 import get_request
from lr5 import save_json

with open("orders_data.json", "r") as f:
    data = json.load(f)  # Загружаем JSON

order_ids = [item["orderID"] for item in data if "orderID" in item]
price_ids = [item["price"] for item in data if "price" in item]
symbol_ids = [item["symbol"] for item in data if "symbol" in item]
status_ids = [item["status"] for item in data if "status" in item]

not_filled_orders = []
nfo_price = []

print("=" * 50)
print("СТАТУС ВСЕХ ОРДЕРОВ")
print("=" * 50)
for i in range(len(order_ids)):
    print(f"OrderID: {order_ids[i]} \t Status: {status_ids[i]}")

print("-" * 50)
print("Если ордер выполнен, его статус изменится на 'filled', иначе статус изменится на 'cancelled' в файле orders_data.json")
print("-" * 50)

for i in range(len(order_ids)):
    response = get_request(f"/api/orders/{order_ids[i]}", "get")
    if "filled" in str(response):
        for order in data:
            if order["orderID"] == order_ids[i]:
                order["status"] = "filled"
    else:
        print(f"OrderID: {order_ids[i]} \t Price: {price_ids[i]}$ \t Status: {status_ids[i]}")
        not_filled_orders.append(order_ids[i])
        nfo_price.append(price_ids[i])
        for order in data:
            if order["orderID"] == order_ids[i]:
                order["status"] = "cancelled"
    
    with open("orders_data.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

print("=" * 50)
print("ОТМЕНА НЕВЫПОЛНЕННЫХ ОРДЕРОВ")
print("=" * 50)
for order_id in not_filled_orders:
    get_request(f"/api/orders/{order_id}", "delete")
    print(f"[-] Отменен ордер: {order_id}")

print("=" * 50)
print("СОЗДАНИЕ НОВЫХ ОРДЕРОВ (цена +1%)")
print("=" * 50)
orders_list = []
for j in range(len(not_filled_orders)):
    new_price = round(float(nfo_price[j]) * 1.01, 4)
    orders_list.append(get_request("/api/orders", "post", symbol_ids[j], new_price))
    print(f"[+] Создан новый ордер: {symbol_ids[j]} по цене {new_price}$")

save_json(orders_list)
print("=" * 50)
print("[+] Ордера успешно созданы.")
print("[+] Для проверки результата посетите сайт ATAIX, вкладка 'Мои ордера'.")
print("[+] Данные успешно сохранены в orders_data.json")
print("=" * 50)
