# 🏥 MediSign Professional Dashboard

A modern, high-performance web interface for medical sign language recognition, built with React, Vite, and Tailwind CSS.

## 🚀 Features

- **Professional UI**: Medical-tech aesthetic with a clean, high-contrast palette.
- **Real-time Webcam Capture**: Direct browser-to-backend inference.
- **Video File Upload**: Support for batch processing of recorded sign language clips.
- **AI-Powered Diagnostics**: Integrated with BiLSTM+Attention neural networks.
- **Interactive History Logs**: Comprehensive audit trail of all predictions.
- **Audio Feedback**: Text-to-speech integration for accessibility and validation.



## 🏃 Getting Started

### Prerequisites

- [Node.js](https://nodejs.org/) (v18.0.0 or higher)
- [npm](https://www.npmjs.com/) (v9.0.0 or higher)

### Installation

1. Navigate to the frontend directory:
   ```powershell
   cd "c:/Users/vishn/OneDrive/Desktop/New folder/medisign/frontend"
   ```

2. Install dependencies:
   ```powershell
   npm install
   ```

3. Start the development server:
   ```powershell
   npm run dev
   ```

4. Open your browser to: `http://localhost:5173`

## 🔌 Backend Integration

This frontend is designed to communicate with the MediSign Flask/FastAPI backend.

- **API Base URL**: `http://localhost:5000/api`
- **Prediction Endpoint**: `/recognize` (POST, accepts `multipart/form-data`)
- **Info Endpoint**: `/info` (GET)

To connect to a different backend server, update the `API_BASE_URL` in `src/services/predictionService.js`.

## 🔐 Credentials (Demo)

- **Username**: `admin@medisign.ai`
- **Password**: `password`

## 📁 Project Structure

```
src/
├── components/   # Modular UI views (Overview, Webcam, Upload, History)
├── layouts/      # Shared structures (Sidebar, Header, Auth)
├── pages/        # Route-level components (Login, Dashboard)
├── services/     # API client and business logic
├── theme/        # Tailwind configuration and design system
└── App.jsx       # Routing and global state
```

---
**Version**: 2.0.0 (Professional)  
**Status**: 🟢 Production Ready
