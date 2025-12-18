# 🎯 Smart Ad Selector

<div align="center">

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![OpenCV](https://img.shields.io/badge/OpenCV-4.0+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

**AI-Powered Gender and Age Detection for Targeted Advertising**

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Configuration](#-configuration) • [Screenshots](#-screenshots) • [Contributing](#-contributing)

</div>

---

## 📖 Overview

**Smart Ad Selector** is an intelligent advertising system that uses advanced computer vision and deep learning to detect a person's gender and age in real-time through a webcam. Based on the detected demographics, the system automatically opens targeted advertisements, making it perfect for digital signage, kiosks, and interactive advertising displays.

The application leverages pre-trained Caffe models for accurate age and gender classification, providing a seamless and automated advertising experience.

---

## ✨ Features

- 🎥 **Real-time Detection**: Live webcam feed with instant gender and age detection
- 🤖 **AI-Powered**: Uses deep learning models (Caffe) for accurate classification
- 🎯 **Targeted Advertising**: Automatically opens ads based on detected demographics
- ⚙️ **Customizable Settings**: Configure different ad URLs for various age groups and genders
- ⏱️ **Configurable Delays**: Set custom delay intervals between ad displays
- 🎨 **Modern GUI**: Beautiful and intuitive Tkinter-based user interface
- 💾 **Settings Persistence**: Saves configuration to JSON file
- 🔄 **Browser Management**: Automatically closes browsers before opening new ads

---

## 🛠️ Installation

### Prerequisites

- Python 3.7 or higher
- Webcam/Camera
- Windows OS (for browser management features)

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/ai_gender_age_scanner.git
cd ai_gender_age_scanner
```

### Step 2: Install Dependencies

```bash
pip install opencv-python numpy pillow tkinter
```

Or create a `requirements.txt` and install:

```bash
pip install -r requirements.txt
```

**Required Packages:**
- `opencv-python` - For computer vision and model loading
- `numpy` - For numerical operations
- `Pillow` - For image processing
- `tkinter` - For GUI (usually included with Python)

### Step 3: Download Model Files

Ensure you have the following model files in the project directory:
- `age_net.caffemodel` - Age detection model
- `gender_net.caffemodel` - Gender detection model
- `deploy_age.prototxt` - Age model architecture
- `deploy_gender.prototxt` - Gender model architecture

---

## 🚀 Usage

### Running the Application

1. **Start the application:**
   ```bash
   python test10.py
   ```

2. **Main Interface:**
   - Click **"Start"** to begin detection
   - A 10-second countdown will appear before the camera activates
   - The webcam window will show real-time detection results

3. **Detection Process:**
   - The system detects gender (Male/Female) and age group
   - Age groups: (0-2), (4-6), (8-12), (15-20), (25-32), (38-43), (48-53), (60-100)
   - After detection, a 3-second countdown appears before opening the ad
   - Press `q` in the webcam window to stop detection

4. **Settings:**
   - Click **"Settings"** to configure ad URLs and delay times
   - Set different URLs for each gender and age group
   - Adjust the delay between ad displays (in seconds)

5. **Exit:**
   - Click **"Exit"** to close the application

---

## ⚙️ Configuration

### Settings File

The application uses `settings.json` to store configuration:

```json
{
    "ad_urls": {
        "Male": {
            "(0-2)": "https://example.com/kids-ads",
            "(4-6)": "https://example.com/toddler-ads",
            ...
        },
        "Female": {
            "(0-2)": "https://example.com/kids-ads",
            ...
        }
    },
    "delay_seconds": 30
}
```

### Age Groups

The system classifies age into 8 groups:
- `(0-2)` - Infants
- `(4-6)` - Toddlers
- `(8-12)` - Children
- `(15-20)` - Teenagers
- `(25-32)` - Young Adults
- `(38-43)` - Adults
- `(48-53)` - Middle-aged
- `(60-100)` - Seniors

### Configuring Ad URLs

1. Open the application
2. Click **"Settings"**
3. Select **"Male"** or **"Female"**
4. Enter URLs for each age group
5. Click **"Save"**
6. Set the delay time (seconds between ad displays)
7. Save settings

---

## 📸 Screenshots

### Main Interface
The application features a modern dark-themed GUI with intuitive controls.

### Detection Window
Real-time webcam feed showing detected gender and age with on-screen labels.

### Settings Panel
Easy-to-use interface for configuring ad URLs and system parameters.

---

## 🏗️ Project Structure

```
ai_gender_age_scanner/
│
├── test10.py                 # Main application file
├── settings.json             # Configuration file
├── age_net.caffemodel        # Age detection model
├── gender_net.caffemodel     # Gender detection model
├── deploy_age.prototxt       # Age model architecture
├── deploy_gender.prototxt    # Gender model architecture
├── icon.png                  # Application icon
├── banner.png                # Banner image
├── pic.png                   # Developer photo
├── start_icon.png            # Start button icon
├── exit_icon.png             # Exit button icon
├── settings_icon.png         # Settings button icon
├── contact_icon.png          # Contact button icon
├── README.md                 # This file
└── LICENSE                   # MIT License
```

---

## 🔧 Technical Details

### Models Used

- **Age Detection**: Caffe-based deep learning model trained on age classification
- **Gender Detection**: Caffe-based deep learning model for gender classification
- **Input Size**: 227x227 pixels
- **Framework**: OpenCV DNN module

### Detection Process

1. Capture frame from webcam
2. Preprocess image (resize to 227x227, normalize)
3. Run gender detection model
4. Run age detection model
5. Display results on frame
6. Open targeted ad based on results

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Developer

**Patchara Al-umaree**

- 📧 Email: Patcharaalumaree@gmail.com
- 🆔 Student ID: 6651630177
- 🔗 GitHub: [@MrPatchara](https://github.com/MrPatchara)

---

## ⚠️ Disclaimer

This application is intended for educational and research purposes. Please ensure compliance with privacy laws and regulations in your jurisdiction when using this software. The developers are not responsible for any misuse of this application.

---

## 🙏 Acknowledgments

- OpenCV community for excellent computer vision tools
- Caffe framework for pre-trained models
- All contributors and users of this project

---

<div align="center">

**Made with ❤️ using Python and OpenCV**

⭐ Star this repo if you find it helpful!

</div>
