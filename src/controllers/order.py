from fastapi import APIRouter, Response, Query
from dtypes import NewOrderRequest, make_response
from service import OrderService
from util import DatabaseSession, RedisSession
from typing import Annotated

router = APIRouter(prefix="/api/v1/orders", tags=["Orders"])
order_service = OrderService(
    dbc=DatabaseSession(), 
    rdc=RedisSession()
)

@router.post("/")
def create_order(request: NewOrderRequest, response: Response):
    user_id = request.user_id
    success, details = order_service.create_order_from_cart(user_id)
    if not success:
        return make_response(response, 400, "Failed to create order")
    return make_response(response, 200, data=details)

@router.get("/")
def search_order(response: Response, q: Annotated[str, Query()] = "", q_type: Annotated[str, Query()] = "id"):
    if q_type not in ["id", "user"]:
        return make_response(response, 400, "Invalid query type, valid types are \"id\" and \"user\"")
    
    if q_type == "id":
        success, details = order_service.get_order_by_id(q)
        if not success:
            return make_response(response, 404, "Order not found")
        return make_response(response, 200, data=details)
    elif q_type == "user":
        success, details = order_service.get_order_by_user(q)
        if not success:
            return make_response(response, 404, "Order not found")
        return make_response(response, 200, data=details)
    return make_response(response, 400, "Invalid query type")

@router.put("/{order_id}")
def update_order(order_id: str, response: Response):
    success, _ = order_service.mark_order_as_paid(order_id)
    if not success:
        return make_response(response, 400, "Failed to update order")
    return make_response(response, 200, "Order updated successfully", {"order_id": order_id, "status": "paid"})