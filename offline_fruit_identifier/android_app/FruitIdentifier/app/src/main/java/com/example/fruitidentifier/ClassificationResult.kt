package com.example.fruitidentifier

/**
 * Data class representing a single classification result.
 *
 * @property label The predicted class name (e.g., "Apple Red Delicious")
 * @property confidence Confidence score between 0.0 and 1.0
 * @property index The class index in the model output
 */
data class ClassificationResult(
    val label: String,
    val confidence: Float,
    val index: Int
) {
    /**
     * Get confidence as percentage string (e.g., "95.2%")
     */
    fun getConfidencePercentage(): String {
        return String.format("%.1f%%", confidence * 100)
    }

    override fun toString(): String {
        return "$label (${getConfidencePercentage()})"
    }
}

/**
 * Data class containing multiple classification results and metadata.
 *
 * @property results Top-K classification results, sorted by confidence
 * @property inferenceTime Time taken for inference in milliseconds
 * @property preprocessTime Time taken for preprocessing in milliseconds
 */
data class ClassificationOutput(
    val results: List<ClassificationResult>,
    val inferenceTime: Long,
    val preprocessTime: Long
) {
    /**
     * Get the top prediction
     */
    fun getTopResult(): ClassificationResult? = results.firstOrNull()

    /**
     * Get total processing time
     */
    fun getTotalTime(): Long = inferenceTime + preprocessTime

    /**
     * Check if prediction is confident (>50%)
     */
    fun isConfident(): Boolean {
        return getTopResult()?.confidence ?: 0f > 0.5f
    }
}
