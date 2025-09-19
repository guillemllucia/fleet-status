# src/uploader.py
import os
import cloudinary
import cloudinary.uploader
import streamlit as st

cloudinary.config(
    cloud_name=st.secrets["CLOUDINARY_CLOUD_NAME"],
    api_key=st.secrets["CLOUDINARY_API_KEY"],
    api_secret=st.secrets["CLOUDINARY_API_SECRET"],
    secure=True
)

def upload_image(file_to_upload, vehicle_alias: str) -> str:
    """
    Uploads and transforms an image file to Cloudinary, returning its secure URL.
    """
    try:
        # Add a transformation to crop the image to a 4:3 aspect ratio
        result = cloudinary.uploader.upload(
            file_to_upload,
            public_id=f"fleet-status/{vehicle_alias}",
            overwrite=True,
            resource_type="image",
            transformation=[
                {'width': 800, 'height': 600, 'crop': 'fill', 'gravity': 'auto'}
            ]
        )
        return result.get("secure_url")
    except Exception as e:
        print(f"Error uploading image: {e}")
        return None
