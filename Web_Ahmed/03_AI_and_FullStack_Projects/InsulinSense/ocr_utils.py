
from unittest import result
import requests
import re
import tempfile
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("OCR_API_KEY")


def extract_value(text, keywords):

    if isinstance(keywords, str):
        keywords = [keywords]

    for keyword in keywords:

        pattern = rf"{keyword}.*?(\d+\.?\d*)"

        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            return match.group(1)

    return ""


def run_ocr(file_bytes, mime_type):

    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:

        temp_file.write(file_bytes)

        temp_path = temp_file.name

    with open(temp_path, "rb") as f:

        response = requests.post(
            "https://api.ocr.space/parse/image",
            files={"file": f},
            data={
                "apikey": API_KEY,
                "language": "eng",
                "isTable": True,
                "OCREngine": 2
            }
        )

    result = response.json()
    print(result)
    if "ParsedResults" not in result:
        raise RuntimeError(f"OCR API Error: {result}")

    if not result["ParsedResults"]:
        raise RuntimeError("No text detected in image")

    parsed_text = result["ParsedResults"][0].get("ParsedText", "")

    if not parsed_text.strip():
        raise RuntimeError("OCR could not extract readable text")

    data = {
        "glucose": extract_value(parsed_text, ["FBS", "Glucose", "Blood Sugar"]),
        
        "insulin": extract_value(parsed_text, [
            "Insulin",
            "Fasting Insulin"
        ]),

        "cholesterol": extract_value(parsed_text, [
            "Cholesterol",
            "Total Cholesterol"
        ]),

        "hdl": extract_value(parsed_text, [
            "HDL",
            "HDL Cholesterol"
        ]),

        "ldl": extract_value(parsed_text, [
            "LDL",
            "LDL Cholesterol"
        ]),

        "triglycerides": extract_value(parsed_text, [
            "Triglycerides",
            "TG",
            "TRIG"
        ]),

        "hba1c": extract_value(parsed_text, [
            "HbA1c",
            "A1C",
            "HBA1C"
        ]),
    }

    return data