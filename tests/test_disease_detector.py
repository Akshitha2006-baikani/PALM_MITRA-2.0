import sys
import os
import json

# Add Palm Mitra project root
PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

sys.path.insert(
    0,
    PROJECT_ROOT
)

from ml.inference.disease_detector import analyze_disease


# ---------------------------------------------------------
# TEST IMAGE
# ---------------------------------------------------------

IMAGE_PATH = r"C:\Users\user\Desktop\Akshitha\Plantintel(project)\AI Based PLANTINTEL\backend\dataset\rice_tungro\000030.jpg"


# ---------------------------------------------------------
# RUN DISEASE DETECTION
# ---------------------------------------------------------

result = analyze_disease(
    IMAGE_PATH
)


# ---------------------------------------------------------
# DISPLAY RESULT
# ---------------------------------------------------------

print(
    json.dumps(
        result,
        indent=2
    )
)