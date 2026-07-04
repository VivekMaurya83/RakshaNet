import os
import google.generativeai as genai
from fastapi import HTTPException

def configure_gemini():
    """Configures the Gemini SDK client."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Missing GEMINI_API_KEY environment variable.")
    genai.configure(api_key=api_key)

async def generate_structured_json(
    prompt: str,
    system_instruction: str,
    model_name: str = "gemini-1.5-flash"
) -> str:
    """
    Sends request to Gemini model requesting JSON response.
    """
    try:
        configure_gemini()
        model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=system_instruction
        )
        # Requesting a json output format
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        return response.text
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Gemini API failure: {str(e)}"
        )
