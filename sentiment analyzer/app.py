from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import re

app = Flask(__name__)
CORS(app)

# ---------------- EMOTION KEYWORDS ----------------
ENGLISH_EMOTIONS = {
    "happy": ["happy", "joy", "love", "amazing", "great", "awesome", "good", "best"],
    "sad": ["sad", "cry", "depressed", "lonely", "hurt", "miss""sad", "cry", "depressed", "lonely",
    "hurt", "miss", "don't like",
    "dont like", "bad", "worst",
    "pain", "upset"],
    "angry": ["angry", "hate", "frustrated", "annoyed", "mad"],
    "fearful": ["fear", "scared", "worried", "panic", "stress"],
    "surprised": ["wow", "shocked", "surprised", "amazed"],
    "neutral": ["okay", "fine", "normal"]
}

TAMIL_EMOTIONS = {
    "happy": ["மகிழ்ச்சி", "சந்தோஷம்", "அருமை", "நல்ல"],
    "sad": ["துக்கம்", "வருத்தம்", "சோகம்"],
    "angry": ["கோபம்", "எரிச்சல்"],
    "fearful": ["பயம்", "கவலை"],
    "surprised": ["ஆச்சரியம்", "வியப்பு"],
    "neutral": ["சரி", "பரவாயில்லை"]
}

TANGLISH_EMOTIONS = {
    "happy": ["semma", "super", "vera level", "romba nalla", "happy"],
    "sad": ["romba sad", "cry panren", "kastam""romba sad",
    "sad aa iruku",
    "cry panren",
    "kastam",
    "pudikala",
    "pidikala",
    "venam",
    "pidikave illa",
    "unna pudikala",
    "romba kashtama iruku",
    "hurt ah iruku"],
    "angry": ["kovam", "erichal", "waste", "frustrated","kovam",
    "erichal",
    "hate",
    "frustrated",
    "annoying",
    "waste",
    "veruppu"],
    "fearful": ["bayam", "tension", "stress"],
    "surprised": ["aiyo", "shock aiten", "wow da"],
    "neutral": ["seri", "okay da"]
}

POSITIVE_EMOTIONS = {"happy", "surprised"}
NEGATIVE_EMOTIONS = {"sad", "angry", "fearful"}

EMOJI_MAP = {
    "happy": "😊",
    "sad": "😢",
    "angry": "😠",
    "fearful": "😨",
    "surprised": "😲",
    "neutral": "😐"
}


# ---------------- HOME PAGE ROUTE ----------------
@app.route("/")
def home():
    return render_template("index.html")


# ---------------- LANGUAGE DETECTION ----------------
def detect_language(text):
    tamil_pattern = re.compile(r'[\u0B80-\u0BFF]')

    if tamil_pattern.search(text):
        return "tamil"

    tanglish_words = ["semma", "romba", "kovam", "bayam", "super", "da", "pa"]

    for word in tanglish_words:
        if word in text.lower():
            return "tanglish"

    return "english"


# ---------------- EMOTION ANALYSIS ----------------
def analyze_emotions(text, language):
    text_lower = text.lower()

    if language == "tamil":
        emotion_dict = TAMIL_EMOTIONS
    elif language == "tanglish":
        emotion_dict = TANGLISH_EMOTIONS
    else:
        emotion_dict = ENGLISH_EMOTIONS

    scores = {emotion: 0 for emotion in emotion_dict}

    for emotion, keywords in emotion_dict.items():
        for keyword in keywords:
            if keyword.lower() in text_lower:
                scores[emotion] += 1

    total = sum(scores.values())

    if total == 0:
        dominant_emotion = "neutral"
        confidence = 50
    else:
        dominant_emotion = max(scores, key=scores.get)
        confidence = min(95, int((scores[dominant_emotion] / total) * 100))

    if dominant_emotion in POSITIVE_EMOTIONS:
        sentiment = "Positive"
    elif dominant_emotion in NEGATIVE_EMOTIONS:
        sentiment = "Negative"
    else:
        sentiment = "Neutral"

    return {
        "language": language,
        "sentiment": sentiment,
        "emotion": dominant_emotion,
        "confidence": confidence,
        "emoji": EMOJI_MAP.get(dominant_emotion, "😐")
    }


# ---------------- TEXT ANALYSIS ----------------
@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    text = data.get("text", "")

    if not text:
        return jsonify({"error": "No text provided"})

    language = detect_language(text)
    result = analyze_emotions(text, language)

    return jsonify(result)


# ---------------- VOICE ANALYSIS ----------------
@app.route("/analyze-voice", methods=["POST"])
def analyze_voice():
    data = request.get_json()
    text = data.get("text", "")

    if not text:
        return jsonify({"error": "No voice text provided"})

    language = detect_language(text)
    result = analyze_emotions(text, language)
    result["source"] = "voice"

    return jsonify(result)


# ---------------- HEALTH CHECK ----------------
@app.route("/health")
def health():
    return jsonify({"status": "running"})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
