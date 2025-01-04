from fastapi import APIRouter, status, HTTPException
from pydantic import BaseModel, EmailStr
from datetime import datetime
from app.models.user import User
from ..config import collection_name_users
import bcrypt
from app.config.jwt_config import create_access_token

router = APIRouter()

class NewUser(BaseModel):
    name: str
    email: EmailStr 
    password: str

# Response model for API response
class Response(BaseModel):
    success: bool
    message: str
    user: object

@router.post(
    "/register/", 
    tags=["users"], 
    status_code=status.HTTP_201_CREATED
)
async def create_user(new_user: NewUser) -> Response:
    # Check if user already exists
    existing_user = collection_name_users.find_one({"email": new_user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash the password
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(new_user.password.encode('utf-8'), salt).decode('utf-8')

    # Create a new user document
    user = {
        "name": new_user.name,
        "email": new_user.email,
        "password": hashed_password,
        "holdings": [],
        "trades":[],
        "journal": [],
        "created_at": datetime.now(),  
        "is_banned": False,
        "ban_time": None
    }

    # Insert the new user into the MongoDB collection
    result = collection_name_users.insert_one(user)
    
    if result.inserted_id:
        new_user_with_id = {**user, "_id": str(result.inserted_id)}  # Include the inserted _id
        return Response(
            success=True, 
            message="User registered successfully", 
            user=new_user_with_id  # Return the full user object
        )
    else:
        raise HTTPException(status_code=500, detail="Failed to register user")


class LoginUser(BaseModel):
    email: EmailStr 
    password: str

# Pydantic models for request and response
class LoginUser(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    success: bool
    message: str
    access_token: str

@router.post(
    "/login/", 
    tags=["users"], 
    status_code=status.HTTP_200_OK,
    response_model=LoginResponse
)
async def login_user(login_user: LoginUser):
    # Check if user exists
    existing_user: User = collection_name_users.find_one({"email": login_user.email})
    if not existing_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist")
    
    # Validate password
    is_match = bcrypt.checkpw(
        login_user.password.encode('utf-8'), 
        existing_user["password"].encode('utf-8')
    )

    if not is_match:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    
    # Create token 
    access_token = create_access_token({"email": login_user.email})
    

    return LoginResponse(
        success=True,
        message=f"Welcome back, {existing_user['name']}!",
        access_token=access_token
    )

class ResetPassword(BaseModel):
    email: EmailStr 
    password: str

@router.post(
    "/reset/", 
    tags=["users"], 
    status_code=status.HTTP_200_OK
)
async def reset_password(reset_password: ResetPassword) -> Response:
    # Check if user exists
    existing_user:User = collection_name_users.find_one({"email": reset_password.email})
    if not existing_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist")
    
    # Hash the new password
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(reset_password.password.encode('utf-8'), salt).decode('utf-8')

    # Update the password in the database
    update_result = collection_name_users.update_one(
        {"email": reset_password.email}, 
        {"$set": {"password": hashed_password}}
    )

    # Check if the update was successful
    if update_result.modified_count == 1:
        return Response(
            success=True, 
            message="Password reset successfully", 
            user={"email": reset_password.email}
        )
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to reset password")

