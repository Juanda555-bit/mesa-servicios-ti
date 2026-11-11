from fastapi import FastAPI

app = FastAPI(title="Mesa de Servicios TI")


@app.get("/salud")
def salud():
    return {"estado": "ok"}