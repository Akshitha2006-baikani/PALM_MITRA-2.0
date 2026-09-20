
"""
Palm Mitra - FastAPI Backend

Connects the HTML/CSS/JavaScript frontend
to the Palm Mitra ML pipeline.
"""

import os
import shutil
import uuid

from fastapi import FastAPI, File, UploadFile, HTTPException
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


# ---------------------------------------------------------
# LEAF ANALYSIS ENDPOINT
# ---------------------------------------------------------

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