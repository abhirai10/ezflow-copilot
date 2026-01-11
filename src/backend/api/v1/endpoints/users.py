from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session


router = APIRouter()

@router.post("/", response_model=str)
def register_user():
    return "Hello From Fastapi"
