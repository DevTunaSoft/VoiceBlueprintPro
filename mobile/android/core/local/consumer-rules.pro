# JNI looks these up by name and exact signature (see NativeTtsCallback).
-keep class com.k2fsa.sherpa.onnx.** { *; }
-keep class com.devtunasoft.voiceblueprint.mobile.local.NativeControl { *; }
-keep class com.devtunasoft.voiceblueprint.mobile.local.NativeTtsCallback { *; }

# Portable source-built MP3 exporter JNI.
-keep class com.devtunasoft.voiceblueprint.mobile.local.NativeMp3Bridge { *; }
