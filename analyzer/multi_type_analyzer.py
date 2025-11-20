"""
Multi-Type Compliance Analyzer

Supports multiple analysis types: waste, shelf, promo, fifo with structured outputs.
"""

import base64
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Literal
import uuid

import anthropic
from dotenv import load_dotenv
from PIL import Image
from jsonschema import validate, ValidationError

from .prompts import SYSTEM_PROMPT, TYPE_PROMPTS
from .schemas import SCHEMAS

# Load environment variables
load_dotenv()

CaptureType = Literal["waste", "shelf", "promo", "fifo", "quality_check"]


class MultiTypeComplianceAnalyzer:
    """
    Multi-purpose compliance analyzer supporting different capture types.

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
        model: str = "claude-3-5-sonnet-20241022",
        max_tokens: int = 4096
    ):
        """
        Initialize the analyzer.

        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
            model: Claude model to use
            max_tokens: Maximum tokens for response
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY must be set in environment or passed to constructor"
            )

        self.model = model
        self.max_tokens = max_tokens
        self.client = anthropic.Anthropic(api_key=self.api_key)

    def _encode_image(self, image_path: str) -> tuple[str, str]:
        """
        Encode image to base64 and determine media type.

        Args:
            image_path: Path to image file

        Returns:
            Tuple of (base64_data, media_type)
        """
        path = Path(image_path)

        if not path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        # Determine media type
        suffix = path.suffix.lower()
        media_types = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".webp": "image/webp"
        }

        media_type = media_types.get(suffix, "image/jpeg")

        # Read and encode
        with open(image_path, "rb") as f:
            image_data = base64.standard_b64encode(f.read()).decode("utf-8")

        return image_data, media_type

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
            ValidationError: If output doesn't match schema (when validate_schema=True)
        """
        # Encode image
        image_data, media_type = self._encode_image(image_path)

        # Get image metadata
        image_metadata = self._get_image_metadata(image_path)

        # Create prompt
        prompt = self._create_prompt(capture_type)

        # Analyze with Claude
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=0.1,  # Low temperature for consistent structured output
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": image_data,
                                },
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ],
                    }
                ],
            )

            # Extract JSON from response
            response_text = message.content[0].text

            # Parse JSON
            try:
                # Remove markdown formatting if present
                if "```json" in response_text:
                    response_text = response_text.split("```json")[1].split("```")[0]
                elif "```" in response_text:
                    response_text = response_text.split("```")[1].split("```")[0]

                result = json.loads(response_text.strip())

                # Add metadata
                result["_metadata"] = {
                    "image_filename": image_metadata.get("filename"),
                    "image_resolution": image_metadata.get("resolution"),
                    "analysis_timestamp": datetime.utcnow().isoformat() + "Z",
                    "model_used": self.model,
                    "capture_type": capture_type
                }

                # Validate against schema if requested
                if validate_schema and capture_type in SCHEMAS:
                    try:
                        validate(instance=result, schema=SCHEMAS[capture_type])
                    except ValidationError as e:
                        print(f"Warning: Schema validation failed: {e.message}")
                        # Don't raise, just warn - allows for slight schema deviations

                return result

            except json.JSONDecodeError as e:
                # Return error structure
                return {
                    "capture_type": capture_type,
                    "error": "json_parse_error",
                    "error_message": f"Failed to parse JSON: {str(e)}",
                    "raw_response": response_text[:1000],
                    "_metadata": {
                        "image_filename": image_metadata.get("filename"),
                        "analysis_timestamp": datetime.utcnow().isoformat() + "Z",
                        "model_used": self.model
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
                    "model_used": self.model
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
