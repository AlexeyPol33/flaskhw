
from crud import AdvertisementCRUD, HttpError
from pydantic import ValidationError
from typing import Optional, Type
from models import Users,Role,Session
import pydantic
import re

MAX_ADVERTISEMENT = 5 # Максимальное количество постов которые может опубликовать 1 пользователь

class CreateUser(pydantic.BaseModel):
    username: str
    password: str
    email: str

    @pydantic.validator("password")
    def validate_password(cls, value):
        if len(value) < 8:
            raise HttpError(400,"Password is too short")
        return value
    
    @pydantic.validator("email")
    def validate_email(cls,value):
        patern='\w*(@)\w*([.])\w*'
        valid_email = re.fullmatch(patern,value)
        if valid_email == None:
            raise HttpError(400,'email not valide')
        return value

    @pydantic.validator('username')
    def validate_username(cls,value):
        with Session() as session:
            user = session.query(Users).filter_by(username=value).first()
            if user != None:
                raise HttpError(409,'username is buisy')
            return value

class PatchUser(pydantic.BaseModel):
    username: Optional[str]
    password: Optional[str]
    email: Optional[str]

    @pydantic.validator("password")
    def validate_password(cls, value):
        if len(value) < 8:
            raise HttpError(400,"Password is too short")
        return value
    
    @pydantic.validator("email")
    def validate_email(cls,value):
        patern='\w*(@)\w*([.])\w*'
        valid_email = re.fullmatch(patern,value)
        if valid_email == None:
            raise HttpError(400,'email not valide')
        return value
    
    @pydantic.validator('username')
    def validate_username(cls,value):
        with Session() as session:
            user = session.query(Users).filter_by(username=value).first()
            if user != None:
                raise HttpError(409,'username is buisy')
            return value

class CreateAdvertisement(pydantic.BaseModel):
    title:Optional[str]
    description:Optional[str]
    
    @pydantic.validator('title')
    def validate_title(cls,value):
        if 5 > len(value) or len(value) > 20:
            raise HttpError(400,'The title cannot be less than 5 characters or more than 20 characters')
        else:
            return value
    
    @pydantic.validator('description')
    def validate_description(cls,value):
        if 10 > len(value) or len(value) > 500:
            raise HttpError(400,'The title cannot be less than 10 characters or more than 500 characters')
        else:
            return value
    
class PatchAdvertisement(pydantic.BaseModel):
    title:Optional[str]
    description:Optional[str]

    @pydantic.validator('title')
    def validate_title(cls,value):
        if 5 > len(value) or len(value) > 20:
            raise HttpError(400,'The title cannot be less than 5 characters or more than 20 characters')
        else:
            return value
    
    @pydantic.validator('description')
    def validate_description(cls,value):
        if 10 > len(value) or len(value) > 500:
            raise HttpError(400,'The title cannot be less than 10 characters or more than 500 characters')
        else:
            return value
        
VALIDATION_CLASS = Type[CreateUser] | Type[PatchUser] | Type[CreateAdvertisement] | Type[PatchAdvertisement]

def validate_json(json_data: dict, validation_model: VALIDATION_CLASS):
    try:
        model_obj = validation_model(**json_data)
        model_obj_dict = model_obj.dict(exclude_none=True)
    except ValidationError as err:
        raise HttpError(400, message=err.errors())
    return model_obj_dict

def check_post_limit(user_obj):
    if user_obj.role == Role.admin:
        return
    all_posts = AdvertisementCRUD.all_user_post(user_obj)
    if len(all_posts) >= MAX_ADVERTISEMENT:
       raise HttpError(400,'the ad limit is exceeded')
    return

