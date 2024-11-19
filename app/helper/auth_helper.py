from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token

def password_hash(password):
    return generate_password_hash(password, method='pbkdf2:sha256')

def verify_password(password, hashed_password):
    return check_password_hash(hashed_password, password)

def access_token(user):
    return create_access_token(
                identity=str(user.id),
                additional_claims={
                    "username": user.username,
                    "role": user.role
                }
            )

def refres_token(user):
    return create_refresh_token(
                identity=str(user.id),
                additional_claims={
                    "username": user.username,
                    "role": user.role
                }
            )