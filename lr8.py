import json

from lr4 import get_request
from lr6 import print_order_status


def sum_orders_sell_buy(side_status: str, info_orders: list):
    cumQuoteQuantity = 0
    Commission = 0
    for side in info_orders:
        if side["result"]["side"] == side_status:
            # print(side["result"]["orderID"])
            cumQuoteQuantity += float(side["result"]["cumQuoteQuantity"])
            Commission += float(side["result"]["cumCommission"])

    return cumQuoteQuantity, Commission


if __name__ == "__main__":
    with open("orders_data.json", "r") as f:
        data = json.load(f)

    order_ids = [item["orderID"] for item in data if "orderID" in item]

    info_orders = []
    for i in range(len(order_ids)):
        response = get_request(f"/api/orders/{order_ids[i]}", "get")
        info_orders.append(response)

    orderID_list = []
    side_list = []
    price_list = []
    quantity_list = []
    cumQuantity_list = []
    cumQuoteQuantity_list = []
    cumCommission_list = []
    symbol_list = []
    status_list = []

    for order in info_orders:
        result = order["result"]
        orderID_list.append(result["orderID"])
        side_list.append(result["side"])
        price_list.append(result["price"])
        quantity_list.append(result["quantity"])
        cumQuantity_list.append(result["cumQuantity"])
        cumQuoteQuantity_list.append(result["cumQuoteQuantity"])
        cumCommission_list.append(result["cumCommission"])
        symbol_list.append(result["symbol"])
        status_list.append(result["status"])

    print_order_status(Order_ID=orderID_list, Side=side_list, Price=price_list,
                       Quantity=quantity_list, Cum_Quantity=cumQuantity_list,
                       Cum_Quote=cumQuoteQuantity_list,
                       Commission=cumCommission_list,
                       Symbol=symbol_list, Status=status_list)

    cumQuoteQuantity_sell, Commission_sell = sum_orders_sell_buy("sell", info_orders)
    cumQuoteQuantity_buy, Commission_buy = sum_orders_sell_buy("buy", info_orders)

    revenue = cumQuoteQuantity_sell - Commission_sell
    cost = cumQuoteQuantity_buy + Commission_buy
    total = round(revenue - cost, 4)

    if cost != 0:
        total_percent = round((total / cost) * 100, 2)
    else:
        total_percent = 0.0

    print(f"Общая сумма по продаже: {cumQuoteQuantity_sell}$ (включая комиссию: {Commission_sell}$)")
    print(f"Общая сумма по покупке: {cumQuoteQuantity_buy}$ (включая комиссию: {Commission_buy}$)")

    # Определим результат
    if total > 0:
        print(f"✅ Прибыль: {total}$ (+{total_percent}%)")
    elif total < 0:
        print(f"🔻 Убыток: {total}$ ({total_percent}%)")
    else:
        print(f"➖ Ни прибыли, ни убытка: {total}$ (0%)")
