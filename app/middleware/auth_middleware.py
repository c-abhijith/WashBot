from functools import wraps
from flask_jwt_extended import get_jwt_identity
from app.models import User
import uuid

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            current_user_id = get_jwt_identity()
            user_uuid = uuid.UUID(current_user_id)
            current_user = User.query.filter_by(id=user_uuid).first()
            
            if not current_user or current_user.role != 'admin':
                return {'message': 'Admin token required'}, 403
                
            return f(*args, **kwargs)
        except ValueError:
            return {'message': 'Invalid user ID'}, 400
        except Exception as e:
            return {'message': 'Authentication error', 'error': str(e)}, 500
    return decorated_function

def staff_admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            current_user_id = get_jwt_identity()
            user_uuid = uuid.UUID(current_user_id)
            current_user = User.query.filter_by(id=user_uuid).first()
            
            if not current_user or current_user.role not in ['admin', 'staff']:
                return {'message': 'Staff or Admin token required'}, 403
                
            return f(*args, **kwargs)
        except ValueError:
            return {'message': 'Invalid user ID'}, 400
        except Exception as e:
            return {'message': 'Authentication error', 'error': str(e)}, 500
    return decorated_function

def user_admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            current_user_id = get_jwt_identity()
            user_uuid = uuid.UUID(current_user_id)
            current_user = User.query.filter_by(id=user_uuid).first()
            
            if not current_user or current_user.role not in ['admin', 'user']:
                return {'message': 'User or Admin token required'}, 403
                
            return f(*args, **kwargs)
        except ValueError:
            return {'message': 'Invalid user ID'}, 400
        except Exception as e:
            return {'message': 'Authentication error', 'error': str(e)}, 500
    return decorated_function

def user_staff_admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            current_user_id = get_jwt_identity()
            user_uuid = uuid.UUID(current_user_id)
            current_user = User.query.filter_by(id=user_uuid).first()
            
            if not current_user or current_user.role not in ['admin', 'staff', 'user']:
                return {'message': 'Authentication required'}, 403
                
            return f(*args, **kwargs)
        except ValueError:
            return {'message': 'Invalid user ID'}, 400
        except Exception as e:
            return {'message': 'Authentication error', 'error': str(e)}, 500
    return decorated_function 