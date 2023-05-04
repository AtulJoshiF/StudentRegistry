from sqlalchemy import Column, Integer, String, Date
from database import Base


class Students(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    register_number = Column(Integer, unique=True, index=True)
    date_of_birth = Column(Date)
    gender = Column(String)
    phone_number = Column(Integer)
    course = Column(String)
    address = Column(String)
    hashed_password = Column(String)

