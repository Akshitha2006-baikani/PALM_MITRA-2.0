import sys
import os
import json

# Add project root to Python path
PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

sys.path.insert(0, PROJECT_ROOT)

from ml.inference.leaf_analyzer import analyze_leaf


IMAGE_PATH = r"C:\Users\user\Desktop\Akshitha\Plantintel(project)\AI Based PLANTINTEL\backend\dataset\rice_tungro\000030.jpg"


result = analyze_leaf(
    IMAGE_PATH,
    run_nutrient_detection=True
)

print(json.dumps(result, indent=2))