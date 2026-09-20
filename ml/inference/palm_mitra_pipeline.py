
"""
Palm Mitra - Complete ML Pipeline

Connects:
1. Leaf screening
2. Nutrient detection
3. Recommendation engine
"""

import os
import json

from ml.inference.leaf_analyzer import analyze_leaf
from recommendation_engine.recommendation import (
    generate_recommendation
)


# ---------------------------------------------------------
# COMPLETE ANALYSIS
# ---------------------------------------------------------

def analyze_palm_leaf(
    image_path,
    run_nutrient_detection=True
):
    """
    Run complete Palm Mitra leaf analysis.

    Returns:
        dictionary containing:
        - ML analysis
        - farmer recommendation
    """

    if not os.path.isfile(image_path):
        raise FileNotFoundError(
            f"Image not found: {image_path}"
        )

    # -----------------------------------------------------
    # STEP 1: ML ANALYSIS
    # -----------------------------------------------------

    analysis = analyze_leaf(
        image_path,
        run_nutrient_detection=run_nutrient_detection
    )

    # -----------------------------------------------------
    # STEP 2: RECOMMENDATION
    # -----------------------------------------------------

    recommendation = generate_recommendation(
        analysis
    )

    # -----------------------------------------------------
    # STEP 3: COMBINE RESULTS
    # -----------------------------------------------------

    return {
        "analysis": analysis,
        "recommendation": recommendation
    }


# ---------------------------------------------------------
# TEST
# ---------------------------------------------------------

if __name__ == "__main__":

    IMAGE_PATH = "test_leaf.jpg"

    result = analyze_palm_leaf(
        IMAGE_PATH,
        run_nutrient_detection=True
    )

    print(
        json.dumps(
            result,
            indent=2
        )
    )
