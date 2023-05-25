from werkzeug.security import check_password_hash
from crud import get_user_by_name, HttpError, owner_verification_advertisement
from flask import  request
from models import Role
from functools import wraps

roles = ['Admin','User']

def _issuing_permits(auth_date):
    username = auth_date['username']
    password = auth_date['password']
    user = get_user_by_name(username)
    check_password = check_password_hash(user.password,password)
    if check_password:
        return {'role':user.role, 'user_id':user.id}
    
    raise HttpError(401, 'error wrong password')

def user_limited_access(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        
        try:
            decoded_data = request.authorization.parameters
        except:
            raise HttpError (401, 'Authorization error')
        
        user_permit = _issuing_permits(decoded_data)
        roles = user_permit['role']
        user_id = user_permit['user_id']
        
        if roles == Role.admin:
            return func(*args, **kwargs)
        
        if user_id == int(request.view_args['user_id']):
            return func(*args, **kwargs)
        
        raise HttpError(403, 'access denied')
    
    return wrapper

def advertisement_limited_acces(func):
    @wraps(func)
    def wrapper(*args,**kwargs):

        try:
            decoded_data = request.authorization.parameters
        except:
            raise HttpError (401, 'Authorization error')
        
        user_permit = _issuing_permits(decoded_data)
        user_id = user_permit['user_id']
        role = user_permit['role']
        method = request.method

        if method == 'POST':
            return func(*args,**kwargs,user_id=user_id)
        
        if method == 'DELETE' or 'PATCH':
            request_advertisement_id = request.view_args['advertisement_id']
            if role == Role.admin:
                return func(*args,**kwargs)
            if role == Role.user:
                owner_verification_advertisement(user_id,request_advertisement_id)
                return func(*args,**kwargs)
    return wrapper