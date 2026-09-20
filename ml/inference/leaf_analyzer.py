import os

import torch
import torch.nn as nn
import numpy as np
from PIL import Image
from torchvision import transforms, models
from ultralytics import YOLO


# ---------------------------------------------------------
# PATHS
# ---------------------------------------------------------

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

MODEL_DIR = os.path.join(BASE_DIR, "models")

CLASSIFICATION_MODEL_PATH = os.path.join(
    MODEL_DIR,
    "palm_mitra_healthy_diseased_mobilenetv3.pth"
)

NUTRIENT_MODEL_PATH = os.path.join(
    MODEL_DIR,
    "palm_mitra_nutrient_yolo11n.pt"
)


# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------

SCREENING_THRESHOLD = 0.80

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)


# ---------------------------------------------------------
# LOAD HEALTHY / DISEASED MODEL
# ---------------------------------------------------------

def load_screening_model():

    checkpoint = torch.load(
        CLASSIFICATION_MODEL_PATH,
        map_location=DEVICE
    )

    model = models.mobilenet_v3_small(
        weights=None
    )

    model.classifier[3] = nn.Linear(
        model.classifier[3].in_features,
        2
    )

    model.load_state_dict(
        checkpoint["model_state_dict"]
    )

    model.to(DEVICE)
    model.eval()

    return model, checkpoint


# ---------------------------------------------------------
# LOAD NUTRIENT MODEL
# ---------------------------------------------------------

def load_nutrient_model():

    model = YOLO(
        NUTRIENT_MODEL_PATH
    )

    return model


# ---------------------------------------------------------
# HEALTHY / DISEASED SCREENING
# ---------------------------------------------------------

def screen_leaf(
    image_path,
    model,
    class_mapping
):

    image = Image.open(
        image_path
    ).convert("RGB")

    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[
                0.485,
                0.456,
                0.406
            ],
            std=[
                0.229,
                0.224,
                0.225
            ]
        )
    ])

    tensor = transform(
        image
    ).unsqueeze(0).to(DEVICE)

    with torch.no_grad():

        outputs = model(tensor)

        probabilities = torch.softmax(
            outputs,
            dim=1
        )[0]

    confidence, predicted_index = torch.max(
        probabilities,
        dim=0
    )

    confidence = float(
        confidence.item()
    )

    predicted_index = int(
        predicted_index.item()
    )

    # class_mapping is index -> class name
    prediction = class_mapping[
        predicted_index
    ]

    status = (
        "accepted"
        if confidence >= SCREENING_THRESHOLD
        else "uncertain"
    )

    return {
        "prediction": prediction,
        "confidence": round(
            confidence,
            4
        ),
        "status": status
    }


# ---------------------------------------------------------
# NUTRIENT DETECTION
# ---------------------------------------------------------

def detect_nutrients(
    image_path,
    model
):

    results = model.predict(
        source=image_path,
        imgsz=384,
        conf=0.25,
        verbose=False
    )

    detections = []

    for result in results:

        if result.boxes is None:
            continue

        for box in result.boxes:

            class_id = int(
                box.cls.item()
            )

            confidence = float(
                box.conf.item()
            )

            coordinates = (
                box.xyxy[0]
                .cpu()
                .numpy()
                .tolist()
            )

            name = model.names[
                class_id
            ]

            detections.append({
                "name": name,
                "confidence": round(
                    confidence,
                    4
                ),
                "box": coordinates
            })

    return detections


# ---------------------------------------------------------
# COMPLETE LEAF ANALYSIS
# ---------------------------------------------------------

def analyze_leaf(
    image_path,
    run_nutrient_detection=True
):

    if not os.path.isfile(
        image_path
    ):
        raise FileNotFoundError(
            f"Image not found: {image_path}"
        )

    # Load screening model
    screening_model, checkpoint = (
        load_screening_model()
    )

    # Recover class mapping
    class_to_idx = checkpoint[
        "class_to_idx"
    ]

    class_mapping = {
        index: class_name
        for class_name, index
        in class_to_idx.items()
    }

    # Run screening
    screening = screen_leaf(
        image_path,
        screening_model,
        class_mapping
    )

    response = {
        "image": os.path.basename(
            image_path
        ),
        "screening": screening,
        "nutrient_detection": {
            "enabled": False,
            "detections": []
        }
    }

    # -----------------------------------------------------
    # UNCERTAIN
    # -----------------------------------------------------

    if screening["status"] == "uncertain":

        response["status"] = "uncertain"

        response["message"] = (
            "The image could not be classified "
            "with enough confidence. Please upload "
            "a clearer oil-palm leaf image."
        )

        return response

    # -----------------------------------------------------
    # HEALTHY
    # -----------------------------------------------------

    if screening["prediction"] == "healthy":

        response["status"] = "healthy"

        response["message"] = (
            "The leaf appears healthy based on "
            "the screening model."
        )

        return response

    # -----------------------------------------------------
    # DISEASED / PROBLEM
    # -----------------------------------------------------

    if not run_nutrient_detection:

        response["status"] = (
            "problem_detected"
        )

        response["message"] = (
            "The leaf appears abnormal based "
            "on the screening model."
        )

        return response

    # -----------------------------------------------------
    # RUN NUTRIENT DETECTOR
    # -----------------------------------------------------

    nutrient_model = load_nutrient_model()

    detections = detect_nutrients(
        image_path,
        nutrient_model
    )

    response["nutrient_detection"] = {
        "enabled": True,
        "detections": detections
    }

    # -----------------------------------------------------
    # NUTRIENT INDICATION
    # -----------------------------------------------------

    if detections:

        highest_detection = max(
            detections,
            key=lambda item: item["confidence"]
        )

        response["status"] = (
            "nutrient_indication"
        )

        response["possible_condition"] = (
            highest_detection["name"]
        )

        response["detection_confidence"] = (
            highest_detection["confidence"]
        )

        response["message"] = (
            "The leaf shows a possible "
            "nutrient-deficiency pattern. "
            "Soil and field conditions should "
            "be checked before taking corrective action."
        )

    # -----------------------------------------------------
    # NO NUTRIENT PATTERN
    # -----------------------------------------------------

    else:

        response["status"] = (
            "problem_detected"
        )

        response["possible_condition"] = None

        response["detection_confidence"] = None

        response["message"] = (
            "The leaf appears abnormal based on "
            "the screening model, but the nutrient "
            "model did not find a clear nutrient-deficiency "
            "pattern."
        )

    return response