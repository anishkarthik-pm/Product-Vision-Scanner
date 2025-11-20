"""
Gemini-Based Compliance Analyzer

Multi-type compliance analyzer using Google's Gemini API with structured outputs.
"""

import base64
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Literal

import google.generativeai as genai
from dotenv import load_dotenv
from PIL import Image
from jsonschema import validate, ValidationError

from .prompts import SYSTEM_PROMPT, TYPE_PROMPTS
from .schemas import SCHEMAS

# Load environment variables
load_dotenv()

CaptureType = Literal["waste", "shelf", "promo", "fifo", "quality_check"]


class GeminiComplianceAnalyzer:
    """
    Multi-purpose compliance analyzer using Gemini with structured outputs.

    Supports:
    - waste: Waste/disposal/shrinkage analysis
    - shelf: On-Shelf Availability (OSA) and shelf compliance
    - promo: Promotional display compliance
    - fifo: FIFO (First In, First Out) compliance checking
    - quality_check: Image quality pre-assessment
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gemini-1.5-flash",
        max_tokens: int = 4096,
        temperature: float = 0.1
    ):
        """
        Initialize the analyzer.

        Args:
            api_key: Google API key (defaults to GEMINI_API_KEY or GOOGLE_API_KEY env var)
            model: Gemini model to use (gemini-1.5-flash or gemini-1.5-pro)
            max_tokens: Maximum tokens for response
            temperature: Temperature for generation (0.0-1.0, lower is more deterministic)
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY or GOOGLE_API_KEY must be set in environment or passed to constructor"
            )

        self.model_name = model
        self.max_tokens = max_tokens
        self.temperature = temperature

        # Configure Gemini
        genai.configure(api_key=self.api_key)

    def _get_image_metadata(self, image_path: str) -> Dict[str, Any]:
        """
        Extract basic image metadata.

        Args:
            image_path: Path to image file

        Returns:
            Dictionary with image metadata
        """
        try:
            with Image.open(image_path) as img:
                width, height = img.size
                format_name = img.format

            return {
                "filename": Path(image_path).name,
                "resolution": f"{width}x{height}",
                "format": format_name,
                "quality_score": 1.0 if width >= 1024 else 0.7
            }
        except Exception:
            return {
                "filename": Path(image_path).name,
                "resolution": None,
                "quality_score": 0.5
            }

    def _create_prompt(self, capture_type: CaptureType) -> str:
        """
        Create the analysis prompt for the specified capture type.

        Args:
            capture_type: Type of analysis to perform

        Returns:
            Combined system prompt and type-specific prompt
        """
        if capture_type not in TYPE_PROMPTS:
            raise ValueError(f"Invalid capture_type: {capture_type}. Must be one of: {list(TYPE_PROMPTS.keys())}")

        return f"{SYSTEM_PROMPT}\n\n{TYPE_PROMPTS[capture_type]}"

    def _convert_schema_for_gemini(self, schema: dict) -> dict:
        """
        Convert JSON schema to Gemini's schema format.

        Gemini uses a slightly different schema format than standard JSON Schema.
        """
        # Gemini schemas don't use $schema, title, description at root level
        gemini_schema = {}

        if "type" in schema:
            gemini_schema["type"] = schema["type"]

        if "properties" in schema:
            gemini_schema["properties"] = {}
            for prop_name, prop_def in schema["properties"].items():
                gemini_schema["properties"][prop_name] = self._convert_property(prop_def)

        if "required" in schema:
            gemini_schema["required"] = schema["required"]

        if "items" in schema:
            gemini_schema["items"] = self._convert_property(schema["items"])

        return gemini_schema

    def _convert_property(self, prop: dict) -> dict:
        """Convert a property definition to Gemini format."""
        converted = {}

        # Handle type
        if "type" in prop:
            prop_type = prop["type"]
            # Handle nullable types like ["string", "null"]
            if isinstance(prop_type, list):
                # Gemini doesn't support union types the same way
                # Use the non-null type
                non_null = [t for t in prop_type if t != "null"]
                if non_null:
                    converted["type"] = non_null[0]
                    converted["nullable"] = True
            else:
                converted["type"] = prop_type

        # Handle nested properties
        if "properties" in prop:
            converted["properties"] = {}
            for nested_name, nested_def in prop["properties"].items():
                converted["properties"][nested_name] = self._convert_property(nested_def)

        # Handle arrays
        if "items" in prop:
            converted["items"] = self._convert_property(prop["items"])

        # Handle enums
        if "enum" in prop:
            converted["enum"] = prop["enum"]

        # Handle required fields
        if "required" in prop:
            converted["required"] = prop["required"]

        # Handle constraints
        for constraint in ["minimum", "maximum", "minLength", "maxLength"]:
            if constraint in prop:
                converted[constraint] = prop[constraint]

        return converted

    def analyze_image(
        self,
        image_path: str,
        capture_type: CaptureType = "waste",
        validate_schema: bool = True
    ) -> Dict[str, Any]:
        """
        Analyze an image for compliance based on capture type.

        Args:
            image_path: Path to the image file
            capture_type: Type of analysis ("waste", "shelf", "promo", "fifo", "quality_check")
            validate_schema: Whether to validate output against schema

        Returns:
            Dictionary containing structured compliance analysis

        Raises:
            FileNotFoundError: If image file doesn't exist
            ValueError: If API key is not set or invalid capture_type
        """
        # Check file exists
        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        # Get image metadata
        image_metadata = self._get_image_metadata(image_path)

        # Create prompt
        prompt = self._create_prompt(capture_type)

        # Load image
        image = Image.open(image_path)

        try:
            # Create model with system instruction
            model = genai.GenerativeModel(
                model_name=self.model_name,
                system_instruction=SYSTEM_PROMPT
            )

            # Get schema for this capture type
            schema = SCHEMAS.get(capture_type)

            # Configure generation with JSON mode and schema
            generation_config = genai.GenerationConfig(
                response_mime_type="application/json",
                temperature=self.temperature,
                max_output_tokens=self.max_tokens
            )

            # Add schema if available
            if schema:
                # Convert schema to Gemini format
                gemini_schema = self._convert_schema_for_gemini(schema)
                generation_config.response_schema = gemini_schema

            # Generate response
            response = model.generate_content(
                [image, TYPE_PROMPTS[capture_type]],
                generation_config=generation_config
            )

            # Parse JSON response
            result = json.loads(response.text)

            # Add metadata
            result["_metadata"] = {
                "image_filename": image_metadata.get("filename"),
                "image_resolution": image_metadata.get("resolution"),
                "analysis_timestamp": datetime.utcnow().isoformat() + "Z",
                "model_used": self.model_name,
                "capture_type": capture_type
            }

            # Validate against schema if requested
            if validate_schema and schema:
                try:
                    validate(instance=result, schema=schema)
                except ValidationError as e:
                    print(f"Warning: Schema validation failed: {e.message}")
                    # Don't raise, just warn

            return result

        except json.JSONDecodeError as e:
            # Return error structure
            return {
                "capture_type": capture_type,
                "error": "json_parse_error",
                "error_message": f"Failed to parse JSON: {str(e)}",
                "raw_response": str(response.text)[:1000] if 'response' in locals() else "No response",
                "_metadata": {
                    "image_filename": image_metadata.get("filename"),
                    "analysis_timestamp": datetime.utcnow().isoformat() + "Z",
                    "model_used": self.model_name
                }
            }

        except Exception as e:
            # Return error structure
            return {
                "capture_type": capture_type,
                "error": "analysis_error",
                "error_message": str(e),
                "_metadata": {
                    "image_filename": image_metadata.get("filename"),
                    "analysis_timestamp": datetime.utcnow().isoformat() + "Z",
                    "model_used": self.model_name
                }
            }

    def quality_check(self, image_path: str) -> Dict[str, Any]:
        """
        Perform a quality check on an image before full analysis.

        Args:
            image_path: Path to image file

        Returns:
            Quality check result with suitability assessment
        """
        return self.analyze_image(image_path, capture_type="quality_check")

    def analyze_waste(self, image_path: str) -> Dict[str, Any]:
        """Convenience method for waste/disposal analysis."""
        return self.analyze_image(image_path, capture_type="waste")

    def analyze_shelf(self, image_path: str) -> Dict[str, Any]:
        """Convenience method for shelf/OSA analysis."""
        return self.analyze_image(image_path, capture_type="shelf")

    def analyze_promo(self, image_path: str) -> Dict[str, Any]:
        """Convenience method for promotional compliance analysis."""
        return self.analyze_image(image_path, capture_type="promo")

    def analyze_fifo(self, image_path: str) -> Dict[str, Any]:
        """Convenience method for FIFO compliance analysis."""
        return self.analyze_image(image_path, capture_type="fifo")

    def analyze_and_save(
        self,
        image_path: str,
        capture_type: CaptureType,
        output_path: str,
        pretty: bool = True
    ) -> Dict[str, Any]:
        """
        Analyze image and save result to JSON file.

        Args:
            image_path: Path to input image
            capture_type: Type of analysis to perform
            output_path: Path to output JSON file
            pretty: Whether to pretty-print JSON (default: True)

        Returns:
            Analysis result dictionary
        """
        result = self.analyze_image(image_path, capture_type=capture_type)

        with open(output_path, "w") as f:
            if pretty:
                json.dump(result, f, indent=2)
            else:
                json.dump(result, f)

        return result
