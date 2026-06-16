"""
=========================================================
Project : AI Powered Vehicle Valuation System
Module  : AWS Bedrock Vision (Nova Lite)
=========================================================
"""

import base64
import json
import os
from pathlib import Path

import boto3
from PIL import Image

from backend.app.config import (
    AWS_ACCESS_KEY_ID,
    AWS_REGION,
    AWS_SECRET_ACCESS_KEY,
    BEDROCK_MODEL_ID,
)


def get_bedrock_client():
    """Initialize Bedrock Runtime client."""
    return boto3.client(
        service_name="bedrock-runtime",
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )


def encode_image_to_base64(image: Image.Image) -> str:
    """Convert PIL Image to base64 string."""
    import io
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def analyze_vehicle_image_with_bedrock(image: Image.Image) -> dict:
    """
    Analyze vehicle image using AWS Bedrock Nova Lite.
    Returns detected brand name and other vehicle details.
    """
    client = get_bedrock_client()
    
    # Encode image
    image_base64 = encode_image_to_base64(image)
    
    # Prepare prompt for Nova Lite
    prompt = """Identify the car brand in this image. 
Return ONLY valid JSON in this exact format:
{
  "detected_brand": "Brand Name",
  "detected_model": "Model Name",
  "detected_body_type": "Body Type",
  "detected_color": "Color",
  "confidence": 0-100
}

Important: For brand name, use only the manufacturer name (e.g., "Maruti" not "Maruti Swift", "Honda" not "Honda City").
If unsure, provide best estimate. Focus on detecting the brand accurately."""

    # Prepare request payload for Nova Lite
    request_body = {
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "image": {
                            "format": "jpeg",
                            "source": {
                                "bytes": image_base64
                            }
                        }
                    },
                    {
                        "text": prompt
                    }
                ]
            }
        ],
        "inferenceConfig": {
            "max_new_tokens": 500,
            "temperature": 0.3,
            "top_p": 0.9
        }
    }
    
    try:
        # Invoke Bedrock model
        response = client.invoke_model(
            modelId=BEDROCK_MODEL_ID,
            body=json.dumps(request_body),
            contentType="application/json",
            accept="application/json"
        )
        
        # Parse response
        response_body = json.loads(response["body"].read())
        
        # Extract text from Nova Lite response
        output_text = response_body.get("output", {}).get("message", {}).get("content", [{}])[0].get("text", "{}")
        
        # Clean and parse JSON
        output_text = output_text.strip()
        if "```json" in output_text:
            output_text = output_text.split("```json")[1].split("```")[0].strip()
        elif "```" in output_text:
            output_text = output_text.split("```")[1].split("```")[0].strip()
        
        result = json.loads(output_text)
        
        # Clean brand name (remove model if included)
        brand = result.get("detected_brand", "")
        if brand:
            # Extract first word as brand (e.g., "Maruti Swift" → "Maruti")
            brand = brand.split()[0] if " " in brand else brand
        
        return {
            "detected_brand": brand,
            "detected_model": result.get("detected_model"),
            "detected_body_type": result.get("detected_body_type"),
            "detected_color": result.get("detected_color"),
            "confidence": result.get("confidence", 0),
        }
        
    except Exception as e:
        print(f"Bedrock analysis error: {e}")
        return {
            "detected_brand": None,
            "detected_model": None,
            "detected_body_type": None,
            "detected_color": None,
            "confidence": 0,
        }


def detect_vehicle_damage_with_bedrock(image: Image.Image) -> dict:
    """
    Detect vehicle damage using AWS Bedrock Nova Lite.
    Returns damage assessment and description.
    """
    client = get_bedrock_client()
    image_base64 = encode_image_to_base64(image)
    
    prompt = """Analyze this vehicle image for any visible damage or defects.
Return ONLY valid JSON in this exact format:
{
  "has_damage": true/false,
  "damage_severity": "none/minor/medium/major",
  "damage_description": "Detailed description of visible damage",
  "damage_areas": ["area1", "area2"],
  "confidence": 0-100
}

Damage severity guidelines:
- none: No visible damage, car looks pristine
- minor: Small scratches, paint chips, minor dents
- medium: Broken parts, cracked glass, visible collision damage, multiple dents
- major: Severe structural damage, major accident damage, frame damage, flood damage

Be thorough and accurate. If no damage is visible, set has_damage to false and damage_description to "No visible damage detected"."""

    request_body = {
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "image": {
                            "format": "jpeg",
                            "source": {
                                "bytes": image_base64
                            }
                        }
                    },
                    {
                        "text": prompt
                    }
                ]
            }
        ],
        "inferenceConfig": {
            "max_new_tokens": 500,
            "temperature": 0.3,
            "top_p": 0.9
        }
    }
    
    try:
        response = client.invoke_model(
            modelId=BEDROCK_MODEL_ID,
            body=json.dumps(request_body),
            contentType="application/json",
            accept="application/json"
        )
        
        response_body = json.loads(response["body"].read())
        output_text = response_body.get("output", {}).get("message", {}).get("content", [{}])[0].get("text", "{}")
        
        # Clean JSON
        output_text = output_text.strip()
        if "```json" in output_text:
            output_text = output_text.split("```json")[1].split("```")[0].strip()
        elif "```" in output_text:
            output_text = output_text.split("```")[1].split("```")[0].strip()
        
        result = json.loads(output_text)
        
        return {
            "has_damage": result.get("has_damage", False),
            "damage_severity": result.get("damage_severity", "none"),
            "damage_description": result.get("damage_description", "No visible damage detected"),
            "damage_areas": result.get("damage_areas", []),
            "confidence": result.get("confidence", 0),
        }
        
    except Exception as e:
        print(f"Damage detection error: {e}")
        return {
            "has_damage": False,
            "damage_severity": "none",
            "damage_description": "Unable to analyze damage",
            "damage_areas": [],
            "confidence": 0,
        }
