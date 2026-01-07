# 📱 Android Installation Guide

## Method 1: Install via USB (ADB) - Recommended

### Enable USB Debugging on Your Phone

1. **Open Settings** on your Android phone
2. **Go to "About Phone"**
3. **Tap "Build Number" 7 times** - You'll see "You are now a developer!"
4. **Go back to Settings**
5. **Open "Developer Options"** (now visible)
6. **Enable "USB Debugging"** - Toggle it ON
7. **Connect phone to computer via USB**
8. **Accept the "Allow USB Debugging" prompt** on your phone

### Install Using ADB

```bash
# Navigate to the APK location
cd /home/user/Product-Vision-Scanner/offline_fruit_identifier/android_app/FruitIdentifier

# Check your device is connected
adb devices

# You should see something like:
# List of devices attached
# ABC123456789    device

# Install the APK
adb install app/build/outputs/apk/release/app-release-unsigned.apk

# You should see:
# Performing Streamed Install
# Success
```

**✅ Done! The app is now installed on your phone.**

---

## Method 2: Manual Install (No USB)

### Step 1: Transfer APK to Phone

**Option A: USB File Transfer**
1. Connect phone to computer via USB
2. Choose "File Transfer" mode on phone
3. Copy the APK file to your phone's **Downloads** folder:
   ```
   From: android_app/FruitIdentifier/app/build/outputs/apk/release/app-release-unsigned.apk
   To: Phone/Downloads/fruit-identifier.apk
   ```

**Option B: Cloud Transfer**
1. Upload APK to Google Drive / Dropbox
2. Download on your phone
3. APK will be in Downloads folder

**Option C: Email**
1. Email the APK to yourself
2. Open email on phone
3. Download attachment

### Step 2: Enable Unknown Sources

1. **Open Settings** on your phone
2. **Go to Security** (or "Privacy" on some phones)
3. **Enable "Install Unknown Apps"**
   - You may need to select the app you'll use to install (e.g., "Files", "Chrome", "Gmail")
   - Toggle **"Allow from this source"** to ON

### Step 3: Install the APK

1. **Open File Manager** on your phone (Files, My Files, etc.)
2. **Navigate to Downloads folder**
3. **Tap on the APK file** (fruit-identifier.apk)
4. **Tap "Install"**
5. **Wait for installation** (5-10 seconds)
6. **Tap "Open"** to launch the app

**✅ Done! The app is installed.**

---

## Method 3: Wireless Install (ADB over WiFi)

### Prerequisites
- Phone and computer on same WiFi network
- USB debugging already enabled

### Steps

1. **Connect phone via USB first**
   ```bash
   adb tcpip 5555
   ```

2. **Find your phone's IP address**
   - Settings → About Phone → Status → IP Address
   - Example: 192.168.1.100

3. **Disconnect USB and connect wirelessly**
   ```bash
   adb connect 192.168.1.100:5555
   ```

4. **Install APK**
   ```bash
   adb install app/build/outputs/apk/release/app-release-unsigned.apk
   ```

---

## 🎯 After Installation

### First Launch

1. **Open the app** from your app drawer
2. **Allow camera permission** when prompted
3. **Point camera at a fruit or vegetable**
4. **See predictions appear in real-time!**

### Testing the App

Try these fruits/vegetables for best results:
- 🍎 **Apples** (red, green)
- 🍌 **Bananas**
- 🍊 **Oranges**
- 🍇 **Grapes**
- 🍅 **Tomatoes**
- 🫑 **Bell Peppers**

**Tips for accurate predictions:**
- ✅ Good, even lighting
- ✅ Hold phone steady
- ✅ Keep fruit in center of screen
- ✅ Distance: 15-30 cm from camera
- ✅ Show full fruit (not cut/partial)

---

## 🔧 Troubleshooting

### Problem: "App not installed"

**Causes & Solutions:**

1. **Insufficient storage**
   - Free up at least 50MB space
   - Go to Settings → Storage → Free up space

2. **Conflicting package**
   - Uninstall any previous version
   - Settings → Apps → Fruit Identifier → Uninstall

3. **Corrupted APK**
   - Re-download or re-build the APK
   - Verify file size is ~8-10 MB

### Problem: "Installation blocked"

**Solution:**
- Enable "Unknown Sources" or "Install Unknown Apps"
- Settings → Security → Unknown Sources → ON
- Or for newer Android: Settings → Apps → Special Access → Install Unknown Apps → [Your File Manager] → Allow

### Problem: "Parse Error"

**Causes:**
- APK is corrupted
- Wrong Android version (need 7.0+)

**Solution:**
- Re-download or re-build APK
- Check your Android version: Settings → About Phone

### Problem: "adb: device not found"

**Solutions:**

1. **Check USB connection**
   ```bash
   adb devices
   ```
   Should show your device

2. **Reconnect phone**
   - Unplug and replug USB
   - Try different USB port
   - Try different USB cable

3. **Accept USB debugging prompt**
   - Check your phone screen
   - Tap "Allow" on the prompt

4. **Restart ADB server**
   ```bash
   adb kill-server
   adb start-server
   adb devices
   ```

5. **Install/Update ADB**
   ```bash
   # On Linux
   sudo apt install android-tools-adb

   # On Mac
   brew install android-platform-tools

   # On Windows
   # Download from: https://developer.android.com/studio/releases/platform-tools
   ```

### Problem: App crashes on launch

**Check:**
1. **Model files present**
   - app/src/main/assets/model.tflite should exist
   - app/src/main/assets/labels.txt should exist

2. **Rebuild APK**
   ```bash
   cd android_app/FruitIdentifier
   ./gradlew clean
   ./gradlew assembleRelease
   ```

3. **Check Android version**
   - Requires Android 7.0 (API 24) or higher
   - Settings → About Phone → Android Version

### Problem: Camera not working

**Solutions:**
1. **Grant camera permission**
   - Settings → Apps → Fruit Identifier → Permissions → Camera → Allow

2. **Check camera access**
   - Close other apps using camera
   - Restart phone

3. **Clear app data**
   - Settings → Apps → Fruit Identifier → Storage → Clear Data

### Problem: Predictions are wrong/slow

**Optimization:**

1. **Good lighting**
   - Use bright, natural light
   - Avoid shadows and backlighting

2. **Proper distance**
   - Keep fruit 15-30cm from camera
   - Fill most of the screen

3. **Device performance**
   - Close background apps
   - Restart phone
   - Check if GPU delegate is working

---

## 📊 Checking Installation Success

### Verify Installation

```bash
# List installed packages
adb shell pm list packages | grep fruit

# Should show:
# package:com.example.fruitidentifier
```

### Check App Info

```bash
# Get app details
adb shell dumpsys package com.example.fruitidentifier | grep version

# Shows version code and name
```

### View App Logs

```bash
# See real-time logs (useful for debugging)
adb logcat | grep FruitIdentifier

# Or filter by tag
adb logcat -s TFLiteClassifier
```

---

## 🔐 Security & Permissions

### Required Permission
- **Camera** - To capture images for identification

### No Other Permissions Needed
- ❌ No internet/network
- ❌ No storage access
- ❌ No location
- ❌ No contacts
- ❌ No microphone

**100% Privacy:** Everything runs on-device, no data leaves your phone.

---

## 🗑️ Uninstalling

### Via Phone Settings
1. Settings → Apps
2. Find "Fruit Identifier"
3. Tap → Uninstall

### Via ADB
```bash
adb uninstall com.example.fruitidentifier
```

---

## 📱 Device Requirements

### Minimum Requirements
- **OS:** Android 7.0 (Nougat) or higher
- **RAM:** 2 GB
- **Storage:** 50 MB free space
- **Camera:** Any rear camera

### Recommended
- **OS:** Android 10+
- **RAM:** 4 GB+
- **Processor:** Snapdragon 600 series or better
- **Camera:** 12MP+ for better accuracy

### Performance by Device

| Device Type | Inference Speed | User Experience |
|-------------|----------------|-----------------|
| High-end (Pixel 6, S21) | 45-50ms | Excellent |
| Mid-range (Pixel 4a) | 80-100ms | Very Good |
| Budget (SD665) | 120-150ms | Good |
| Very old (<2018) | 200-300ms | Acceptable |

---

## 🎓 Quick Reference Commands

### Build APK
```bash
cd /home/user/Product-Vision-Scanner/offline_fruit_identifier
./scripts/build_apk.sh
```

### Check Device Connected
```bash
adb devices
```

### Install APK
```bash
adb install app/build/outputs/apk/release/app-release-unsigned.apk
```

### Uninstall App
```bash
adb uninstall com.example.fruitidentifier
```

### View Logs
```bash
adb logcat | grep -i fruit
```

### Get APK from Device (if already installed)
```bash
adb pull /data/app/com.example.fruitidentifier/base.apk
```

---

## 📞 Getting Help

If you encounter issues:

1. **Check this guide** - Most common issues covered above
2. **Review logs** - `adb logcat` shows detailed errors
3. **Verify files** - Ensure model.tflite and labels.txt are in assets
4. **Rebuild** - Try clean build: `./gradlew clean assembleRelease`

---

## ✅ Installation Checklist

Before asking for help, verify:

- [ ] Phone is Android 7.0 or higher
- [ ] USB debugging is enabled (for ADB method)
- [ ] Unknown sources allowed (for manual method)
- [ ] Model files exist in assets folder
- [ ] APK file size is 8-10 MB
- [ ] Phone has 50+ MB free storage
- [ ] Camera permission will be granted

---

**🎉 Ready to identify fruits and vegetables offline!**
