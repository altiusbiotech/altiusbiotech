"""
Cloudinary Helper Module
Handles all Cloudinary uploads and deletions
"""

import os
import cloudinary
import cloudinary.uploader
import cloudinary.api

def is_cloudinary_configured():
    """Check if Cloudinary environment variables are set"""
    cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME')
    api_key = os.getenv('CLOUDINARY_API_KEY')
    api_secret = os.getenv('CLOUDINARY_API_SECRET')

    if not all([cloud_name, api_key, api_secret]):
        print("[CLOUDINARY] Not configured - missing environment variables")
        return False

    # Check if values are still placeholders
    if cloud_name == 'your_cloud_name' or api_key == 'your_api_key':
        print("[CLOUDINARY] Not configured - placeholder values detected")
        return False

    # Configure Cloudinary
    cloudinary.config(
        cloud_name=cloud_name,
        api_key=api_key,
        api_secret=api_secret,
        secure=True
    )

    print(f"[CLOUDINARY] Configured successfully with cloud: {cloud_name}")
    return True


def upload_image(file, folder='altius-biotech'):
    """
    Upload image to Cloudinary

    Args:
        file: FileStorage object from request.files
        folder: Cloudinary folder path (e.g., 'altius-biotech/features')

    Returns:
        str: Cloudinary secure URL if successful, None if failed
    """
    if not is_cloudinary_configured():
        print("[CLOUDINARY] Upload skipped - not configured")
        return None

    try:
        print(f"[CLOUDINARY] Uploading to folder: {folder}")

        # Upload to Cloudinary
        result = cloudinary.uploader.upload(
            file,
            folder=folder,
            resource_type='image',
            allowed_formats=['jpg', 'jpeg', 'png', 'gif', 'webp']
        )

        # Return the secure HTTPS URL
        secure_url = result['secure_url']
        print(f"[CLOUDINARY] Upload successful!")
        print(f"[CLOUDINARY] Public ID: {result.get('public_id')}")
        print(f"[CLOUDINARY] Secure URL: {secure_url}")
        print(f"[CLOUDINARY] URL length: {len(secure_url)} characters")

        return secure_url

    except Exception as e:
        print(f"[CLOUDINARY] Upload error: {e}")
        import traceback
        traceback.print_exc()
        return None


def delete_file(url):
    """
    Delete file from Cloudinary by URL

    Args:
        url: Full Cloudinary URL (e.g., https://res.cloudinary.com/.../image.jpg)

    Returns:
        bool: True if deleted successfully, False otherwise
    """
    if not is_cloudinary_configured():
        return False

    if not url or not url.startswith('http'):
        return False

    try:
        # Extract public_id from URL
        # URL format: https://res.cloudinary.com/cloud_name/image/upload/v123456/folder/file.jpg
        parts = url.split('/')

        # Find the index of 'upload'
        upload_index = parts.index('upload')

        # Everything after 'upload/vXXXXXX/' is the public_id (without extension)
        public_id_parts = parts[upload_index + 2:]  # Skip 'upload' and version
        public_id_with_ext = '/'.join(public_id_parts)

        # Remove file extension
        public_id = public_id_with_ext.rsplit('.', 1)[0]

        print(f"[CLOUDINARY] Deleting public_id: {public_id}")

        # Delete from Cloudinary
        result = cloudinary.uploader.destroy(public_id)

        success = result.get('result') == 'ok'
        print(f"[CLOUDINARY] Delete result: {result}")
        return success

    except Exception as e:
        print(f"[CLOUDINARY] Delete error: {e}")
        return False
