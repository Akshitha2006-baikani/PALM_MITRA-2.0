"""
Palm Mitra - AI Assistant

Gemini-powered agricultural assistant for oil-palm farmers.
"""

import os

from dotenv import load_dotenv
from google import genai


# ---------------------------------------------------------
# LOAD ENVIRONMENT VARIABLES
# ---------------------------------------------------------

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

load_dotenv(
    os.path.join(BASE_DIR, ".env")
)


# ---------------------------------------------------------
# GEMINI CLIENT
# ---------------------------------------------------------

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is not configured in .env"
    )

client = genai.Client(
    api_key=GEMINI_API_KEY
)


# ---------------------------------------------------------
# PALM MITRA SYSTEM INSTRUCTIONS
# ---------------------------------------------------------

SYSTEM_INSTRUCTION = """
You are Palm Mitra, an AI assistant for oil-palm farmers.

Your role is to provide practical, clear and safe guidance
about oil-palm cultivation.

You can help with:
- irrigation
- drainage
- soil testing
- nutrient management
- pest and disease monitoring
- leaf symptoms
- farm activities
- plantation management
- general oil-palm cultivation questions
- interpreting Palm Mitra analysis results

Important safety rules:

1. Do not claim that an AI prediction is a confirmed
   agricultural diagnosis.

2. Do not prescribe exact fertilizer or pesticide doses
   without sufficient field and soil information.

3. Encourage soil testing and expert/field verification
   when appropriate.

4. If a farmer describes serious or persistent symptoms,
   recommend consulting an agricultural expert.

5. Give practical steps in simple language.

6. Do not invent farm data, weather information or
   analysis results.

7. If information is missing, clearly say what information
   would help.

8. Keep answers focused and farmer-friendly.

The user may later select English, Telugu or Hindi.
For now, respond in English unless another language is
explicitly requested.
"""


# ---------------------------------------------------------
# CHAT FUNCTION
# ---------------------------------------------------------

def ask_palm_mitra(
    message: str,
    farm_context: dict | None = None,
    weather_context: dict | None = None,
    leaf_context: dict | None = None
) -> str:

    if not message or not message.strip():
        return "Please enter a question."

    context_parts = []


    # -----------------------------------------------------
    # FARM CONTEXT
    # -----------------------------------------------------

    if farm_context:

        context_parts.append(
            f"""
Farm information:
{farm_context}
"""
        )


    # -----------------------------------------------------
    # WEATHER CONTEXT
    # -----------------------------------------------------

    if weather_context:

        context_parts.append(
            f"""
Current weather information:
{weather_context}
"""
        )


    # -----------------------------------------------------
    # LEAF ANALYSIS CONTEXT
    # -----------------------------------------------------

    if leaf_context:

        context_parts.append(
            f"""
Latest Palm Mitra leaf analysis:
{leaf_context}
"""
        )


    context = "\n".join(context_parts)


    # -----------------------------------------------------
    # FINAL PROMPT
    # -----------------------------------------------------

    prompt = f"""
{SYSTEM_INSTRUCTION}

{context}

Farmer's question:
{message}

Provide a clear and practical answer.
"""


    # -----------------------------------------------------
    # GEMINI REQUEST
    # -----------------------------------------------------

    try:

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        if response.text:
            return response.text.strip()

        return (
            "I couldn't generate a response right now. "
            "Please try again."
        )

    except Exception as error:

        print(
            "Palm Mitra AI Assistant error:",
            error
        )

        return (
            "The AI Assistant is temporarily unavailable. "
            "Please try again."
        )