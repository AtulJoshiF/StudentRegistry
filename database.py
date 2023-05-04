from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

SQL_ALCHEMY_DATABASE_URL = postgresql://studentregistry_epgp_user:MgyigwcIbJAjoHlSErwBxJZKe6LElNzJ@dpg-ch9nihik728hts35ts1g-a/studentregistry_epgp
engine = create_engine(SQL_ALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

