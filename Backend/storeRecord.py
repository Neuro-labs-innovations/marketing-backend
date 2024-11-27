
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import APIRouter
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import os
import io

router = APIRouter()

# MongoDB connection setup using Motor (async)
client = AsyncIOMotorClient('mongodb+srv://marketing:Neurolabs%40123@cluster0.wtf2o.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')

db = client["marketing"]
collection = db["Record"]


SCOPES = ['https://www.googleapis.com/auth/drive.file']
SERVICE_ACCOUNT_FILE = 'Backend/marketing-neuro-labs-bpo.json'  
API_NAME = 'drive'
API_VERSION = 'v3'


def authenticate_google_drive():
    creds = None
    try:

        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        
        
        drive_service = build(API_NAME, API_VERSION, credentials=creds)
        return drive_service

    except Exception as e:
        print(f"Error authenticating with Google Drive: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to authenticate with Google Drive.")

# Upload file to Google Drive in a specific folder (async)
async def upload_file_to_drive(file: UploadFile, folder_id: str):
    try:
        drive_service = authenticate_google_drive()
        file_content = io.BytesIO(await file.read())  # Use await to read the file asynchronously
        
        # Create file metadata
        file_metadata = {
            'name': file.filename,
            'parents': [folder_id]
        }
        
        media = MediaIoBaseUpload(file_content, mimetype=file.content_type)
        
        # Upload file to Google Drive
        uploaded_file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        return f'https://drive.google.com/file/d/{uploaded_file["id"]}/view'
    except Exception as e:
        print(f"Error uploading file to Google Drive: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to upload file to Google Drive.")

# Define your API endpoint to handle form submission
@router.post("/submit_form/")
async def submit_form(
    user_name: str = Form(...),
    company_name: str = Form(...),
    address: str = Form(...),
    contact_person: str = Form(...),
    contact_number: str = Form(...),  # Added contact_number parameter
    website_url: Optional[str] = Form(''),
    purpose: str = Form(...),
    status: str = Form(...),
    upload_time: str = Form(...),
    location: Optional[str] = Form(''),
    image_upload: UploadFile = File(...),
    visiting_card: Optional[UploadFile] = File(None)
):
    try:
        # Get the last record to generate a new serial number (asynchronous)
        last_record = await collection.find_one(sort=[("serial_number", -1)])
        serial_number = last_record["serial_number"] + 1 if last_record else 1

        # Prepare form data
        form_data = {
            "user_name": user_name,
            "company_name": company_name,
            "address": address,
            "contact_person": contact_person,
            "contact_number": contact_number,  # Save contact_number
            "website_url": website_url,
            "purpose": purpose,
            "status": status,
            "upload_time": upload_time,
            "location": location,
            "serial_number": serial_number,
        }

        # Define the folder IDs for image and visiting card directories in Google Drive
        images_folder_id = '1vQ9TQem0HCyrVFT7e5XUYYQiLz2uSFzK'
        visiting_card_folder_id = '1iknb6X9kEO0Q-CML9oSm9t-29DwkzcU6'

        # Upload the image
        image_path = None
        if image_upload:
            image_path = await upload_file_to_drive(image_upload, images_folder_id)
            form_data["image_path"] = image_path

        # Upload the visiting card
        visiting_card_path = None
        if visiting_card:
            visiting_card_path = await upload_file_to_drive(visiting_card, visiting_card_folder_id)
            form_data["visiting_card_path"] = visiting_card_path

        # Insert form data into MongoDB asynchronously
        result = await collection.insert_one(form_data)

        return {
            "status": "success",
            "data_id": str(result.inserted_id),
            "serial_number": serial_number,
            "image_path": image_path,
            "visiting_card_path": visiting_card_path
        }

    except Exception as e:
        print(f"Error submitting form: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while processing the request.")
