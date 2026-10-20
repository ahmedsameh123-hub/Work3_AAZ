# Graduation Site

## Folder structure

```
graduation-site/
├── main.py                  <- FastAPI server (don't edit)
├── config.json              <- ALL the texts (name, letter, timeline, ...)
├── requirements.txt
├── optimize_images.py       <- optional: shrinks photos so the site loads fast
├── raw_photos/              <- put your ORIGINAL photos here (for optimize_images.py)
└── static/
    ├── index.html
    ├── css/style.css
    ├── js/script.js
    ├── music/               <- put ONE song here (song.mp3) - optional
    └── images/
        ├── hero.jpg         <- her main photo (inside the arch frame)
        └── gallery/         <- all gallery photos: 1.jpg, 2.jpg, 3.jpg ...
```

## Run

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```
Open http://127.0.0.1:8000

## Share with ngrok (2nd terminal)

```powershell
ngrok config add-authtoken YOUR_TOKEN     # only once
ngrok http 8000
```
Send her the https://....ngrok-free.app link.

Or in one command: `python main.py --share`
