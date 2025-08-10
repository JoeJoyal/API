from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# classical method
# @app.post("/euron/api/multipy/")
# def multiply(a:int,b:int):
#     return a*b

# print(multiply(5,5))

# postman exec: http://127.0.0.1:8000/euron/api/multipy

#pydantic method
# class multipy_model(BaseModel):
#     a: int
#     b: int

# @app.post("/multiply_pydantic")
# def multiply_pydantic(model: multipy_model):
#     return multiply(model.a, model.b)

# postman exec: http://127.0.0.1:8000/multiply_pydantic


# Simple Calculator using API

@app.post("/euron/api/addition/")
def addition(a:int,b:int):
    return a+b

@app.post("/euron/api/subtraction/")
def subtraction(a:int,b:int):
    return a-b

@app.post("/euron/api/multiplication/")
def multiplication(a:int,b:int):
    return a*b

@app.post("/euron/api/division/")
def division(a:int,b:int):
    return a//b

#pydantic method
class multipy_model(BaseModel):
    a: int
    b: int

@app.post("/addition_pydantic")
def addition_pydantic(model: multipy_model):
    return addition(model.a, model.b)

@app.post("/subtraction_pydantic")
def subtraction_pydantic(model: multipy_model):
    return subtraction(model.a, model.b)

@app.post("/multiplication_pydantic")
def multiplication_pydantic(model: multipy_model):
    return multiplication(model.a, model.b)

@app.post("/division_pydantic")
def division_pydantic(model: multipy_model):
   return division(model.a, model.b)


@app.post("/division_ifelse_pydantic")
def division_pydantic(model: multipy_model):
    try:
        if isinstance(model.a, int) and isinstance(model.b, int):
            print("This is statement valid one!")
            return {'result': f"This statement is valid : {str(division(model.a, model.b))}"}
        else:
            return {'error':'Invalid Input given'}
    except Exception as e:
        return {"error": f"Invalid statement: {str(e)}"}
    
# postman exec: api_mode : POST url: http://127.0.0.1:8000/division_ifelse_pydantic

   
 