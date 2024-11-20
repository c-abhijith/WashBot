from app.models import User,Vehicle
from app.helper.auth_helper import verify_password


def check_signup(data):
    required_fields = ["username", "password", "phonenumber", "role"]
    
    for field in required_fields:
        if field not in data:
            return {"message": f"Missing required field: {field}"}, 400
        if not data[field]:
            return {"message": f"{field} cannot be empty"}, 400
            
    if data["role"] not in ["user", "admin","staff"]:
        return {"message": "Invalid role. Must be 'user' or 'admin'"}, 400
    
    existing_user = User.query.filter_by(username=data["username"]).first()
    if existing_user:
        return {"message": "Username already exists"}, 400
    
    existing_phonenumber = User.query.filter_by(phonenumber=data["phonenumber"]).first()
    if existing_phonenumber:
        return {"message": "phonenumber already exists"}, 400
    
    return None

def check_login(data):
    required_fields = ["username", "password"]
    
    for field in required_fields:
        if field not in data:
            return {"message": f"Missing required field: {field}"}, 400
        if not data[field]:
            return {"message": f"{field} cannot be empty"}, 400
    user = User.query.filter_by(username=data["username"]).first()
    if not user:
        return {"message": "Invalid username"}, 401
    
    if not verify_password(data["password"], user.password):
        return {"message": "Invalid password"}, 401
    
    return None

def vechile_validation(data):
    required_fields = ["vehicle_name", "vehicle_model", "numberplate", "vehicle_type"]
    for field in required_fields:
        if field not in data:
            return {"message": f"Missing required field: {field}"}, 400
        
    if Vehicle.query.filter_by(numberplate=data["numberplate"]).first():
                return {"message": "Vehicle with this numberplate already exists"}, 400
    return None