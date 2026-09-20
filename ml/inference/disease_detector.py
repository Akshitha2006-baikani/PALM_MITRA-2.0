import os

import torch
import torch.nn as nn
from PIL import Image
from torchvision import transforms, models


# ---------------------------------------------------------
# PATHS
# ---------------------------------------------------------

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

MODEL_DIR = os.path.join(
    BASE_DIR,
    "models"
)

MODEL_PATH = os.path.join(
    MODEL_DIR,
    "palm_mitra_healthy_diseased_mobilenetv3.pth"
)


# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------

SCREENING_THRESHOLD = 0.80

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)


# ---------------------------------------------------------
# LOAD MODEL
# ---------------------------------------------------------

def load_disease_model():

    if not os.path.isfile(MODEL_PATH):
        raise FileNotFoundError(
            f"Disease model not found: {MODEL_PATH}"
        )

    checkpoint = torch.load(
        MODEL_PATH,
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

    class_to_idx = checkpoint["class_to_idx"]

    class_mapping = {
        index: class_name
        for class_name, index
        in class_to_idx.items()
    }

    return model, class_mapping


# ---------------------------------------------------------
# IMAGE PREPROCESSING
# ---------------------------------------------------------

def preprocess_image(image_path):

    if not os.path.isfile(image_path):
        raise FileNotFoundError(
            f"Image not found: {image_path}"
        )

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
    ).unsqueeze(0)

    return tensor


# ---------------------------------------------------------
# DISEASE DETECTION
# ---------------------------------------------------------

def detect_disease(
    image_path,
    model=None,
    class_mapping=None
):

    # Load model if not supplied
    if model is None or class_mapping is None:

        model, class_mapping = (
            load_disease_model()
        )

    tensor = preprocess_image(
        image_path
    ).to(DEVICE)

    with torch.no_grad():

        outputs = model(
            tensor
        )

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

    prediction = class_mapping[
        predicted_index
    ]

    # -----------------------------------------------------
    # CONFIDENCE CHECK
    # -----------------------------------------------------

    if confidence < SCREENING_THRESHOLD:

        status = "uncertain"

        message = (
            "The image could not be classified "
            "with enough confidence. Please upload "
            "a clearer oil-palm leaf image."
        )

    elif prediction == "healthy":

        status = "healthy"

        message = (
            "The oil-palm leaf appears healthy "
            "based on the screening model."
        )

    else:

        status = "problem_detected"

        message = (
            "The oil-palm leaf appears abnormal "
            "based on the screening model. "
            "Further diagnosis is required to "
            "identify the specific cause."
        )

    return {
        "prediction": prediction,
        "confidence": round(
            confidence,
            4
        ),
        "status": status,
        "message": message
    }


# ---------------------------------------------------------
# SIMPLE PUBLIC FUNCTION
# ---------------------------------------------------------

def analyze_disease(image_path):

    model, class_mapping = (
        load_disease_model()
    )

    result = detect_disease(
        image_path,
        model,
        class_mapping
    )

    result["image"] = os.path.basename(
        image_path
    )

    return result