# Add project specific ProGuard rules here

# TensorFlow Lite rules
-keep class org.tensorflow.lite.** { *; }
-keep interface org.tensorflow.lite.** { *; }

# Keep native methods
-keepclasseswithmembernames class * {
    native <methods>;
}

# Keep classification result classes
-keep class com.example.fruitidentifier.ClassificationResult { *; }
-keep class com.example.fruitidentifier.ClassificationOutput { *; }
