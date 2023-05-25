from models import Session, Users, Advertisements, UserAdvertisements
from werkzeug.security import generate_password_hash

class HttpError(Exception):
    def __init__(self,status_code, message) -> None:
        self.status_code = status_code
        self.message = message  

def get_user(session,id):
    user = session.get(Users,id)
    if user is None:
        raise HttpError(404, message='user not found')
    return user

def get_user_by_name(name):
    with Session() as session:
        query = session.query(Users).filter(Users.username == name).first()
        if query == None:
            raise HttpError(404, message='user not found')
        return query

def get_advertisement(session,id):
    advertisement = session.get(Advertisements,id)
    if advertisement is None:
        raise HttpError(404, message='advertisement not found')
    return advertisement

def owner_verification_advertisement(user_id,advertisement_id):
    with Session() as session:
        query = session.query(UserAdvertisements).\
        filter(
            UserAdvertisements.user_id == user_id,
            UserAdvertisements.advertisement_id == advertisement_id
        ).first()
        if query == None:
            raise HttpError(403,'possession is not confirmed')

class UserCRUD():

    @staticmethod
    def create(username,password,email):
        with Session() as session:
            password = generate_password_hash(password)
            user = Users(username=username,password=password,email=email)
            session.add(user)
            session.commit()
            return get_user(session,user.id)

    @staticmethod
    def read(user_id):
        with Session() as session:
            return get_user(session,user_id)

    @staticmethod
    def update(user_id,username=None,password=None,email=None):
        with Session() as session:
            user = get_user(session, user_id)
            if username:
                user.username = username
            if password:
                user.password = generate_password_hash(password)
            if email:
                user.email = email
            session.commit()
            return get_user(session, user.id)

    @staticmethod
    def delete(user_id):
        with Session() as session:
            user = get_user(session,user_id)
            session.delete(user)
            session.commit()
            return user


class AdvertisementCRUD():
    @staticmethod
    def create(user_obj,title,description):
        with Session() as session:

            advertisement = Advertisements(title=title,description=description)
            session.add(advertisement)
            session.commit()
            user_advertisement = UserAdvertisements(user_id = user_obj.id, advertisement_id = advertisement.id)
            session.add(user_advertisement)
            session.commit()
            return session.query(Advertisements).get(advertisement.id)

    @staticmethod
    def all_user_post(user_obj):
        with Session() as session:
            query = session.query(Users,Advertisements).select_from(Users).join(UserAdvertisements).filter(UserAdvertisements.user_id == user_obj.id)
            return query.all()
        
    @staticmethod
    def all_post_by_title(title):
        with Session() as session:
            query = session.query(Advertisements).filter(Advertisements.title == title)
            return query.all()


    @staticmethod
    def update(advertisement_id,title =None,description=None):
        with Session() as session:
            advertisement = get_advertisement(session,advertisement_id)
            if title:
                advertisement.title = title
            if description:
                advertisement.description = description
            session.commit()
            return get_advertisement(session,advertisement_id)
    
    @staticmethod
    def delete(advertisement_id):
        with Session() as session:
            advertisement = get_advertisement(session,advertisement_id)
            session.delete(advertisement)
            session.commit()
            return advertisement 




if __name__ == '__main__':
    #UserCRUD().create('testcrud2','testpassword2','test@email.com2')
    #print(UserCRUD().read(1222))
    #UserCRUD().update(10,email='222')
    #UserCRUD().delete(10)
    #AdvertisementCRUD().create(UserCRUD().read(1), 'testtred', 'this is test')
    #print(AdvertisementCRUD().read(UserCRUD().read(1)))
    owner_verification_advertisement(1,2)
    pass
