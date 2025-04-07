from fastapi import FastAPI
# from app.routers import auth, vote
from .routers import product, order, user, auth, warehouse
from app.db import init_db

from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(lifespan=lifespan)


app.include_router(product.router)
app.include_router(user.router)
app.include_router(order.router)
app.include_router(auth.router)
app.include_router(warehouse.router)