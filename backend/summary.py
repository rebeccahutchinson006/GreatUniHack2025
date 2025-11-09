import json
import re
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# === CONFIGURATION ===
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
MODEL = "gemini-2.5-flash"  # Fast and efficient model - alternatives: gemini-flash-latest, gemini-2.5-pro
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={GEMINI_API_KEY}"


# === FUNCTION TO LIST AVAILABLE MODELS ===
def list_available_models():
    """
    List all available models for the given API key.
    Useful for debugging and finding the correct model name.
    """
    list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={GEMINI_API_KEY}"
    try:
        response = requests.get(list_url, timeout=10)
        if response.status_code == 200:
            print(response)
            models_data = response.json()
            if "models" in models_data:
                print("Available models:")
                for model in models_data["models"]:
                    name = model.get("name", "Unknown")
                    # Extract just the model name from full path
                    model_name = name.split("/")[-1] if "/" in name else name
                    print(f"  - {model_name}")
                return [model.get("name", "").split("/")[-1] for model in models_data["models"]]
        else:
            print(f"Error listing models: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {str(e)}")
    return []


# === PROMPT TEMPLATE ===
PROMPT_TEMPLATE = """
Given the lyrics, return a JSON with two fields: 'summary' and 'insights'.

- 'summary': A short English summary of the song.
- 'insights': A list of short, concise bullet points. Each bullet point MUST explain a specific idiom, pun, joke, euphemism, or clever wordplay that is deeply tied to the original language.

**IMPORTANT RULES for 'insights'**:
1.  Focus on the non-obvious: Only include insights that a learner couldn't guess from a direct translation.
2.  AVOID universal metaphors: Do not include common metaphors like calling someone 'sunshine' for happiness. These are not language-specific.
3.  If no unique linguistic devices are found, return an empty list for 'insights'.

Lyrics:
{lyrics}
"""

# === FUNCTION TO CALL GOOGLE AI STUDIO ===
def analyze_lyrics(lyrics: str):
    """
    Analyze song lyrics using Google AI Studio API.
    
    Args:
        lyrics: The song lyrics to analyze
        
    Returns:
        dict: A dictionary with 'summary' and 'insights' keys
        
    Raises:
        Exception: If the API call fails or returns an error
    """
    if not lyrics or not lyrics.strip():
        raise ValueError("Lyrics cannot be empty")
    
    headers = {"Content-Type": "application/json"}
    prompt = PROMPT_TEMPLATE.format(lyrics=lyrics)
    payload = {
        "contents": [
            {"role": "user", "parts": [{"text": prompt}]}
        ]
    }

    try:
        response = requests.post(API_URL, headers=headers, data=json.dumps(payload), timeout=30)
    except requests.exceptions.RequestException as e:
        raise Exception(f"Network error: {str(e)}")

    if response.status_code != 200:
        error_msg = f"API error: {response.status_code}, {response.text}"
        if response.status_code == 404:
            error_msg += f"\n\nThe model '{MODEL}' was not found. This could mean:"
            error_msg += "\n  1. The model name is incorrect for your API key"
            error_msg += "\n  2. Your API key doesn't have access to this model"
            error_msg += "\n  3. The API key is invalid or expired"
            error_msg += f"\n\nTry running: list_available_models() to see available models"
        raise Exception(error_msg)

    try:
        result = response.json()
    except json.JSONDecodeError:
        raise Exception(f"Invalid JSON response from API: {response.text}")

    # Extract the model's text output
    try:
        output = result["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        raise Exception("Unexpected response format", result)

    # Try to parse JSON (handle markdown code blocks if present)
    try:
        # First try direct parsing
        return json.loads(output)
    except json.JSONDecodeError:
        # Try to extract JSON from markdown code blocks
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', output, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
        
        # If still failing, try to find JSON object in the output
        json_match = re.search(r'\{.*\}', output, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass
        
        return {"raw_output": output, "error": "Could not parse JSON from model response"}
