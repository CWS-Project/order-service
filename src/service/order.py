from util import DatabaseSession, RedisSession, create_payment_id
from bson.objectid import ObjectId
from typing import Tuple
import requests, os, json

class OrderService:
    __db_client: DatabaseSession
    __redis_client: RedisSession

    def __init__(self, dbc: DatabaseSession, rdc: RedisSession):
        self.__db_client = dbc
        self.__redis_client = rdc
        self.product_svc_url = os.getenv("PRODUCT_SERVICE_URL", "http://localhost:8002")
        self.auth_svc_url = os.getenv("AUTH_SERVICE_URL", "http://localhost:8001")
    
    def get_product_details(self, product_id: str) -> Tuple[bool, dict | None]:
        response = requests.get(f"{self.product_svc_url}/api/v1/products/{product_id}").json()
        if response["status"] != 200:
            return False, None
        return True, response["data"]
    
    def create_order_from_cart(self, user_id: str) -> Tuple[bool, dict | None]:
        response = requests.get(f"{self.auth_svc_url}/api/v1/customer/cart/{user_id}").json()
        if response["status"] != 200:
            return False, None
        cart = response["data"]
        if len(cart) == 0:
            return False, None
        for item in cart:
            success, product = self.get_product_details(item["product_id"])
            if not success:
                return False, None
            item["price"] = product["price"]
            item["name"] = product["name"]
        

        sub_total = round(sum([item["price"] for item in cart]), 2)
        tax = round(sub_total * 0.18, 2)
        grand_total = round(sub_total + tax, 2)
        payment_intent_id = create_payment_id(grand_total, "INR", f"Payment for order by {user_id}", user_id)

        success, data = self.__db_client.insert("orders", {
            "user_id": user_id,
            "items": cart,
            "sub_total": sub_total,
            "tax": tax,
            "grand_total": grand_total,
            "currency": "inr",
            "status": "pending",
            "payment_id": payment_intent_id
        })

        if not success:
            return False, None
        
        return True, {"order_id": data, "grand_total": grand_total}
    
    def get_order_by_id(self, order_id: str) -> Tuple[bool, dict | None]:
        order = self.__redis_client.get(f"order:{order_id}")
        if order:
            return True, json.loads(order)
        success, data = self.__db_client.findOne("orders", {"_id": ObjectId(order_id)})
        if not success:
            return False, None
        data["_id"] = str(data["_id"])
        self.__redis_client.set(f"order:{order_id}", json.dumps(data))
        return True, data
    
    def get_order_by_user(self, user_id: str) -> Tuple[bool, list]:
        orders = self.__redis_client.get(f"orders:{user_id}")
        if orders:
            return True, json.loads(orders)
        success, data = self.__db_client.find("orders", {"user_id": user_id})
        if not success:
            return False, []
        for item in data:
            item["_id"] = str(item["_id"])
        self.__redis_client.set(f"orders:{user_id}", json.dumps(data), 3600)
        return True, data
    
    def mark_order_as_paid(self, order_id: str) -> Tuple[bool, dict | None]:
        success, _ = self.__db_client.update("orders", {"_id": ObjectId(order_id)}, {"status": "paid"})
        if not success:
            return False, None
        self.__redis_client.delete(f"order:{order_id}")
        return True, None
