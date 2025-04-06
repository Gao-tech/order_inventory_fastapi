from fastapi import FastAPI
from .db import get_session
from .oauth2 import get_current_user

app = FastAPI()


PRODUCTS_MAL = [
    {'id': "40309870", 'category': 'BED & MA', 'name': 'beds', 'price': 300, 'location': 'Hövdingevägen', 'stock': 5, 'serie': 'SÄBÖVIK'},
    {'id': "19399033", 'category': 'Sofas & armchairs', 'name': 'sofas', 'price': 400, 'location': 'Hövdingevägen', 'stock': 10,'serie': 'VIMLE'},
    {'id': "09561633", 'category': 'Tables & chairs', 'name': 'Dining furniture', 'price': 1000, 'location': 'Hövdingevägen', 'stock': 5, 'serie':'SKANSNÄS '},
]

PRODUCTS_HEL = [
    {'id': "40309870", 'category': 'BED & MA', 'name': 'beds', 'price': 300, 'location': 'Marknadsvägen', 'stock': 30, 'serie': 'SÄBÖVIK'},
    {'id': "19399033", 'category': 'Sofas & armchairs', 'name': 'sofas', 'price': 400, 'location': 'Marknadsvägen', 'stock': 10,'serie': 'VIMLE'},
    {'id': "09561633", 'category': 'Tables & chairs', 'name': 'Dining furniture', 'price': 1000, 'location': 'Marknadsvägen', 'stock': 10, 'serie':'SKANSNÄS '},
]





@app.post('/user')
async def user_register():
    pass

@app.post('/user')
async def user_login():
    pass

@app.get('/users/{id}')
async def logined_user():
    pass

