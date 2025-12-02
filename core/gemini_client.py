"""Thin wrapper around the official Gemini Python client."""

from __future__ import annotations

import json
from typing import Any, Dict

import google.generativeai as genai

from core.config import get_settings


_settings = get_settings()

if not _settings.google_api_key:
    raise RuntimeError("GOOGLE_API_KEY missing for Gemini client")

genai.configure(api_key=_settings.google_api_key)

# Free-tier models only (avoid experimental models like gemini-2.5-pro-exp)
# Order: flash (faster, cheaper) -> pro (more capable)
FREE_TIER_MODELS = [
    "gemini-1.5-flash",
    "gemini-1.5-flash-latest", 
    "gemini-1.5-pro",
    "gemini-1.5-pro-latest",
    "gemini-pro",
]

# Try to find a free-tier model
_available_model = None
try:
    available_models = {}
    for m in genai.list_models():
        if "generateContent" in m.supported_generation_methods:
            model_name = m.name.split("/")[-1]
            # Skip experimental models (they're not on free tier)
            if "-exp" not in model_name and "2.5" not in model_name:
                available_models[model_name] = m.name
    
    # Try free-tier models first
    for preferred in FREE_TIER_MODELS:
        if preferred in available_models:
            _available_model = preferred
            break
    
    # If no preferred model found, use first non-experimental available
    if not _available_model and available_models:
        _available_model = list(available_models.keys())[0]
except Exception:
    pass

# Fallback to a known free-tier model
DEFAULT_MODEL = _available_model or "gemini-1.5-flash"


def generate_json(prompt: str, model: str | None = None) -> Dict[str, Any]:
    """Call Gemini with a prompt and try to parse JSON from the response text.
    
    Only uses free-tier models. Experimental models (with -exp or 2.5) are rejected.
    """
    
    # Always use free-tier model - reject experimental models even if passed
    if model:
        model_clean = model.replace("models/", "").lower()
        # Reject experimental models
        if "-exp" in model_clean or "2.5" in model_clean:
            raise ValueError(
                f"Experimental model '{model}' is not available on free tier. "
                f"Using free-tier model '{DEFAULT_MODEL}' instead."
            )
        # Only allow known free-tier models
        if model_clean not in [m.lower() for m in FREE_TIER_MODELS]:
            # If not in our list, use default to be safe
            model_name = DEFAULT_MODEL
        else:
            model_name = model_clean
    else:
        model_name = DEFAULT_MODEL
    
    # Ensure model name has 'models/' prefix if not present
    if not model_name.startswith("models/"):
        model_name = f"models/{model_name}"
    
    try:
        gm = genai.GenerativeModel(model_name)
        response = gm.generate_content(prompt)
        text = getattr(response, "text", None) or ""

        try:
            return json.loads(text)
        except Exception:
            # Fall back to returning raw text so the UI can still show something.
            return {"raw": text, "parse_error": "Response was not valid JSON"}
    except Exception as e:
        error_msg = str(e)
        if "quota" in error_msg.lower() or "429" in error_msg or "ResourceExhausted" in error_msg:
            raise RuntimeError(
                f"Google API quota exceeded for model {model_name}. "
                f"Please check your quota at https://ai.dev/usage?tab=rate-limit "
                f"or wait for quota reset. Error: {error_msg[:200]}"
            ) from e
        raise


