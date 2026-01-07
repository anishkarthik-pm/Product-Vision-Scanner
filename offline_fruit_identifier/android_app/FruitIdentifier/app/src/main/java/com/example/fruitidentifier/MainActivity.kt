package com.example.fruitidentifier

import android.Manifest
import android.content.pm.PackageManager
import android.os.Bundle
import android.util.Log
import android.view.View
import android.widget.TextView
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.camera.core.*
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.view.PreviewView
import androidx.core.content.ContextCompat
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.util.concurrent.ExecutorService
import java.util.concurrent.Executors

/**
 * Main activity for real-time fruit and vegetable identification.
 *
 * This activity:
 * 1. Requests camera permission
 * 2. Sets up CameraX preview
 * 3. Captures frames continuously
 * 4. Runs TFLite inference
 * 5. Displays predictions on screen
 *
 * The entire pipeline runs offline with no network calls.
 */
class MainActivity : AppCompatActivity() {

    companion object {
        private const val TAG = "MainActivity"
        private const val INFERENCE_INTERVAL_MS = 500L  // Run inference every 500ms
    }

    // UI Components
    private lateinit var previewView: PreviewView
    private lateinit var resultText: TextView
    private lateinit var confidenceText: TextView
    private lateinit var inferenceTimeText: TextView
    private lateinit var statusText: TextView

    // Camera components
    private var camera: Camera? = null
    private var cameraProvider: ProcessCameraProvider? = null
    private lateinit var cameraExecutor: ExecutorService

    // ML classifier
    private var classifier: TFLiteClassifier? = null

    // Inference control
    private var lastInferenceTime = 0L
    private var isInferenceRunning = false

    /**
     * Permission launcher for camera access
     */
    private val requestPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { isGranted ->
        if (isGranted) {
            startCamera()
        } else {
            showToast("Camera permission is required")
            finish()
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Initialize UI
        initializeViews()

        // Initialize camera executor
        cameraExecutor = Executors.newSingleThreadExecutor()

        // Initialize TFLite classifier
        initializeClassifier()

        // Request camera permission
        when {
            ContextCompat.checkSelfPermission(
                this,
                Manifest.permission.CAMERA
            ) == PackageManager.PERMISSION_GRANTED -> {
                startCamera()
            }
            else -> {
                requestPermissionLauncher.launch(Manifest.permission.CAMERA)
            }
        }
    }

    /**
     * Initialize UI components
     */
    private fun initializeViews() {
        previewView = findViewById(R.id.previewView)
        resultText = findViewById(R.id.resultText)
        confidenceText = findViewById(R.id.confidenceText)
        inferenceTimeText = findViewById(R.id.inferenceTimeText)
        statusText = findViewById(R.id.statusText)

        // Initial status
        updateStatus("Initializing...")
    }

    /**
     * Initialize TFLite classifier
     */
    private fun initializeClassifier() {
        try {
            updateStatus("Loading model...")

            classifier = TFLiteClassifier(
                context = this,
                modelPath = "model.tflite",
                labelsPath = "labels.txt",
                numThreads = 4,
                useGpu = true
            )

            updateStatus("Model loaded (${classifier?.getNumClasses()} classes)")

            // Run benchmark
            lifecycleScope.launch(Dispatchers.Default) {
                val avgTime = classifier?.benchmark(iterations = 50)
                withContext(Dispatchers.Main) {
                    updateStatus("Ready (avg inference: ${String.format("%.1f", avgTime)}ms)")
                }
            }

        } catch (e: Exception) {
            Log.e(TAG, "Error initializing classifier", e)
            showToast("Error loading model: ${e.message}")
            updateStatus("Model load failed")
        }
    }

    /**
     * Start camera and image analysis
     */
    private fun startCamera() {
        val cameraProviderFuture = ProcessCameraProvider.getInstance(this)

        cameraProviderFuture.addListener({
            try {
                cameraProvider = cameraProviderFuture.get()
                bindCameraUseCases()
            } catch (e: Exception) {
                Log.e(TAG, "Camera initialization failed", e)
                showToast("Camera error: ${e.message}")
            }
        }, ContextCompat.getMainExecutor(this))
    }

    /**
     * Bind camera preview and image analysis use cases
     */
    private fun bindCameraUseCases() {
        val cameraProvider = cameraProvider ?: return

        // Preview use case
        val preview = Preview.Builder()
            .build()
            .also {
                it.setSurfaceProvider(previewView.surfaceProvider)
            }

        // Image analysis use case
        val imageAnalysis = ImageAnalysis.Builder()
            .setBackpressureStrategy(ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST)
            .setOutputImageFormat(ImageAnalysis.OUTPUT_IMAGE_FORMAT_YUV_420_888)
            .build()
            .also {
                it.setAnalyzer(cameraExecutor, ImageAnalyzer())
            }

        // Select back camera
        val cameraSelector = CameraSelector.DEFAULT_BACK_CAMERA

        try {
            // Unbind all use cases before rebinding
            cameraProvider.unbindAll()

            // Bind use cases to camera
            camera = cameraProvider.bindToLifecycle(
                this,
                cameraSelector,
                preview,
                imageAnalysis
            )

            Log.d(TAG, "Camera bound successfully")

        } catch (e: Exception) {
            Log.e(TAG, "Use case binding failed", e)
            showToast("Camera binding failed")
        }
    }

    /**
     * Image analyzer that runs TFLite inference on camera frames
     */
    private inner class ImageAnalyzer : ImageAnalysis.Analyzer {

        override fun analyze(imageProxy: ImageProxy) {
            // Throttle inference to avoid overwhelming the device
            val currentTime = System.currentTimeMillis()
            if (currentTime - lastInferenceTime < INFERENCE_INTERVAL_MS || isInferenceRunning) {
                imageProxy.close()
                return
            }

            lastInferenceTime = currentTime
            isInferenceRunning = true

            // Run inference on background thread
            lifecycleScope.launch(Dispatchers.Default) {
                try {
                    val result = runInference(imageProxy)

                    // Update UI on main thread
                    withContext(Dispatchers.Main) {
                        displayResults(result)
                    }

                } catch (e: Exception) {
                    Log.e(TAG, "Inference error", e)
                    withContext(Dispatchers.Main) {
                        updateStatus("Inference error")
                    }
                } finally {
                    isInferenceRunning = false
                    imageProxy.close()
                }
            }
        }

        /**
         * Run TFLite inference on image
         */
        private fun runInference(imageProxy: ImageProxy): ClassificationOutput {
            val image = imageProxy.image ?: throw IllegalStateException("Image is null")

            // Convert to bitmap
            val bitmap = ImageProcessor.imageToBitmap(image)

            // Run classification
            return classifier?.classify(bitmap) ?: throw IllegalStateException("Classifier not initialized")
        }
    }

    /**
     * Display classification results on UI
     */
    private fun displayResults(output: ClassificationOutput) {
        if (output.results.isEmpty()) {
            resultText.text = "No prediction"
            confidenceText.text = ""
            inferenceTimeText.text = ""
            return
        }

        // Display top 3 results
        val topResults = output.results.take(3)

        // Top result with large text
        val topResult = topResults[0]
        resultText.text = topResult.label

        // Confidence with color coding
        val confidence = topResult.confidence
        confidenceText.text = topResult.getConfidencePercentage()
        confidenceText.setTextColor(getConfidenceColor(confidence))

        // Show other results
        val otherResults = topResults.drop(1).joinToString("\n") { result ->
            "${result.label}: ${result.getConfidencePercentage()}"
        }

        // Inference time
        inferenceTimeText.text = "Inference: ${output.inferenceTime}ms | Total: ${output.getTotalTime()}ms"

        // Update status with additional info
        if (otherResults.isNotEmpty()) {
            statusText.text = "Other predictions:\n$otherResults"
        }
    }

    /**
     * Get color based on confidence level
     */
    private fun getConfidenceColor(confidence: Float): Int {
        return when {
            confidence > 0.8f -> ContextCompat.getColor(this, android.R.color.holo_green_dark)
            confidence > 0.5f -> ContextCompat.getColor(this, android.R.color.holo_orange_dark)
            else -> ContextCompat.getColor(this, android.R.color.holo_red_dark)
        }
    }

    /**
     * Update status text
     */
    private fun updateStatus(status: String) {
        runOnUiThread {
            statusText.text = status
        }
    }

    /**
     * Show toast message
     */
    private fun showToast(message: String) {
        runOnUiThread {
            Toast.makeText(this, message, Toast.LENGTH_SHORT).show()
        }
    }

    override fun onDestroy() {
        super.onDestroy()

        // Clean up resources
        cameraExecutor.shutdown()
        classifier?.close()
        cameraProvider?.unbindAll()

        Log.d(TAG, "Activity destroyed, resources released")
    }

    /**
     * Handle back button to properly close app
     */
    override fun onBackPressed() {
        super.onBackPressed()
        finish()
    }
}
