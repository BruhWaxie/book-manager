from fastapi import FastAPI, Query, Depends

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from db import crud, models, schemas
from db.database import SessionLocal, engine
models.Base.metadata.create_all(bind=engine)
app = FastAPI()
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


@app.get("/books{author}", response_model=schemas.BookDB)
def get_books(author: str, db: Session = Depends(get_db)):
        books = db.query(models.Book).filter(models.Author.name == author).all()
        return books
    

    
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
    

