"""
JSON Schema definitions for different capture types.

Defines structured output schemas for waste, shelf, promo, and FIFO analysis.
"""

# Waste/Disposal Analysis Schema
WASTE_SCHEMA = {
    "type": "object",
    "required": ["capture_type", "products", "waste_reason", "estimated_total_items", "image_quality", "confidence"],
    "properties": {
        "capture_type": {
            "type": "string",
            "enum": ["waste"]
        },
        "products": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["product_name", "quantity", "unit", "condition", "damage_details"],
                "properties": {
                    "product_name": {"type": "string"},
                    "brand": {"type": ["string", "null"]},
                    "sku": {"type": ["string", "null"]},
                    "quantity": {"type": ["number", "string"]},
                    "unit": {"type": "string"},
                    "expiry_date": {"type": ["string", "null"]},
                    "batch_code": {"type": ["string", "null"]},
                    "mrp": {"type": ["number", "null"]},
                    "condition": {
                        "type": "string",
                        "enum": ["expired", "damaged", "spoiled", "packaging_torn", "contaminated", "recall"]
                    },
                    "damage_details": {"type": "string"}
                }
            }
        },
        "waste_reason": {"type": "string"},
        "estimated_total_items": {"type": "number"},
        "image_quality": {
            "type": "string",
            "enum": ["clear", "partial", "poor"]
        },
        "confidence": {
            "type": "number",
            "minimum": 0.0,
            "maximum": 1.0
        },
        "notes": {"type": ["string", "null"]}
    }
}

# Shelf Compliance/OSA Analysis Schema
SHELF_SCHEMA = {
    "type": "object",
    "required": ["capture_type", "shelf_overview", "products", "issues", "compliance_status", "confidence"],
    "properties": {
        "capture_type": {
            "type": "string",
            "enum": ["shelf"]
        },
        "shelf_overview": {
            "type": "object",
            "required": ["total_facings", "empty_facings", "osa_percentage", "shelf_level"],
            "properties": {
                "total_facings": {"type": "number"},
                "stocked_facings": {"type": "number"},
                "empty_facings": {"type": "number"},
                "osa_percentage": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 100
                },
                "shelf_level": {"type": ["string", "null"]},
                "category": {"type": ["string", "null"]}
            }
        },
        "products": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "product_name": {"type": "string"},
                    "brand": {"type": ["string", "null"]},
                    "facings": {"type": "number"},
                    "stock_level": {
                        "type": "string",
                        "enum": ["full", "adequate", "low", "out_of_stock"]
                    },
                    "price_visible": {"type": "boolean"},
                    "planogram_compliant": {"type": ["boolean", "null"]}
                }
            }
        },
        "issues": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["issue_type", "severity"],
                "properties": {
                    "issue_type": {
                        "type": "string",
                        "enum": ["out_of_stock", "low_stock", "misplaced", "damaged_product",
                                "missing_price", "poor_facing", "expired_visible", "other"]
                    },
                    "product_name": {"type": ["string", "null"]},
                    "location": {"type": ["string", "null"]},
                    "severity": {
                        "type": "string",
                        "enum": ["critical", "high", "medium", "low"]
                    },
                    "description": {"type": "string"}
                }
            }
        },
        "compliance_status": {
            "type": "string",
            "enum": ["compliant", "issues_found", "critical_issues", "unclear"]
        },
        "image_quality": {
            "type": "string",
            "enum": ["clear", "partial", "poor"]
        },
        "confidence": {
            "type": "number",
            "minimum": 0.0,
            "maximum": 1.0
        },
        "notes": {"type": ["string", "null"]}
    }
}

# Promotional Compliance Schema
PROMO_SCHEMA = {
    "type": "object",
    "required": ["capture_type", "promo_details", "compliance_status", "confidence"],
    "properties": {
        "capture_type": {
            "type": "string",
            "enum": ["promo"]
        },
        "promo_details": {
            "type": "object",
            "required": ["promo_type", "products_on_promo", "display_quality"],
            "properties": {
                "promo_type": {
                    "type": "string",
                    "enum": ["endcap", "display_stand", "shelf_signage", "bundle", "price_reduction", "other"]
                },
                "promo_title": {"type": ["string", "null"]},
                "products_on_promo": {"type": "number"},
                "display_quality": {
                    "type": "string",
                    "enum": ["excellent", "good", "poor", "damaged"]
                },
                "signage_visible": {"type": "boolean"},
                "price_visible": {"type": "boolean"},
                "validity_dates": {
                    "type": "object",
                    "properties": {
                        "start_date": {"type": ["string", "null"]},
                        "end_date": {"type": ["string", "null"]},
                        "dates_visible": {"type": "boolean"}
                    }
                }
            }
        },
        "products": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "product_name": {"type": "string"},
                    "brand": {"type": ["string", "null"]},
                    "promo_price": {"type": ["number", "null"]},
                    "regular_price": {"type": ["number", "null"]},
                    "stock_level": {
                        "type": "string",
                        "enum": ["full", "adequate", "low", "out_of_stock"]
                    }
                }
            }
        },
        "issues": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "issue_type": {
                        "type": "string",
                        "enum": ["out_of_stock", "missing_signage", "incorrect_price",
                                "damaged_display", "expired_promo", "poor_visibility", "other"]
                    },
                    "severity": {
                        "type": "string",
                        "enum": ["critical", "high", "medium", "low"]
                    },
                    "description": {"type": "string"}
                }
            }
        },
        "compliance_status": {
            "type": "string",
            "enum": ["compliant", "minor_issues", "major_issues", "non_compliant"]
        },
        "image_quality": {
            "type": "string",
            "enum": ["clear", "partial", "poor"]
        },
        "confidence": {
            "type": "number",
            "minimum": 0.0,
            "maximum": 1.0
        },
        "notes": {"type": ["string", "null"]}
    }
}

# FIFO Compliance Schema
FIFO_SCHEMA = {
    "type": "object",
    "required": ["capture_type", "fifo_compliance", "products", "confidence"],
    "properties": {
        "capture_type": {
            "type": "string",
            "enum": ["fifo"]
        },
        "fifo_compliance": {
            "type": "object",
            "required": ["compliant", "total_products_checked", "violations_found"],
            "properties": {
                "compliant": {"type": "boolean"},
                "total_products_checked": {"type": "number"},
                "violations_found": {"type": "number"},
                "overall_status": {
                    "type": "string",
                    "enum": ["compliant", "minor_violations", "major_violations", "unclear"]
                }
            }
        },
        "products": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["product_name", "fifo_status"],
                "properties": {
                    "product_name": {"type": "string"},
                    "brand": {"type": ["string", "null"]},
                    "front_expiry_date": {"type": ["string", "null"]},
                    "back_expiry_date": {"type": ["string", "null"]},
                    "fifo_status": {
                        "type": "string",
                        "enum": ["correct", "violation", "unclear", "unable_to_verify"]
                    },
                    "violation_details": {"type": ["string", "null"]},
                    "days_until_expiry_front": {"type": ["number", "null"]},
                    "recommendation": {"type": ["string", "null"]}
                }
            }
        },
        "issues": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "product_name": {"type": "string"},
                    "issue_type": {
                        "type": "string",
                        "enum": ["newer_in_front", "expired_in_front", "mixed_dates", "unclear_dates"]
                    },
                    "severity": {
                        "type": "string",
                        "enum": ["critical", "high", "medium", "low"]
                    },
                    "description": {"type": "string"}
                }
            }
        },
        "image_quality": {
            "type": "string",
            "enum": ["clear", "partial", "poor"]
        },
        "confidence": {
            "type": "number",
            "minimum": 0.0,
            "maximum": 1.0
        },
        "notes": {"type": ["string", "null"]}
    }
}

# Image Quality Pre-check Schema
QUALITY_CHECK_SCHEMA = {
    "type": "object",
    "required": ["suitable_for_analysis", "recommendation"],
    "properties": {
        "suitable_for_analysis": {"type": "boolean"},
        "blur_level": {
            "type": "string",
            "enum": ["clear", "slight", "severe"]
        },
        "lighting": {
            "type": "string",
            "enum": ["good", "dim", "overexposed"]
        },
        "angle": {
            "type": "string",
            "enum": ["straight", "angled", "obstructed"]
        },
        "content_visible": {"type": "boolean"},
        "issues": {
            "type": "array",
            "items": {"type": "string"}
        },
        "recommendation": {
            "type": "string",
            "enum": ["proceed", "retake_blur", "retake_lighting", "retake_angle", "retake_framing"]
        }
    }
}

# Map capture types to schemas
SCHEMAS = {
    "waste": WASTE_SCHEMA,
    "shelf": SHELF_SCHEMA,
    "promo": PROMO_SCHEMA,
    "fifo": FIFO_SCHEMA,
    "quality_check": QUALITY_CHECK_SCHEMA
}
