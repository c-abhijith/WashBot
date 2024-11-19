from werkzeug.security import generate_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
import bcrypt


def password_hash(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def access_token(user):
    return create_access_token(
                identity=str(user.id),
                additional_claims={
                    "username": user.username,
                    "role": user.role
                }
            )
def refres_token(user):
    create_refresh_token(
                identity=str(user.id),
                additional_claims={
                    "username": user.username,
                    "role": user.role
                }
            )