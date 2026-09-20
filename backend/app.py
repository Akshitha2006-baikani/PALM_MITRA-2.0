
"""
Palm Mitra - FastAPI Backend

Connects the HTML/CSS/JavaScript frontend
to the Palm Mitra ML pipeline.
"""

import os
import shutil
import uuid
from sqlalchemy.orm import Session
from fastapi import Depends

from database.database import Base, engine, get_db
from database.models import User, Farm
from backend.auth import hash_password ,verify_password
from backend.auth_token import (
    create_access_token,
    decode_access_token
)
from backend.schemas import SignupRequest, LoginRequest

from fastapi import (FastAPI, File, UploadFile, HTTPException, Depends,Header)
from fastapi.middleware.cors import CORSMiddleware

from ml.inference.palm_mitra_pipeline import analyze_palm_leaf
from weather.weather_service import get_current_weather
from chatbot.assistant import ask_palm_mitra

# ---------------------------------------------------------
# PATHS
# ---------------------------------------------------------

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

UPLOAD_DIR = os.path.join(
    BASE_DIR,
    "backend",
    "uploads"
)

os.makedirs(
    UPLOAD_DIR,
    exist_ok=True
)


# ---------------------------------------------------------
# FASTAPI APPLICATION
# ---------------------------------------------------------

app = FastAPI(
    title="Palm Mitra API",
    description=(
        "AI-powered oil-palm cultivation "
        "and leaf analysis backend."
    ),
    version="1.0.0"
)

Base.metadata.create_all(bind=engine)
# ---------------------------------------------------------
# CORS
# ---------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# ROOT ENDPOINT
# ---------------------------------------------------------

@app.get("/")
def root():

    return {
        "application": "Palm Mitra",
        "status": "running",
        "message": "Palm Mitra API is running successfully."
    }


# ---------------------------------------------------------
# HEALTH ENDPOINT
# ---------------------------------------------------------

@app.get("/api/health")
def health_check():

    return {
        "status": "healthy",
        "service": "Palm Mitra API"
    }


@app.post("/api/auth/signup")
def signup(
    request: SignupRequest,
    db: Session = Depends(get_db)
):
    existing_user = (
        db.query(User)
        .filter(User.email == request.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="An account with this email already exists."
        )

    if len(request.password) < 8:
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 8 characters long."
        )

    new_user = User(
        name=request.name.strip(),
        email=request.email.lower().strip(),
        password_hash=hash_password(
            request.password
        )
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "success": True,
        "message": "Account created successfully.",
        "user": {
            "id": new_user.id,
            "name": new_user.name,
            "email": new_user.email
        }
    }

@app.post("/api/auth/login")
def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    user = (
        db.query(User)
        .filter(User.email == request.email.lower().strip())
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password."
        )

    if not verify_password(
        request.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password."
        )

    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "email": user.email
        }
    )

    return {
        "success": True,
        "message": "Login successful.",
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email
        }
    }

@app.get("/api/auth/me")
def get_current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db)
):
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization header is required."
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization header."
        )

    token = authorization.replace("Bearer ", "", 1)

    payload = decode_access_token(token)

    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token."
        )

    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid token."
        )

    user = (
        db.query(User)
        .filter(User.id == int(user_id))
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found."
        )

    return {
        "success": True,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email
        }
    }

# ---------------------------------------------------------
# FARM PROFILE ENDPOINTS
# ---------------------------------------------------------

@app.get("/api/farm")
def get_farm(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db)
):
    # Check authorization header
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization header is required."
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization header."
        )

    # Extract token
    token = authorization.replace("Bearer ", "", 1)

    # Decode token
    payload = decode_access_token(token)

    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token."
        )

    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid token."
        )

    # Check user exists
    user = (
        db.query(User)
        .filter(User.id == int(user_id))
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found."
        )

    # Find farm belonging to this user
    farm = (
        db.query(Farm)
        .filter(Farm.user_id == user.id)
        .first()
    )

    # User has not created a farm yet
    if not farm:
        return {
            "success": True,
            "farm": None
        }

    return {
        "success": True,
        "farm": {
            "id": farm.id,
            "name": farm.name,
            "location": farm.location,
            "area": farm.area,
            "palms": farm.palms,
            "plantationType": farm.plantation_type,
            "waterSource": farm.water_source,
            "irrigation": farm.irrigation,
            "soil": farm.soil,
            "plantationDate": farm.plantation_date
        }
    }


@app.post("/api/farm")
def save_farm(
    farm_data: dict,
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db)
):
    # Check authorization header
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization header is required."
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization header."
        )

    # Extract token
    token = authorization.replace("Bearer ", "", 1)

    # Decode token
    payload = decode_access_token(token)

    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token."
        )

    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid token."
        )

    # Check user exists
    user = (
        db.query(User)
        .filter(User.id == int(user_id))
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found."
        )

    # Check whether the user already has a farm
    farm = (
        db.query(Farm)
        .filter(Farm.user_id == user.id)
        .first()
    )

    if farm:
        # Update existing farm
        farm.name = farm_data.get("name", farm.name)
        farm.location = farm_data.get("location", farm.location)
        farm.area = farm_data.get("area", farm.area)
        farm.palms = farm_data.get("palms", farm.palms)
        farm.plantation_type = farm_data.get(
            "plantationType",
            farm.plantation_type
        )
        farm.water_source = farm_data.get(
            "waterSource",
            farm.water_source
        )
        farm.irrigation = farm_data.get(
            "irrigation",
            farm.irrigation
        )
        farm.soil = farm_data.get(
            "soil",
            farm.soil
        )
        farm.plantation_date = farm_data.get(
            "plantationDate",
            farm.plantation_date
        )

    else:
        # Create new farm
        farm = Farm(
            user_id=user.id,
            name=farm_data.get("name", "My Palm Farm"),
            location=farm_data.get("location"),
            area=farm_data.get("area"),
            palms=farm_data.get("palms"),
            plantation_type=farm_data.get("plantationType"),
            water_source=farm_data.get("waterSource"),
            irrigation=farm_data.get("irrigation"),
            soil=farm_data.get("soil"),
            plantation_date=farm_data.get("plantationDate")
        )

        db.add(farm)

    db.commit()
    db.refresh(farm)

    return {
        "success": True,
        "message": "Farm profile saved successfully.",
        "farm": {
            "id": farm.id,
            "name": farm.name,
            "location": farm.location,
            "area": farm.area,
            "palms": farm.palms,
            "plantationType": farm.plantation_type,
            "waterSource": farm.water_source,
            "irrigation": farm.irrigation,
            "soil": farm.soil,
            "plantationDate": farm.plantation_date
        }
    }
# ---------------------------------------------------------
# LEAF ANALYSIS ENDPOINT
# -------------------------------------------------


@app.post("/api/analyze-leaf")
async def analyze_leaf(
    file: UploadFile = File(...)
):

    # -----------------------------------------------------
    # CHECK FILE TYPE
    # -----------------------------------------------------

    allowed_types = [
        "image/jpeg",
        "image/png",
        "image/webp"
    ]

    if file.content_type not in allowed_types:

        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid image format. Please upload "
                "a JPG, PNG or WEBP image."
            )
        )

    # -----------------------------------------------------
    # CREATE UNIQUE FILE NAME
    # -----------------------------------------------------

    extension = os.path.splitext(
        file.filename or ""
    )[1].lower()

    if not extension:
        extension = ".jpg"

    filename = (
        f"{uuid.uuid4().hex}"
        f"{extension}"
    )

    image_path = os.path.join(
        UPLOAD_DIR,
        filename
    )

    # -----------------------------------------------------
    # SAVE UPLOADED IMAGE
    # -----------------------------------------------------

    try:

        with open(
            image_path,
            "wb"
        ) as buffer:

            shutil.copyfileobj(
                file.file,
                buffer
            )

        # -------------------------------------------------
        # RUN PALM MITRA ML PIPELINE
        # -------------------------------------------------

        result = analyze_palm_leaf(
            image_path,
            run_nutrient_detection=True
        )

        return {
            "success": True,
            "filename": file.filename,
            "result": result
        }

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )

    finally:

        # -------------------------------------------------
        # REMOVE TEMPORARY IMAGE
        # -------------------------------------------------

        if os.path.exists(image_path):

            os.remove(
                image_path
            )
@app.get("/api/weather")
def weather(city: str):
    try:
        return {
            "success": True,
            "weather": get_current_weather(city)
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except RuntimeError as error:
        raise HTTPException(
            status_code=502,
            detail=str(error)
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error)
        )
# ---------------------------------------------------------
# AI ASSISTANT ENDPOINT
# ---------------------------------------------------------

@app.post("/api/chat")
async def chat(request: dict):

    message = request.get("message", "").strip()

    farm_context = request.get(
        "farm_context"
    )

    weather_context = request.get(
        "weather_context"
    )

    leaf_context = request.get(
        "leaf_context"
    )

    if not message:

        raise HTTPException(
            status_code=400,
            detail="Message is required."
        )

    try:

        response = ask_palm_mitra(
            message=message,
            farm_context=farm_context,
            weather_context=weather_context,
            leaf_context=leaf_context
        )

        return {
            "success": True,
            "response": response
        }

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )