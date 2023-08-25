from pydantic import BaseModel

class AuthDetails(BaseModel):
    username: str
    password: str
    
    
class UserInput(BaseModel):
    name: str
    username: str
    password: str
    
        
class User(BaseModel):
    id: str
    name: str
    username: str
    password: str
    
    
class NoteIn(BaseModel):
    text: str
    completed: bool


class Note(BaseModel):
    id: int
    text: str
    user: str
    completed: bool
