

def data_error(error):
    return {
                    "message": "Database error occurred",
                    "error": str(error)
                }

def unexcept_error(error):
     return {
                "message": "An unexpected error occurred",
                "error": str(error)
            }
