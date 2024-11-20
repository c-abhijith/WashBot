import cloudinary
import cloudinary.uploader
from flask import current_app

def configure_cloudinary():
    cloudinary.config(
        cloud_name=current_app.config['CLOUDINARY_CLOUD_NAME'],
        api_key=current_app.config['CLOUDINARY_API_KEY'],
        api_secret=current_app.config['CLOUDINARY_API_SECRET']
    )

def upload_image(file, folder):
    try:
        # Configure cloudinary
        configure_cloudinary()
        
        # Upload file
        result = cloudinary.uploader.upload(
            file,
            folder=folder,
            resource_type="auto"
        )
        
        return {
            'success': True,
            'url': result['secure_url'],
            'public_id': result['public_id']
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def delete_image(public_id):
    try:
        # Configure cloudinary
        configure_cloudinary()
        
        # Delete file
        result = cloudinary.uploader.destroy(public_id)
        
        return {
            'success': True,
            'result': result
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        } 