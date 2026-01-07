package com.example.fruitidentifier

import android.content.Context
import android.graphics.Bitmap
import android.util.Log
import org.tensorflow.lite.Interpreter
import org.tensorflow.lite.gpu.CompatibilityList
import org.tensorflow.lite.gpu.GpuDelegate
import java.io.BufferedReader
import java.io.FileInputStream
import java.io.InputStreamReader
import java.nio.ByteBuffer
import java.nio.MappedByteBuffer
import java.nio.channels.FileChannel

/**
 * TensorFlow Lite classifier for fruit and vegetable identification.
 *
 * This class:
 * 1. Loads TFLite model from assets
 * 2. Loads class labels
 * 3. Initializes GPU delegate for acceleration
 * 4. Runs inference on input images
 * 5. Returns top-K predictions
 *
 * Usage:
 *   val classifier = TFLiteClassifier(context)
 *   val results = classifier.classify(bitmap)
 *   results.results.forEach { println(it) }
 */
class TFLiteClassifier(
    private val context: Context,
    private val modelPath: String = "model.tflite",
    private val labelsPath: String = "labels.txt",
    private val numThreads: Int = 4,
    private val useGpu: Boolean = true
) {
    companion object {
        private const val TAG = "TFLiteClassifier"
        private const val IMAGE_SIZE = 224  // MobileNetV2 input size
        private const val MAX_RESULTS = 5   // Top-K results to return
    }

    // TFLite interpreter
    private var interpreter: Interpreter? = null

    // GPU delegate for hardware acceleration
    private var gpuDelegate: GpuDelegate? = null

    // Class labels loaded from file
    private var labels: List<String> = emptyList()

    // Model metadata
    private var numClasses: Int = 0

    init {
        loadModel()
        loadLabels()
    }

    /**
     * Load TFLite model from assets folder.
     *
     * Steps:
     * 1. Read model file into MappedByteBuffer
     * 2. Configure interpreter options (threads, GPU)
     * 3. Create interpreter instance
     */
    private fun loadModel() {
        try {
            Log.d(TAG, "Loading model: $modelPath")

            // Load model file
            val modelFile = loadModelFile(modelPath)

            // Configure interpreter options
            val options = Interpreter.Options()
            options.setNumThreads(numThreads)

            // Try to use GPU delegate if available
            if (useGpu) {
                val compatList = CompatibilityList()
                if (compatList.isDelegateSupportedOnThisDevice) {
                    gpuDelegate = GpuDelegate(compatList.bestOptionsForThisDevice)
                    options.addDelegate(gpuDelegate)
                    Log.d(TAG, "GPU delegate enabled")
                } else {
                    Log.d(TAG, "GPU delegate not supported, using CPU")
                }
            }

            // Create interpreter
            interpreter = Interpreter(modelFile, options)

            // Log model info
            val inputShape = interpreter?.getInputTensor(0)?.shape()
            val outputShape = interpreter?.getOutputTensor(0)?.shape()

            Log.d(TAG, "Model loaded successfully")
            Log.d(TAG, "  Input shape: ${inputShape?.contentToString()}")
            Log.d(TAG, "  Output shape: ${outputShape?.contentToString()}")

            numClasses = outputShape?.get(1) ?: 0

        } catch (e: Exception) {
            Log.e(TAG, "Error loading model", e)
            throw RuntimeException("Failed to load TFLite model", e)
        }
    }

    /**
     * Load model file from assets into MappedByteBuffer.
     */
    private fun loadModelFile(modelPath: String): MappedByteBuffer {
        val fileDescriptor = context.assets.openFd(modelPath)
        val inputStream = FileInputStream(fileDescriptor.fileDescriptor)
        val fileChannel = inputStream.channel
        val startOffset = fileDescriptor.startOffset
        val declaredLength = fileDescriptor.declaredLength
        return fileChannel.map(FileChannel.MapMode.READ_ONLY, startOffset, declaredLength)
    }

    /**
     * Load class labels from assets.
     *
     * Labels file format: one label per line
     */
    private fun loadLabels() {
        try {
            Log.d(TAG, "Loading labels: $labelsPath")

            context.assets.open(labelsPath).use { inputStream ->
                BufferedReader(InputStreamReader(inputStream)).use { reader ->
                    labels = reader.readLines().filter { it.isNotBlank() }
                }
            }

            Log.d(TAG, "Loaded ${labels.size} labels")

            if (numClasses > 0 && labels.size != numClasses) {
                Log.w(TAG, "Label count (${labels.size}) doesn't match model output (${numClasses})")
            }

        } catch (e: Exception) {
            Log.e(TAG, "Error loading labels", e)
            throw RuntimeException("Failed to load labels", e)
        }
    }

    /**
     * Run classification on input bitmap.
     *
     * Steps:
     * 1. Preprocess bitmap to ByteBuffer
     * 2. Run TFLite inference
     * 3. Parse output probabilities
     * 4. Return top-K results
     *
     * @param bitmap Input image (will be resized to 224x224)
     * @return ClassificationOutput with top predictions and timing
     */
    fun classify(bitmap: Bitmap): ClassificationOutput {
        // Start timing
        val startTime = System.currentTimeMillis()

        // Preprocess image
        val preprocessStartTime = System.currentTimeMillis()
        val inputBuffer = ImageProcessor.preprocessBitmap(bitmap, IMAGE_SIZE)
        val preprocessTime = System.currentTimeMillis() - preprocessStartTime

        // Run inference
        val inferenceStartTime = System.currentTimeMillis()
        val outputBuffer = Array(1) { FloatArray(numClasses) }

        interpreter?.run(inputBuffer, outputBuffer)

        val inferenceTime = System.currentTimeMillis() - inferenceStartTime

        // Get top-K results
        val results = getTopKResults(outputBuffer[0])

        Log.d(TAG, "Classification complete:")
        Log.d(TAG, "  Preprocess: ${preprocessTime}ms")
        Log.d(TAG, "  Inference: ${inferenceTime}ms")
        Log.d(TAG, "  Top result: ${results.firstOrNull()}")

        return ClassificationOutput(
            results = results,
            inferenceTime = inferenceTime,
            preprocessTime = preprocessTime
        )
    }

    /**
     * Run classification on preprocessed ByteBuffer.
     *
     * This is useful when you've already preprocessed the image
     * (e.g., from camera frame).
     *
     * @param inputBuffer Preprocessed image buffer
     * @return ClassificationOutput with top predictions and timing
     */
    fun classifyBuffer(inputBuffer: ByteBuffer): ClassificationOutput {
        val inferenceStartTime = System.currentTimeMillis()

        // Run inference
        val outputBuffer = Array(1) { FloatArray(numClasses) }
        interpreter?.run(inputBuffer, outputBuffer)

        val inferenceTime = System.currentTimeMillis() - inferenceStartTime

        // Get top-K results
        val results = getTopKResults(outputBuffer[0])

        return ClassificationOutput(
            results = results,
            inferenceTime = inferenceTime,
            preprocessTime = 0
        )
    }

    /**
     * Extract top-K predictions from model output.
     *
     * @param probabilities Raw model output (array of probabilities)
     * @return List of top-K ClassificationResult, sorted by confidence
     */
    private fun getTopKResults(probabilities: FloatArray): List<ClassificationResult> {
        // Create list of (index, probability) pairs
        val results = probabilities.mapIndexed { index, probability ->
            ClassificationResult(
                label = if (index < labels.size) labels[index] else "Unknown",
                confidence = probability,
                index = index
            )
        }

        // Sort by confidence descending and take top-K
        return results
            .sortedByDescending { it.confidence }
            .take(MAX_RESULTS)
    }

    /**
     * Get model input size (224 for MobileNetV2).
     */
    fun getInputSize(): Int = IMAGE_SIZE

    /**
     * Get number of classes the model can predict.
     */
    fun getNumClasses(): Int = numClasses

    /**
     * Get all class labels.
     */
    fun getLabels(): List<String> = labels

    /**
     * Check if GPU delegate is active.
     */
    fun isUsingGpu(): Boolean = gpuDelegate != null

    /**
     * Release resources.
     *
     * Call this when done with the classifier to free memory.
     */
    fun close() {
        interpreter?.close()
        interpreter = null

        gpuDelegate?.close()
        gpuDelegate = null

        Log.d(TAG, "Classifier closed")
    }

    /**
     * Benchmark inference performance.
     *
     * Useful for testing performance on different devices.
     *
     * @param iterations Number of iterations to run
     * @return Average inference time in milliseconds
     */
    fun benchmark(iterations: Int = 100): Float {
        Log.d(TAG, "Running benchmark with $iterations iterations...")

        // Create dummy input
        val dummyBitmap = Bitmap.createBitmap(IMAGE_SIZE, IMAGE_SIZE, Bitmap.Config.ARGB_8888)
        val inputBuffer = ImageProcessor.preprocessBitmap(dummyBitmap, IMAGE_SIZE)

        // Warmup
        repeat(10) {
            val outputBuffer = Array(1) { FloatArray(numClasses) }
            interpreter?.run(inputBuffer, outputBuffer)
        }

        // Benchmark
        val times = mutableListOf<Long>()
        repeat(iterations) {
            val startTime = System.nanoTime()

            val outputBuffer = Array(1) { FloatArray(numClasses) }
            interpreter?.run(inputBuffer, outputBuffer)

            val endTime = System.nanoTime()
            times.add((endTime - startTime) / 1_000_000) // Convert to ms
        }

        val avgTime = times.average().toFloat()
        val minTime = times.minOrNull() ?: 0f
        val maxTime = times.maxOrNull() ?: 0f

        Log.d(TAG, "Benchmark results:")
        Log.d(TAG, "  Average: ${String.format("%.2f", avgTime)}ms")
        Log.d(TAG, "  Min: ${String.format("%.2f", minTime)}ms")
        Log.d(TAG, "  Max: ${String.format("%.2f", maxTime)}ms")

        return avgTime
    }
}
