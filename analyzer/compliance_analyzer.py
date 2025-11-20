"""
Retail Compliance Analyzer

Core module for analyzing retail store images and generating compliance reports.
"""

import base64
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import uuid

import anthropic
from dotenv import load_dotenv
from PIL import Image

# Load environment variables
load_dotenv()


class RetailComplianceAnalyzer:
    """
    Analyzes retail store images for compliance auditing.

    Uses Claude's vision capabilities to extract structured data about products,
    their conditions, expiration dates, and compliance violations.
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

    def _create_analysis_prompt(self) -> str:
        """
        Create the system prompt for Claude vision analysis.

        Returns:
            Formatted prompt string
        """
        return """You are a retail store compliance auditor AI. Your job is to analyze store images and extract structured data for compliance reporting.

CRITICAL RULES:
- Only report what you can SEE in the image. Never assume or infer.
- If text/dates are partially visible or unclear, mark as "unclear" not guessed.
- Confidence score: 0.0-1.0 based on image clarity and certainty.
- Return ONLY valid JSON. No explanations outside JSON.
- Use null for fields you cannot determine.

CONTEXT:
- Store format: Retail/grocery store
- Purpose: Compliance auditing and waste tracking
- Data feeds into operations dashboards

ANALYSIS REQUIREMENTS:
For each product visible in the image, extract:
1. Product identification: name, brand, category
2. Dates: expiration_date, manufacture_date, best_before_date (format: YYYY-MM-DD or "unclear")
3. Condition: status (good/damaged/expired/near_expiry/unclear), damage types
4. Location: shelf level, section, position
5. Compliance: violations with type and severity
6. Confidence scores: overall and per-field

OUTPUT FORMAT:
Return a JSON object with this structure:
{
  "report_id": "generated_uuid",
  "timestamp": "ISO 8601 timestamp",
  "analysis_status": "success|partial|failed",
  "products": [
    {
      "product_id": "prod_001",
      "name": "Product Name or null",
      "brand": "Brand Name or null",
      "category": "Category or null",
      "quantity": 1,
      "unit_size": "Size or null",
      "location": {
        "shelf_level": "top|middle|bottom or null",
        "section": "Section name or null",
        "position": "Additional position or null"
      },
      "dates": {
        "expiration_date": "YYYY-MM-DD or unclear or null",
        "manufacture_date": "YYYY-MM-DD or unclear or null",
        "best_before_date": "YYYY-MM-DD or unclear or null",
        "date_visibility": "clear|partial|unclear|not_visible"
      },
      "condition": {
        "status": "good|damaged|expired|near_expiry|unclear",
        "damage_type": ["dented", "torn", ...] or null,
        "notes": "Additional observations or null"
      },
      "compliance": {
        "is_compliant": true|false|null,
        "violations": [
          {
            "type": "expired|damaged|mislabeled|improper_storage|missing_label|other",
            "severity": "critical|high|medium|low",
            "description": "Description of violation"
          }
        ]
      },
      "pricing": {
        "price": "Price string or null",
        "currency": "USD|EUR|etc or null",
        "has_price_tag": true|false|null
      },
      "confidence": 0.0-1.0,
      "field_confidence": {
        "name": 0.0-1.0 or null,
        "brand": 0.0-1.0 or null,
        "expiration_date": 0.0-1.0 or null,
        "condition": 0.0-1.0 or null
      }
    }
  ],
  "overall_compliance": {
    "status": "pass|fail|warning|unclear",
    "total_products": 0,
    "compliant_count": 0,
    "violation_count": 0,
    "critical_violations": ["List of critical issues"],
    "summary": "Brief summary of findings"
  },
  "notes": "Additional observations or null"
}

IMPORTANT: Respond ONLY with valid JSON. No markdown, no explanations, just JSON."""

    def analyze_image(self, image_path: str) -> Dict[str, Any]:
        """
        Analyze a retail store image for compliance.

        Args:
            image_path: Path to the image file

        Returns:
            Dictionary containing structured compliance report

        Raises:
            FileNotFoundError: If image file doesn't exist
            ValueError: If API key is not set
            Exception: For API or processing errors
        """
        # Encode image
        image_data, media_type = self._encode_image(image_path)

        # Get image metadata
        image_metadata = self._get_image_metadata(image_path)

        # Create message with vision
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
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
                                "text": self._create_analysis_prompt()
                            }
                        ],
                    }
                ],
            )

            # Extract JSON from response
            response_text = message.content[0].text

            # Try to parse as JSON
            try:
                # Remove any markdown formatting if present
                if "```json" in response_text:
                    response_text = response_text.split("```json")[1].split("```")[0]
                elif "```" in response_text:
                    response_text = response_text.split("```")[1].split("```")[0]

                result = json.loads(response_text.strip())

                # Add image metadata
                result["image_metadata"] = image_metadata

                # Ensure required fields
                if "report_id" not in result:
                    result["report_id"] = str(uuid.uuid4())
                if "timestamp" not in result:
                    result["timestamp"] = datetime.utcnow().isoformat() + "Z"

                return result

            except json.JSONDecodeError as e:
                # If JSON parsing fails, return error structure
                return {
                    "report_id": str(uuid.uuid4()),
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "image_metadata": image_metadata,
                    "analysis_status": "failed",
                    "products": [],
                    "overall_compliance": {
                        "status": "unclear",
                        "total_products": 0,
                        "compliant_count": 0,
                        "violation_count": 0,
                        "critical_violations": [],
                        "summary": f"Failed to parse analysis results: {str(e)}"
                    },
                    "notes": f"Error: {response_text[:500]}"
                }

        except Exception as e:
            # Return error structure
            return {
                "report_id": str(uuid.uuid4()),
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "image_metadata": image_metadata,
                "analysis_status": "failed",
                "products": [],
                "overall_compliance": {
                    "status": "unclear",
                    "total_products": 0,
                    "compliant_count": 0,
                    "violation_count": 0,
                    "critical_violations": [],
                    "summary": f"Analysis failed: {str(e)}"
                },
                "notes": f"Error during API call: {str(e)}"
            }

    def analyze_and_save(
        self,
        image_path: str,
        output_path: str,
        pretty: bool = True
    ) -> Dict[str, Any]:
        """
        Analyze image and save result to JSON file.

        Args:
            image_path: Path to input image
            output_path: Path to output JSON file
            pretty: Whether to pretty-print JSON (default: True)

        Returns:
            Analysis result dictionary
        """
        result = self.analyze_image(image_path)

        with open(output_path, "w") as f:
            if pretty:
                json.dump(result, f, indent=2)
            else:
                json.dump(result, f)

        return result
