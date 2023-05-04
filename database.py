from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

SQL_ALCHEMY_DATABASE_URL = "postgresql://studentregistry_user:UoY9i5GtLIcoHwLkJggemowS8FfKfQYd@dpg-ch9jqsl269v0obam6b90-a.oregon-postgres.render.com/studentregistry"
engine = create_engine(SQL_ALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

