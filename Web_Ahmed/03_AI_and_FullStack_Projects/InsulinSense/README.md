# InsulinSense

An intelligent system that helps diabetic patients track their meals, analyze lab results, and predict insulin doses using machine learning models.

---

## Project Structure

```
InsulinSense/
├── app.py                  # Main Flask server
├── meal_engine.py          # Meal analysis engine
├── ocr_utils.py            # Text extraction from images
├── smart_imputation.py     # Missing data handling
├── train_model.py          # Insulin model training
├── prepare_data.py         # Data preparation
├── insulin_model.pkl       # Trained ML model
├── users.db                # SQLite user database
├── requirements.txt        # Python dependencies
│
├── insulin-frontend/       # React frontend
│   ├── public/
│   └── src/
│       ├── components/
│       │   ├── AuthPage.jsx
│       │   ├── Dashboard.jsx
│       │   ├── Home.jsx
│       │   ├── MealPlan.jsx
│       │   ├── Navbar.jsx
│       │   ├── OCRUpload.jsx
│       │   ├── Predict.jsx
│       │   └── Profile.jsx
│       └── styles/
│
├── raw_data/               # Raw datasets
├── processed_data/         # Processed datasets
└── templates/              # Flask HTML templates
```

---

## Prerequisites

Make sure you have the following installed before running the project:

- Python 3.10 or higher
- Node.js 18 or higher and npm
- Git

---

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/InsulinSense.git
cd InsulinSense
```

---

### 2. Backend Setup (Python / Flask)

#### Create a virtual environment

```bash
python -m venv venv310
```

#### Activate the virtual environment

On Windows:
```bash
venv310\Scripts\activate
```

On Mac / Linux:
```bash
source venv310/bin/activate
```

#### Install dependencies

```bash
pip install -r requirements.txt
```

#### Create a `.env` file

Create a `.env` file in the root directory and add the following:

```env
SECRET_KEY=your_secret_key_here
DEBUG=True
```

#### Run the server

```bash
python app.py
```

The server will run at: http://localhost:5000

---

### 3. Frontend Setup (React)

#### Navigate to the frontend directory

```bash
cd insulin-frontend
```

#### Install packages

```bash
npm install
```

#### Create a `.env` file for the frontend

Create a `.env` file inside the `insulin-frontend` directory:

```env
REACT_APP_API_URL=http://localhost:5000
```

#### Start the frontend

```bash
npm start
```

The app will open at: http://localhost:3000

---

## Retraining the Model (Optional)

If you want to retrain the insulin prediction model from scratch:

```bash
python prepare_data.py
python train_model.py
```

The trained model will be saved automatically as `insulin_model.pkl`.

---

## Features

| Feature | Description |
|---------|-------------|
| Authentication | Full user login and registration system |
| Dashboard | Personal data overview and analytics |
| Meal Plan | Personalized dietary recommendations |
| OCR Upload | Upload lab result images for automatic value extraction |
| Insulin Prediction | AI-based suggested dose calculation |
| Dark Mode | Light and dark theme support |
| Multi-language | Arabic and English language support |

---

## Troubleshooting

**Issues installing Python dependencies:**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Frontend not connecting to the backend:**
- Make sure Flask is running on port 5000
- Check the `.env` file inside the `insulin-frontend` directory

**Database errors:**
```bash
python app.py  # Flask creates the tables automatically on first run
```

---

## License

This project is intended for educational and research purposes only. It is not a substitute for professional medical advice.
