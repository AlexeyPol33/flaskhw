from flask import Flask, jsonify, request
from flask.views import MethodView
from models import Session, Users, Advertisements, UserAdvertisements
from sqlalchemy.exc import IntegrityError
from crud import UserCRUD, AdvertisementCRUD, HttpError
from validation_model import CreateUser,\
PatchUser,CreateAdvertisement,PatchAdvertisement,validate_json,check_post_limit
from crud import UserCRUD, AdvertisementCRUD
from auth import user_limited_access, advertisement_limited_acces
from functools import wraps

app = Flask("app")

@app.errorhandler(HttpError)
def http_error_handler(error: HttpError):
    error_message = {"status": "error", "description": error.message}
    response = jsonify(error_message)
    response.status_code = error.status_code
    return response

def user_jsonify(user_obj):
    return jsonify (
            {
            'id': user_obj.id,
            'username': user_obj.username,
            'email': user_obj.email,
            'creation_time': user_obj.create_time.isoformat(),
            }
    )

def advertisement_jsonify(advertisement_obj):
    return jsonify(
        {
            'id': advertisement_obj.id,
            'title': advertisement_obj.title,
            'description': advertisement_obj.description,
            'create_time':advertisement_obj.create_time
        }
    )

class UserView(MethodView):

    @user_limited_access
    def get(self, user_id): 
        user = UserCRUD.read(user_id)
        return user_jsonify(user)
    
    def post(self):
        json_data = request.json
        for key in json_data.keys():
            json_data[key] = validate_json(request.json, CreateUser)[key]
        user = user_jsonify(UserCRUD().create(**json_data))
        return user

    @user_limited_access
    def patch(self, user_id):
        json_data = request.json
        for key in json_data.keys():
            json_data[key] = validate_json(request.json, PatchUser)[key]
        user = UserCRUD().update(user_id,**json_data)
        return user_jsonify(user)

    @user_limited_access
    def delete(self,user_id):
        user = UserCRUD.delete(user_id)
        return user_jsonify(user)

class AdvertisementView(MethodView):

    def get(self,title):
        query = AdvertisementCRUD.all_post_by_title(title)
        advertisements = []
        for advertisement_obj in query:
           advertisements.append(advertisement_jsonify(advertisement_obj).json)
        return advertisements

    @advertisement_limited_acces
    def post(self,user_id=None):
        user = UserCRUD.read(user_id)
        check_post_limit(user)
        json_data = request.json
        for key in json_data.keys():
            json_data[key] = validate_json(request.json,CreateAdvertisement)[key]
        try:
            advertisement = AdvertisementCRUD.create(user,**json_data)
        except:
            raise HttpError(400,'Bad Request')
        return advertisement_jsonify(advertisement)

    @advertisement_limited_acces
    def patch(self,advertisement_id,user_id=None):
        json_data = request.json
        for key in json_data.keys():
            json_data[key] = validate_json(request.json, PatchAdvertisement)[key]
        advertisement = AdvertisementCRUD.update(**json_data)
        return advertisement

    @advertisement_limited_acces
    def delete(self,advertisement_id):
        advertisement = AdvertisementCRUD.delete(advertisement_id)
        return advertisement_jsonify(advertisement)

    
app.add_url_rule(
    "/user/<int:user_id>",
    view_func=UserView.as_view("with_user_id"),
    methods=["GET", "PATCH", "DELETE"],
)

app.add_url_rule(
    "/user/", 
    view_func=UserView.as_view("create_user"),
    methods=["POST"]
)

app.add_url_rule(
    "/advertisement/<int:advertisement_id>",
    view_func=AdvertisementView.as_view("with_advertisement_id"),
    methods = ["PATCH", "DELETE"]
)

app.add_url_rule(
    "/advertisement/<string:title>",
    view_func=AdvertisementView.as_view("with_title"),
    methods = ["GET"]
)

app.add_url_rule(
    "/advertisement/",
    view_func=AdvertisementView.as_view("create_advertisement"),
    methods=["POST"]
)

if __name__ == '__main__':
    app.run()
