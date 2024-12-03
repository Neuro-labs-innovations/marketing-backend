import certifi
from fastapi import FastAPI, APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from motor.motor_asyncio import AsyncIOMotorClient  
from bson import ObjectId
from datetime import datetime
from starlette.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import os

router = APIRouter()

# MongoDB configuration using Motor (Async)
client = AsyncIOMotorClient('mongodb+srv://marketing:Neurolabs%40123@cluster0.wtf2o.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0', tls=True, tlsCAFile=certifi.where())
db = client["marketing"]
collection = db["Record"]

# Define models
class RecordResponse(BaseModel):
    serial_number: int
    user_name: str
    address: str
    website_url: str
    contact_person: str
    contact_number: str
    company_name: str
    status: str
    purpose: str
    date_created: str
    image_url: Optional[str] = ""  
    visiting_card_url: Optional[str] = ""  
    location: Optional[str] = "" 

    class Config:
        orm_mode = True


# The directory creation code is now removed as it is not needed in a read-only filesystem environment
# Removed the ensure_directories_exist function

@router.get("/records/", response_model=List[RecordResponse])
async def get_records():
    try:
        # Fetch the records from the MongoDB collection
        records = await collection.find().sort("serial_number", -1).to_list(length=100)
        response_data = []

        for record in records:
            # Prepare the data to return
            record_data = {
                "serial_number": record["serial_number"],  
                "user_name": record.get('user_name', ''),
                "company_name": record.get('company_name', ''),
                "status": record.get('status', ''),
                "purpose": record.get('purpose', ''),
                "date_created": record.get('upload_time', datetime.utcnow().isoformat()),
                "image_url": record.get('image_path', ''), 
                "visiting_card_url": record.get('visiting_card_path', ''),  
                "location": record.get('location', '')
            }
            response_data.append(record_data)
        
        return JSONResponse(content=response_data)

    except Exception as e:
        # Handle any errors and return a 500 internal server error
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/records/{serial_number}", response_model=RecordResponse)
async def get_record(serial_number: int):
    try:
        # Fetch a single record by serial_number
        record = await collection.find_one({"serial_number": serial_number})
        if record:
            return {
                "serial_number": record["serial_number"],
                "user_name": record["user_name"],
                "company_name": record["company_name"],
                "address": record["address"],  
                "contact_person": record["contact_person"],  
                "contact_number": record["contact_number"],  
                "website_url": record["website_url"],  
                "status": record["status"],
                "purpose": record["purpose"],
                "upload_time": record["upload_time"], 
                "date_created": record.get('upload_time', datetime.utcnow().isoformat()),
                "location": record["location"],
                "image_url": record.get('image_path', ''),  
                "visiting_card_url": record.get('visiting_card_path', ''),  
            }
        else:
            raise HTTPException(status_code=404, detail="Record not found")
    
    except Exception as e:
        # Handle any errors and return a 500 internal server error
        raise HTTPException(status_code=500, detail="Internal Server Error")
