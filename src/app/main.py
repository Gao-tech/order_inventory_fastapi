from fastapi import FastAPI
from fastapi.responses import HTMLResponse
# from app.routers import auth, vote
from .routers import product, order, user, auth, warehouse
from app.db import init_db
from contextlib import asynccontextmanager
from mangum import Mangum


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(lifespan=lifespan)
handler = Mangum(app)

# @app.get("/", response_class=HTMLResponse)
# async def hello():
#     return "<h1 style='color: teal;'>Hello to the order and inventory platform!</h1>"


app.include_router(product.router)
app.include_router(user.router)
app.include_router(order.router)
app.include_router(auth.router)
app.include_router(warehouse.router)