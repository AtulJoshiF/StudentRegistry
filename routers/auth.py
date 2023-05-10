from enum import Enum
from datetime import timedelta, datetime, date
from typing_extensions import Annotated
from fastapi import APIRouter, Depends, HTTPException, Form, Response
from pydantic import BaseModel, EmailStr, Field, constr
from sqlalchemy import or_
from sqlalchemy.orm import Session
from starlette import status
from database import SessionLocal
from models import Students
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError


router = APIRouter(
    prefix='/auth',
    tags=['auth']
)


SECRET_KEY = 'abcdefghijklmnopqrstuvwxyz1234567890!@#$%^&*()_+-='
ALGORITHM = 'HS256'


bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')


class Gender(str, Enum):
    Male = "Male"
    Female = "Female"
    Other = "Other"


class CreateStudentRequest(BaseModel):
    username: str = Field(min_length=1)
    email: EmailStr
    first_name: str
    last_name: str
    register_number: int = Field(gt=0)
    date_of_birth: date
    gender: Gender
    phone_number: str
    course: str
    address: str
    password: str
        
        
class ValidateUser(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


def authenticate_user(username_or_email: str, password: str, db):
    user = db.query(Students).filter(or_(Students.username == username_or_email, Students.email == username_or_email)).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user


def create_access_token(username: str, user_id: int, user_email: str, expires_delta: timedelta):
    encode = {'sub': username, 'id': user_id, 'email': user_email}
    expires = datetime.utcnow() + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        user_email: str = payload.get('email')
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')
        return {'username': username, 'id': user_id, 'email': user_email}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_student(db: db_dependency, create_student_request: CreateStudentRequest):
    # Check if a user with the same username already exists
    existing_user = db.query(Students).filter(Students.username == create_student_request.username).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Username already exists')

    # Check if a user with the same email already exists
    existing_email = db.query(Students).filter(Students.email == create_student_request.email).first()
    if existing_email:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Email already exists')

    # Check if a user with the same register number already exists
    existing_register_number = db.query(Students).filter(Students.register_number == create_student_request.register_number).first()
    if existing_register_number:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Email already exists')

    try:
        create_student_model = Students(
            username=create_student_request.username,
            email=create_student_request.email,
            first_name=create_student_request.first_name,
            last_name=create_student_request.last_name,
            register_number=create_student_request.register_number,
            date_of_birth=create_student_request.date_of_birth,
            gender=create_student_request.gender,
            phone_number=create_student_request.phone_number,
            course=create_student_request.course,
            address=create_student_request.address,
            hashed_password=bcrypt_context.hash(create_student_request.password)
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str("Test String"+e))

    db.add(create_student_model)
    db.commit()


@router.post("/token", response_model=Token)
async def login_for_access_token(response: Response, validate_user: ValidateUser, db: db_dependency):
    user = authenticate_user(validate_user.username, validate_user.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')
    token = create_access_token(user.username, user.id, user.email, timedelta(minutes=20))
    response.set_cookie(key="access_token", value=token, httponly=True)
    return {'access_token': token, 'token_type': 'bearer'}


@router.put("/forgotPassword", status_code=status.HTTP_204_NO_CONTENT)
async def forgot_password(db: db_dependency, email: str = Form(...), new_password: str = Form(...)):
    user = db.query(Students).filter(Students.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    hashed_password = bcrypt_context.hash(new_password)
    user.hashed_password = hashed_password
    db.commit()

