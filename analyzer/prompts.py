"""
Type-specific prompts for different compliance analysis scenarios.
"""

SYSTEM_PROMPT = """You are a retail store compliance auditor AI. Your job is to analyze store images and extract structured data for compliance reporting.

CRITICAL RULES:
- Only report what you can SEE in the image. Never assume or infer.
- If text/dates are partially visible or unclear, mark as "unclear" or null.
- Confidence score: 0.0-1.0 based on image clarity and certainty.
- Return ONLY valid JSON matching the specified schema. No explanations outside JSON.
- Use null for fields you cannot determine.
- Be precise with counts and measurements.

CONTEXT:
- Store format: Retail/grocery store
- Purpose: Compliance auditing, waste tracking, shelf monitoring, promotional compliance
- Data feeds into operations dashboards and reporting systems"""

WASTE_PROMPT = """TASK: Analyze this waste/disposal image for shrinkage reporting.

EXTRACT:
1. PRODUCTS - Identify each distinct product:
   - product_name: Exact name if readable, else descriptive ("branded milk 500ml")
   - brand: If visible, else null
   - sku: Only if barcode/label clearly shows it, else null
   - quantity: Count or estimate ("~5" or number)
   - unit: "pieces", "kg", "packs", "bottles", etc.
   - expiry_date: YYYY-MM-DD format if visible, else null
   - batch_code: If visible, else null
   - mrp: If price label visible (number only), else null

2. CONDITION - For each product:
   - condition: "expired" | "damaged" | "spoiled" | "packaging_torn" | "contaminated" | "recall"
   - damage_details: Specific observation ("dented can", "mold visible", "leaked", "brown spots")

3. METADATA:
   - waste_reason: Primary cause for waste (be specific)
   - estimated_total_items: Sum of all quantities
   - image_quality: "clear" | "partial" | "poor"
   - confidence: 0.0-1.0 overall confidence in analysis

Return structured JSON following the waste schema."""

SHELF_PROMPT = """TASK: Analyze this shelf image for On-Shelf Availability (OSA) and compliance.

EXTRACT:
1. SHELF OVERVIEW:
   - total_facings: Total number of product facings visible on shelf
   - stocked_facings: Number of facings with product present
   - empty_facings: Number of empty/out-of-stock facings
   - osa_percentage: (stocked_facings / total_facings) * 100
   - shelf_level: "top" | "middle" | "bottom" | "eye_level" (if determinable)
   - category: Product category if identifiable

2. PRODUCTS - For each visible product:
   - product_name: Name as visible on packaging
   - brand: Brand name
   - facings: Number of facings for this product
   - stock_level: "full" | "adequate" | "low" | "out_of_stock"
   - price_visible: true/false - is price tag visible?
   - planogram_compliant: true/false/null - appears properly placed?

3. ISSUES - Identify compliance issues:
   - issue_type: "out_of_stock" | "low_stock" | "misplaced" | "damaged_product" | "missing_price" | "poor_facing" | "expired_visible" | "other"
   - product_name: Affected product (if applicable)
   - location: Where on shelf
   - severity: "critical" | "high" | "medium" | "low"
   - description: Specific details

4. OVERALL:
   - compliance_status: "compliant" | "issues_found" | "critical_issues" | "unclear"
   - image_quality: "clear" | "partial" | "poor"
   - confidence: 0.0-1.0

Return structured JSON following the shelf schema."""

PROMO_PROMPT = """TASK: Analyze this promotional display for compliance and execution quality.

EXTRACT:
1. PROMO DETAILS:
   - promo_type: "endcap" | "display_stand" | "shelf_signage" | "bundle" | "price_reduction" | "other"
   - promo_title: Title/text on promotional signage (if visible)
   - products_on_promo: Count of distinct products in promotion
   - display_quality: "excellent" | "good" | "poor" | "damaged"
   - signage_visible: true/false - promotional signage present and visible?
   - price_visible: true/false - promotional price clearly displayed?
   - validity_dates:
     - start_date: YYYY-MM-DD if visible, else null
     - end_date: YYYY-MM-DD if visible, else null
     - dates_visible: true/false

2. PRODUCTS - For each product in promotion:
   - product_name: Name visible on product
   - brand: Brand name
   - promo_price: Promotional price (number only) if visible
   - regular_price: Regular price (number only) if visible
   - stock_level: "full" | "adequate" | "low" | "out_of_stock"

3. ISSUES - Compliance problems:
   - issue_type: "out_of_stock" | "missing_signage" | "incorrect_price" | "damaged_display" | "expired_promo" | "poor_visibility" | "other"
   - severity: "critical" | "high" | "medium" | "low"
   - description: Specific details

4. OVERALL:
   - compliance_status: "compliant" | "minor_issues" | "major_issues" | "non_compliant"
   - image_quality: "clear" | "partial" | "poor"
   - confidence: 0.0-1.0

Return structured JSON following the promo schema."""

FIFO_PROMPT = """TASK: Analyze this image for FIFO (First In, First Out) compliance - verify older products are in front.

EXTRACT:
1. FIFO COMPLIANCE:
   - compliant: true/false - is FIFO being followed?
   - total_products_checked: Number of products where dates were verifiable
   - violations_found: Number of FIFO violations detected
   - overall_status: "compliant" | "minor_violations" | "major_violations" | "unclear"

2. PRODUCTS - For each product where dates are visible:
   - product_name: Name on packaging
   - brand: Brand name
   - front_expiry_date: YYYY-MM-DD of front-most product (if visible)
   - back_expiry_date: YYYY-MM-DD of back product (if visible)
   - fifo_status: "correct" | "violation" | "unclear" | "unable_to_verify"
     - "correct": Older dates in front (proper FIFO)
     - "violation": Newer dates in front (FIFO violation)
   - violation_details: Specific issue if violation found
   - days_until_expiry_front: Days remaining until expiry of front product
   - recommendation: Action needed (e.g., "rotate stock", "remove expired")

3. ISSUES - Specific FIFO problems:
   - product_name: Affected product
   - issue_type: "newer_in_front" | "expired_in_front" | "mixed_dates" | "unclear_dates"
   - severity: "critical" | "high" | "medium" | "low"
     - "critical": Expired products in front
     - "high": Newer products significantly ahead of older ones
   - description: Specific details

4. OVERALL:
   - image_quality: "clear" | "partial" | "poor"
   - confidence: 0.0-1.0
   - notes: Additional observations

Return structured JSON following the FIFO schema."""

QUALITY_CHECK_PROMPT = """TASK: Assess if this image is suitable for compliance analysis.

CHECK:
- blur_level: "clear" | "slight" | "severe"
  - "clear": Text and labels are sharp and readable
  - "slight": Minor blur but most content readable
  - "severe": Significant blur affecting readability

- lighting: "good" | "dim" | "overexposed"
  - "good": Well-lit, colors accurate, details visible
  - "dim": Underexposed, shadows obscure details
  - "overexposed": Washed out, blown highlights

- angle: "straight" | "angled" | "obstructed"
  - "straight": Direct view of subject
  - "angled": Acceptable angle but not optimal
  - "obstructed": View blocked or significantly skewed

- content_visible: true/false
  - true: Relevant compliance content (products, labels, dates) in frame
  - false: Key content missing or out of frame

RETURN:
- suitable_for_analysis: true/false
  - true: Image is acceptable for analysis
  - false: Image quality issues prevent accurate analysis

- issues: List of specific problems (e.g., ["severe blur", "dim lighting"])

- recommendation: "proceed" | "retake_blur" | "retake_lighting" | "retake_angle" | "retake_framing"
  - "proceed": Image is acceptable, continue with analysis
  - "retake_blur": Retake with better focus
  - "retake_lighting": Retake with better lighting
  - "retake_angle": Retake from better angle
  - "retake_framing": Retake to include all relevant content

Return structured JSON following the quality_check schema."""

# Map capture types to prompts
TYPE_PROMPTS = {
    "waste": WASTE_PROMPT,
    "shelf": SHELF_PROMPT,
    "promo": PROMO_PROMPT,
    "fifo": FIFO_PROMPT,
    "quality_check": QUALITY_CHECK_PROMPT
}
