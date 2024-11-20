
def signup_response(user):
    return {
            "message": "User created", 
            "user": {
                "id": str(user.id),
                "username": user.username,
                "role": user.role,
                "phonenumber": user.phonenumber
            }
        }

def login_response(access,refresh):
    return {
            "message": "Login successful",
                "accessToken": access,
                "refreshToken": refresh,
        }

def userdata(user):
    return {
                "message": "Profile retrieved successfully",
                "user": {
                    "profile_image":user.profile_image,
                    "username":user.username,
                    "phonenumber":user.phonenumber,
                    "role":user.role
                }
            }, 200

def user_to_dict(user):
    return {
        "id": user.id,
        "profile_image":user.profile_image,
        "username": user.username,
        "phonenumber": user.phonenumber,
        "role": user.role
    }
    
def user_all(user):
    return {
                "message": "Users retrieved successfully",
                "users": user,
                "total": len(user)
            }
def vechile_list(vehicle):
    return {
        "id": str(vehicle.id),
        "vehicle_image": vehicle.vehicle_image,
        "vehicle_name": vehicle.vehicle_name,
        "vehicle_model": vehicle.vehicle_model,
        "numberplate": vehicle.numberplate,
        "vehicle_type": vehicle.vehicle_type,
        "user_id":vehicle.user_id
        }
    
def vechile_response(data):
    return {
                "message": "Vechile listed successfully",
                "users": data,
                "total": len(data)
            }
    
def vechile_create(vehicle):
    return {
                "message": "Vehicle created successfully",
                "vehicle": {
                    "id": str(vehicle.id),
                    "vehicle_name": vehicle.vehicle_name,
                    "vehicle_model": vehicle.vehicle_model,
                    "numberplate": vehicle.numberplate,
                    "vehicle_type": vehicle.vehicle_type
                }
            }
def vechile_details(vehicle):
    return {
                "message": "Vehicle retrieved successfully",
                "vehicle": {
                    "id": str(vehicle.id),
                    "vehicle_name": vehicle.vehicle_name,
                    "vehicle_model": vehicle.vehicle_model,
                    "numberplate": vehicle.numberplate,
                    "vehicle_type": vehicle.vehicle_type,
                    "vehicle_image": vehicle.vehicle_image
                }
            }
    
