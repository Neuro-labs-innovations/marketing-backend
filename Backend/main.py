
from fastapi import FastAPI, HTTPException,Request,Depends, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel,EmailStr
from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
import logging
from typing import Optional
from bson import ObjectId
from email_validator import validate_email, EmailNotValidError
import uvicorn
import random
import string
from . import admin,resetPassword,storeRecord,user,adminDisplay


app = FastAPI()
app.include_router(admin.router)
app.include_router(resetPassword.router)
app.include_router(user.router)
app.include_router(storeRecord.router)
app.include_router(adminDisplay.router)


client = AsyncIOMotorClient('mongodb+srv://marketing:Neurolabs%40123@cluster0.wtf2o.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client["marketing"]


# Add CORS middleware
origins = [
    "http://localhost:5173",  
    "http://marketing.neuro-labs.in" 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Refuse:-

@app.get('/')
def display():
    return {'message':"Marketing"}
