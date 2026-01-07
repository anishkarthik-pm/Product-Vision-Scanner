package com.example.fruitidentifier

import android.graphics.Bitmap
import android.graphics.ImageFormat
import android.graphics.Rect
import android.graphics.YuvImage
import android.media.Image
import java.io.ByteArrayOutputStream
import java.nio.ByteBuffer

/**
 * Image preprocessing utilities for TFLite model inference.
 *
 * This class handles:
 * 1. Converting camera images to Bitmap
 * 2. Resizing to model input size
 * 3. Normalizing pixel values
 * 4. Converting to ByteBuffer for TFLite
 */
object ImageProcessor {

    /**
     * Convert CameraX Image to Bitmap.
     *
     * CameraX provides images in YUV_420_888 format which needs
     * to be converted to RGB Bitmap for processing.
     *
     * @param image CameraX Image from camera
     * @return RGB Bitmap
     */
    fun imageToBitmap(image: Image): Bitmap {
        val yBuffer = image.planes[0].buffer // Y
        val vuBuffer = image.planes[2].buffer // VU

        val ySize = yBuffer.remaining()
        val vuSize = vuBuffer.remaining()

        val nv21 = ByteArray(ySize + vuSize)

        yBuffer.get(nv21, 0, ySize)
        vuBuffer.get(nv21, ySize, vuSize)

        val yuvImage = YuvImage(nv21, ImageFormat.NV21, image.width, image.height, null)
        val out = ByteArrayOutputStream()
        yuvImage.compressToJpeg(Rect(0, 0, yuvImage.width, yuvImage.height), 100, out)
        val imageBytes = out.toByteArray()

        return android.graphics.BitmapFactory.decodeByteArray(imageBytes, 0, imageBytes.size)
    }

    /**
     * Resize bitmap to target size.
     *
     * @param bitmap Input bitmap
     * @param targetSize Target width/height (assuming square)
     * @return Resized bitmap
     */
    fun resizeBitmap(bitmap: Bitmap, targetSize: Int): Bitmap {
        return Bitmap.createScaledBitmap(bitmap, targetSize, targetSize, true)
    }

    /**
     * Convert bitmap to ByteBuffer for TFLite inference.
     *
     * This performs:
     * 1. Extract RGB pixel values
     * 2. Normalize to [-1, 1] range (required by MobileNetV2)
     * 3. Pack into ByteBuffer in FLOAT32 format
     *
     * @param bitmap Input bitmap (should be resized to model input size)
     * @param inputSize Model input size (224 for MobileNetV2)
     * @return ByteBuffer ready for TFLite inference
     */
    fun bitmapToByteBuffer(bitmap: Bitmap, inputSize: Int): ByteBuffer {
        // Allocate buffer: 4 bytes per float * 3 channels * width * height
        val byteBuffer = ByteBuffer.allocateDirect(4 * inputSize * inputSize * 3)
        byteBuffer.order(java.nio.ByteOrder.nativeOrder())

        // Extract pixel values
        val intValues = IntArray(inputSize * inputSize)
        bitmap.getPixels(intValues, 0, bitmap.width, 0, 0, bitmap.width, bitmap.height)

        // Normalize and add to buffer
        var pixel = 0
        for (i in 0 until inputSize) {
            for (j in 0 until inputSize) {
                val pixelValue = intValues[pixel++]

                // Extract RGB values (0-255)
                val r = (pixelValue shr 16 and 0xFF)
                val g = (pixelValue shr 8 and 0xFF)
                val b = (pixelValue and 0xFF)

                // Normalize to [-1, 1] (MobileNetV2 preprocessing)
                byteBuffer.putFloat((r - 127.5f) / 127.5f)
                byteBuffer.putFloat((g - 127.5f) / 127.5f)
                byteBuffer.putFloat((b - 127.5f) / 127.5f)
            }
        }

        return byteBuffer
    }

    /**
     * Complete preprocessing pipeline: Image -> ByteBuffer
     *
     * @param image CameraX Image
     * @param inputSize Model input size
     * @return ByteBuffer ready for inference
     */
    fun preprocessImage(image: Image, inputSize: Int): ByteBuffer {
        val bitmap = imageToBitmap(image)
        val resized = resizeBitmap(bitmap, inputSize)
        return bitmapToByteBuffer(resized, inputSize)
    }

    /**
     * Preprocess Bitmap (for testing with static images)
     *
     * @param bitmap Input bitmap
     * @param inputSize Model input size
     * @return ByteBuffer ready for inference
     */
    fun preprocessBitmap(bitmap: Bitmap, inputSize: Int): ByteBuffer {
        val resized = resizeBitmap(bitmap, inputSize)
        return bitmapToByteBuffer(resized, inputSize)
    }

    /**
     * Center crop bitmap to square
     *
     * Useful for processing images that aren't square.
     *
     * @param bitmap Input bitmap
     * @return Square bitmap
     */
    fun centerCropBitmap(bitmap: Bitmap): Bitmap {
        val dimension = minOf(bitmap.width, bitmap.height)
        val x = (bitmap.width - dimension) / 2
        val y = (bitmap.height - dimension) / 2
        return Bitmap.createBitmap(bitmap, x, y, dimension, dimension)
    }
}
