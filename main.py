from fastapi import FastAPI, Query, Depends

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from db import crud, models, schemas
from db.database import SessionLocal, engine
from typing import Annotated, Union
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta

models.Base.metadata.create_all(bind=engine)
app = FastAPI()

SECRET_KEY = "19109197bd5e7c289b92b2b355083ea26c71dee2085ceccc19308a7291b2ea06"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Визначення аутентифікації через OAuth2BearerToken
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Залежність
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
app = FastAPI()

@app.get("/")
def read_root(db: Session = Depends(get_db)):
    return {"message": "Привіт, FastAPI!"}

all_books = {
    "Джордж Оруелл": [
        {"title": "1984", "pages": 328},
        {"title": "Колгосп тварин", "pages": 112}
    ],
    "Стівен Кінг": [
        {"title": "Воно", "pages": 1138},
        {"title": "Сяйво", "pages": 447}
    ],
    "Артур Конан Дойл": [
        {"title": "Пригоди Шерлока Холмса", "pages": 307},
        {"title": "Собака Баскервілів", "pages": 256}
    ],
    "Джоан Роулінг": [
        {"title": "Гаррі Поттер і філософський камінь", "pages": 223},
        {"title": "Гаррі Поттер і таємна кімната", "pages": 251}
    ]
}

def token_create(data: dict):
    expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt

@app.post("/token")
async def token_get(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db:Session = Depends(get_db)): 
    user_db = db.query(models.User).filter(models.User.login == form_data.username, models.User.password == form_data.password).first()
    if not user_db:
        raise HTTPException(status_code=400, detail="Неправильний логін або пароль")
    
    token = token_create(data={"sub": user_db.login})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/books/{author}", response_model=list[schemas.BookDB])
def get_books(author: str, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
        ''''Отримання книг за автором'''
        books = db.query(models.Book).filter(models.Author.name == author).all()
        if books:
            return books
        elif not books:
            raise HTTPException(status_code=404, detail="Книги не знайдено для цього автора")
    

    
@app.post("/books")
def add_book(book: schemas.BookDB):
    if book.author not in all_books:
        all_books[book.author] = []
        all_books[book.author].append({'title': book.title, 'pages': book.pages})
        return {"message": "Книгу додано успішно"}


@app.delete("/books")
def delete_book(title: str = Query(min_length=3, max_length=100), author: str = Query(min_length=3, max_length=100)):
    if author in all_books:
        for book in all_books[author]:
            if book['title'] == title:
                all_books[author].remove(book)
                return {"message": "Книгу видалено успішно"}
    return {"message": "Книги не знайдено"}


@app.put("/books")
def update_book(title: str = Query(min_length=3, max_length=100), author: str = Query(min_length=3, max_length=100), new_title: str = Query(min_length=3, max_length=100), new_pages: int = Query(gt=10)):
    if author in all_books:
        for book in all_books[author]:
            if book['title'] == title:
                book['title'] = new_title
                book['pages'] = new_pages
                return {"message": "Книгу оновлено успішно"}
    return {"message": "Книги не знайдено"}
    

