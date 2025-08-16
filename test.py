import requests
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

@app.get("/euron/api/add/")
def add(a:int,b:int):
    return a+b
# print(add(2,4))

# GET using python requests
from fastapi.testclient import TestClient

client = TestClient(app)

def test_add():
    response = client.get("/euron/api/add/", params={"a": 5, "b": 7})
    assert response.status_code == 200
    assert response.json() == 12  # 5 + 7 = 12

# Directly run this file to see output (optional)
if __name__ == "__main__":
    test_add()
    print("Test passed!")


@app.post("/euron/api/subtract")
def subtract(a:int,b:int):
    return a-b

# class subtractmodel(BaseModel):
#     a: int
#     b: int

# @app.post("/subtract_pydantic")
# def subtract_numbers(model: subtractmodel):
#     return subtract(model.a, model.b)

# user_db = {
#     1:{"name":"Joe", "age":29},
#     2:{"name":"Joyal", "age":34},
#     3:{"name":"Rajesh", "age":33}
# }

# class User(BaseModel):
#     name: str
#     age: int

# @app.put("/euron/api/update/{user_id}")
# def user_update(user_id:int, user:User):
#     if user_id in user_db:
#         user_db[user_id] = user.dict()
#         print(user_db)
#         return {'message': 'User update successfully', 'user_db': user_db[user_id]}
#     else:
#         print(user_db)
#         return {'message': 'User not found'}

# @app.delete("/euron/api/delete/{user_id}")
# def user_update(user_id:int, user:User):
#     if user_id in user_db:
#         del user_db[user_id]
#         print(user_db)
#         return {"message": "User delete successfully"}
#     else:
#         return {"message": "User not found"}

    

