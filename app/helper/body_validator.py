from app.models import User


def check_signup(data):
    required_fields = ["username", "password", "phonenumber", "role"]
    
    for field in required_fields:
        if field not in data:
            return {"message": f"Missing required field: {field}"}, 400
        if not data[field]:
            return {"message": f"{field} cannot be empty"}, 400
            
    if data["role"] not in ["user", "admin"]:
        return {"message": "Invalid role. Must be 'user' or 'admin'"}, 400
    
    return None

def check_login(data):
    required_fields = ["username", "password"]
    
    for field in required_fields:
        if field not in data:
            return {"message": f"Missing required field: {field}"}, 400
        if not data[field]:
            return {"message": f"{field} cannot be empty"}, 400
    
    return None