
"""
Palm Mitra - Recommendation Engine

Converts leaf-analysis results into simple,
farmer-friendly recommendations.

This module does NOT prescribe fertilizer doses.
It provides safe next-step guidance based on
the ML screening result.
"""


# ---------------------------------------------------------
# HEALTHY LEAF
# ---------------------------------------------------------

def healthy_recommendation():

    return {
        "title": "Leaf appears healthy",
        "priority": "low",
        "summary": (
            "The leaf appears healthy according to "
            "the screening model."
        ),
        "actions": [
            "Continue regular field monitoring.",
            "Maintain proper irrigation and drainage.",
            "Continue routine soil and nutrient management.",
            "Monitor new leaves for changes in colour or appearance."
        ],
        "next_step": (
            "Continue normal plantation management "
            "and monitor the crop regularly."
        )
    }


# ---------------------------------------------------------
# UNCERTAIN RESULT
# ---------------------------------------------------------

def uncertain_recommendation():

    return {
        "title": "Image needs further checking",
        "priority": "medium",
        "summary": (
            "The image could not be classified with "
            "enough confidence."
        ),
        "actions": [
            "Upload a clearer oil-palm leaf image.",
            "Use good lighting when taking the photograph.",
            "Capture the complete affected leaf if possible.",
            "Avoid blurry or heavily shadowed images."
        ],
        "next_step": (
            "Take a clearer photograph and perform "
            "the analysis again."
        )
    }


# ---------------------------------------------------------
# NUTRIENT INDICATION
# ---------------------------------------------------------

def nutrient_recommendation(condition, confidence):

    return {
        "title": "Possible nutrient-deficiency pattern",
        "priority": "medium",
        "summary": (
            f"The model detected a possible {condition} "
            f"pattern with {confidence * 100:.1f}% confidence."
        ),
        "actions": [
            "Inspect the affected leaves and surrounding plants.",
            "Check soil condition and recent fertilization history.",
            "Arrange a soil test before applying corrective fertilizer.",
            "Check irrigation, drainage and root-zone conditions.",
            "Compare symptoms across multiple palms."
        ],
        "next_step": (
            "Confirm the suspected deficiency using field "
            "observation and soil testing before taking "
            "corrective action."
        )
    }


# ---------------------------------------------------------
# ABNORMAL
# ---------------------------------------------------------
# ABNORMAL / DISEASED SCREENING
# ---------------------------------------------------------

def problem_recommendation():

    return {
        "title": "Abnormal leaf pattern detected",
        "priority": "high",
        "summary": (
            "The screening model identified an abnormal "
            "leaf pattern, but no clear nutrient-deficiency "
            "pattern was detected."
        ),
        "actions": [
            "Inspect the affected palm carefully.",
            "Check nearby palms for similar symptoms.",
            "Look for insects, fungal symptoms, lesions or unusual discoloration.",
            "Check irrigation and drainage conditions.",
            "Avoid applying fertilizer or pesticides based only on this prediction.",
            "Consult an agricultural expert if symptoms continue or spread."
        ],
        "next_step": (
            "Perform a field inspection and obtain expert "
            "diagnosis if the abnormal symptoms persist."
        )
    }


# ---------------------------------------------------------
# MAIN RECOMMENDATION FUNCTION
# ---------------------------------------------------------

def generate_recommendation(analysis_result):

    if not isinstance(analysis_result, dict):
        raise TypeError(
            "analysis_result must be a dictionary."
        )

    status = analysis_result.get("status")

    # -----------------------------------------------------
    # HEALTHY
    # -----------------------------------------------------

    if status == "healthy":
        return healthy_recommendation()

    # -----------------------------------------------------
    # UNCERTAIN
    # -----------------------------------------------------

    if status == "uncertain":
        return uncertain_recommendation()

    # -----------------------------------------------------
    # NUTRIENT INDICATION
    # -----------------------------------------------------

    if status == "nutrient_indication":

        condition = analysis_result.get(
            "possible_condition",
            "unknown nutrient"
        )

        confidence = analysis_result.get(
            "detection_confidence",
            0.0
        )

        return nutrient_recommendation(
            condition,
            confidence
        )

    # -----------------------------------------------------
    # PROBLEM DETECTED
    # -----------------------------------------------------

    if status == "problem_detected":
        return problem_recommendation()

    # -----------------------------------------------------
    # UNKNOWN STATUS
    # -----------------------------------------------------

    return {
        "title": "Further assessment required",
        "priority": "medium",
        "summary": (
            "The analysis returned an unexpected result."
        ),
        "actions": [
            "Repeat the analysis with a clear oil-palm image.",
            "Inspect the plant in the field."
        ],
        "next_step": (
            "Repeat the analysis and verify the result "
            "with field observations."
        )
    }


# ---------------------------------------------------------
# SIMPLE TEST
# ---------------------------------------------------------

if __name__ == "__main__":

    sample_result = {
        "status": "problem_detected"
    }

    recommendation = generate_recommendation(
        sample_result
    )

    import json

    print(
        json.dumps(
            recommendation,
            indent=2
        )
    )
