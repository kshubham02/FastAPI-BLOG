from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://postgres:shubham@localhost:5432/blog-fastapi'
SQLALCHEMY_DATABASE_URI = 'sqlite:///./blog.db'



engine = create_engine(SQLALCHEMY_DATABASE_URI, connect_args={'check_same_thread':False} ,echo=True)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()

