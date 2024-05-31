from fastapi import FastAPI, Depends, status, Response, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from schemas import Blog, Users
import models
import schemas
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from typing import List
import jwt_aauthentication
import service


app = FastAPI()

models.Base.metadata.create_all(engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def redirect_to_docs():
    return RedirectResponse(url="/docs")

@app.post('/create_blog', status_code=201, tags=['blog'])
def create_blog(request : Blog, db : Session = Depends(get_db)):
    new_blog = models.BlogModel(title=request.title, body=request.body, user_id=1)
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    return new_blog


@app.get('/get_blogs', tags=['blog'])
def get_blogs( db : Session = Depends(get_db), current_user : schemas.Users = Depends(jwt_aauthentication.get_current_user)):
    blogs = db.query(models.BlogModel).all()
    return blogs


@app.get('/blog/{id}', status_code=200, response_model=schemas.ShowBlog, tags=['blog'])
def get_blog_by_id(id, response : Response, db : Session = Depends(get_db), current_user : schemas.Users = Depends(jwt_aauthentication.get_current_user)):
    blog = db.query(models.BlogModel).filter(models.BlogModel.id==id).first()
    if blog:
        return blog
    else:
        raise HTTPException(status_code=404, detail=f'blog with id {id} does not exists')
    

@app.delete('/delete/{id}', tags=['blog'])
def delete_blog(id, db : Session = Depends(get_db), current_user : schemas.Users = Depends(jwt_aauthentication.get_current_user)):
    blog = db.query(models.BlogModel).filter(models.BlogModel.id==id)
    if blog.first():
        blog.delete()
        db.commit()
        return f'blog with id {id} got deleted'
    else:
        raise HTTPException(status_code=404, detail=f'Not deleted or not exists')


@app.put('/update/{id}', tags=['blog'])
def update_blog(id, request : Blog, db : Session = Depends(get_db), current_user : schemas.Users = Depends(jwt_aauthentication.get_current_user)):
    blog = db.query(models.BlogModel).filter(models.BlogModel.id==id)
    request = request.dict()
    if blog.first():
        blog.update(request, synchronize_session=False)
        db.commit()
        return f'blog with id {id} updated successfully'
    else:
        raise HTTPException(status_code=404, detail=f'Not updated')
    

@app.post('/create_user', response_model=schemas.ShowUsers, tags=['user'])
def create_user(request : Users, db : Session = Depends(get_db)):
    hashed_password = service.hash_password(request.password)
    user = models.UserModel(name=request.name,email=request.email,password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.get('/users', response_model=List[schemas.ShowUsers], tags=['user'])
def get_users( db : Session = Depends(get_db), current_user : schemas.Users = Depends(jwt_aauthentication.get_current_user)):
    users = db.query(models.UserModel).all()
    return users


@app.get('/user/{id}', status_code=200, response_model=schemas.ShowUsers, tags=['user'])
def get_user_by_id(id, response : Response, db : Session = Depends(get_db), current_user : schemas.Users = Depends(jwt_aauthentication.get_current_user)):
    user = db.query(models.UserModel).filter(models.UserModel.id==id).first()
    if user:
        return user
    else:
        raise HTTPException(status_code=404, detail=f'user does not exists')
    

@app.post('/login', tags=['user'])
def login(request : OAuth2PasswordRequestForm = Depends(), db : Session = Depends(get_db)):
    user = db.query(models.UserModel).filter(models.UserModel.email==request.username).first()
    if not user:
        raise HTTPException(status_code=404, detail=f'Invalid credentials')
    
    elif not service.verify_password(request.password,user.password):
        raise HTTPException(status_code=404, detail=f'Invalid password')
    
    access_token = jwt_aauthentication.create_access_token(data={'sub':user.email})
    data = {
        'access_token' : access_token,
        'token_type' : 'bearer'
    }

    return data