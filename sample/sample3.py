from fastapi import FastAPI

app = FastAPI()

@app.get("/add")
async def add_numbers(a: int, b: int):
    sum = a + b
    return {"a":a, "b":b, "sum":sum}

@app.get("/sub")
async def sub_numbers(a: int, b: int):
    sub = a - b
    return {"a":a, "b":b, "sub":sub}

@app.get("/mul")
async def mul_numbers(a: int, b: int):
    mul = a * b
    return {"a":a, "b":b, "mul":mul}

@app.get("/div")
async def div_numbers(a: int, b: int):
    if b == 0:
        return {"a":a, "b":b, "div":"0で割ることはできません"}
    div = a / b
    return {"a":a, "b":b, "div":div}

@app.get("/hello")
async def read_root(name: str = "World"):
    return {"message": f"Hello {name}!"}