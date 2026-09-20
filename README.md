# 🌴 Palm Mitra 2.0

### AI-Powered Oil Palm Cultivation Guidance System

Palm Mitra 2.0 is an AI-based decision-support platform designed
to assist oil-palm farmers with leaf health analysis, nutrient
deficiency detection, weather-aware irrigation guidance, and
personalized cultivation recommendations.

## 🎯 Problem Statement

Oil-palm farmers may face difficulty identifying leaf health
problems, nutrient deficiencies, irrigation requirements, and
appropriate cultivation actions at the right time.

Palm Mitra addresses this problem by combining machine learning,
computer vision, weather information, farm context, and a
recommendation engine into a single platform.

## 🧠 AI / ML Components

### 1. Disease / Health Screening
MobileNetV3-Small is used to classify uploaded oil-palm leaf
images into:

- Healthy
- Problem Detected
- Uncertain

### 2. Nutrient Deficiency Detection
YOLO11n is used to identify visible nutrient-deficiency patterns:

- Boron deficiency
- Magnesium deficiency
- Nitrogen deficiency
- Potassium deficiency

### 3. Recommendation Engine
The recommendation engine combines ML results with farm context
to generate actionable cultivation guidance.

### 4. Weather-Aware Guidance
Live weather information is incorporated into irrigation-related
recommendations.

## 🏗️ System Architecture

Farmer
   ↓
Web Interface
   ↓
FastAPI Backend
   ↓
Image Processing
   ↓
┌───────────────────────────┐
│ MobileNetV3-Small         │
│ Health/Disease Screening  │
└───────────────────────────┘
   ↓
┌───────────────────────────┐
│ YOLO11n                   │
│ Nutrient Detection        │
└───────────────────────────┘
   ↓
Recommendation Engine
   ↓
Farm Context + Weather
   ↓
Personalized Guidance

## 🛠️ Technology Stack

- Python
- FastAPI
- JavaScript
- HTML/CSS
- PyTorch
- Ultralytics YOLO
- MobileNetV3-Small
- OpenWeather API
- Git/GitHub

## 🧪 Testing

The project contains automated tests covering important ML and
application logic, including:

- Disease detector
- Leaf analyzer
- Edge cases
- Error handling

## 🚀 Deployment

The application is deployed as a live web application.

## 👥 Team

[Add team members here]

## 📄 Documentation

- SRS
- System Architecture
- ML Model Documentation
- Testing Documentation
- Project Plan
