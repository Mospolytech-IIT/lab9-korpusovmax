from typing import List, Annotated

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from database import create_all_tables, get_db, User, Post
import schemas

app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_all_tables()

# Dependency
def get_db_session():
    db = next(get_db())
    try:
        yield db
    finally:
        db.close()

@app.get("/")
async def root():
    return {"message": "Welcome to the FastAPI Blog API"}


@app.get("/users")
def main():
    return FileResponse("./users.html")

@app.get("/posts")
def main():
    return FileResponse("./posts.html")

# User CRUD Operations

@app.post("/api/users/", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Annotated[Session, Depends(get_db_session)]):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    db_user = User(username=user.username, email=user.email, password=user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/api/users/", response_model=List[schemas.User])
def read_users(db: Annotated[Session, Depends(get_db_session)], skip: int = 0, limit: int = 100):
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@app.get("/api/users/{user_id}", response_model=schemas.UserWithPosts)
def read_user(user_id: int, db: Annotated[Session, Depends(get_db_session)]):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.put("/api/users/", response_model=schemas.User)
def update_user(user_update: schemas.UserUpdate, db: Annotated[Session, Depends(get_db_session)]):
    db_user = db.query(User).filter(User.id == user_update.id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if user_update.username:
        db_user.username = user_update.username
    if user_update.email:
        # Check if new email already exists for another user
        existing_user_with_email = db.query(User).filter(User.email == user_update.email, User.id != user_update.id).first()
        if existing_user_with_email:
            raise HTTPException(status_code=400, detail="Email already registered by another user")
        db_user.email = user_update.email
    if user_update.password:
        db_user.password = user_update.password # In a real app, hash this password!

    db.commit()
    db.refresh(db_user)
    return db_user

@app.delete("/api/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Annotated[Session, Depends(get_db_session)]):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()
    return {"ok": True}

# Post CRUD Operations

@app.post("/api/users/{user_id}/posts/", response_model=schemas.Post, status_code=status.HTTP_201_CREATED)
def create_post_for_user(
    db: Annotated[Session, Depends(get_db_session)], user_id: int, post: schemas.PostCreate
):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    db_post = Post(**post.model_dump(), user_id=user_id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

@app.get("/api/posts/", response_model=List[schemas.Post])
def read_posts(db: Annotated[Session, Depends(get_db_session)], skip: int = 0, limit: int = 100):
    posts = db.query(Post).offset(skip).limit(limit).all()
    return posts

@app.get("/api/posts/{post_id}", response_model=schemas.Post)
def read_post(post_id: int, db: Annotated[Session, Depends(get_db_session)]):
    post = db.query(Post).filter(Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@app.put("/api/posts/{post_id}", response_model=schemas.Post)
def update_post(post_id: int, post_update: schemas.PostUpdate, db: Annotated[Session, Depends(get_db_session)]):
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if post_update.title:
        db_post.title = post_update.title
    if post_update.content:
        db_post.content = post_update.content
    
    db.commit()
    db.refresh(db_post)
    return db_post

@app.put("/api/posts/{post_id}", response_model=schemas.Post)
def update_post(post_id: int, post_update: schemas.PostUpdate, db: Annotated[Session, Depends(get_db_session)]):
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if post_update.title:
        db_post.title = post_update.title
    if post_update.content:
        db_post.content = post_update.content
    
    db.commit()
    db.refresh(db_post)
    return db_post

@app.delete("/api/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int, db: Annotated[Session, Depends(get_db_session)]):
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    db.delete(db_post)
    db.commit()
    return {"ok": True}

