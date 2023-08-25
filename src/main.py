from typing import List
from fastapi import Depends, FastAPI, HTTPException


from .auth import AuthHandler
from .database import database, users, notes
from .schemas import AuthDetails, Note, NoteIn, UserInput, User


app = FastAPI()


auth_handler = AuthHandler()


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


async def get_user(username: str):
    query = users.select().where(users.c.username == username)
    return await database.fetch_one(query)


@app.post('/register', response_model=User, status_code=201, tags=['Auth'])
async def register(user_input: UserInput):
    user = await get_user(user_input.username)

    if user:
        raise HTTPException(
            status_code=400, detail='Username is already taken')

    password = auth_handler.get_password_hash(user_input.password)
    query = users.insert().values(name=user_input.name,
                                  username=user_input.username, password=password)
    record_id = await database.execute(query)

    return {**user_input.dict(), "id": record_id}


@app.post('/login', tags=['Auth'])
async def login(auth_details: AuthDetails):
    user = await get_user(auth_details.username)
 
    if (user is None) or (not auth_handler.verify_password(auth_details.password, user['password'])):
        raise HTTPException(
            status_code=401, detail='Invalid username and/or password')
    token = auth_handler.encode_token(user['username'])
    return {'token': token}


@app.get('/unprotected', tags=['API'], name="Unprotected Path")
def unprotected():
    return {'hello': 'world'}


@app.get('/protected', tags=['API'])
def protected(username=Depends(auth_handler.auth_wrapper)):
    return {'name': username}


@app.get("/notes/", response_model=List[Note], tags=['API'])
async def read_notes():
    query = notes.select()
    return await database.fetch_all(query)


@app.post("/notes/", response_model=Note, tags=['API'])
async def create_note(note: NoteIn, username=Depends(auth_handler.auth_wrapper)):
    query = notes.insert().values(text=note.text, completed=note.completed, user=username)
    record_id = await database.execute(query)
    
    query = notes.select().where(notes.c.id == record_id)
    return await database.fetch_one(query)
