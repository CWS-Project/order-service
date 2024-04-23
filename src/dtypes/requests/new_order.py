from pydantic import BaseModel

class NewOrderRequest(BaseModel):
    user_id: str