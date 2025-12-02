from flask import Flask, render_template, request
import os
import spacy
import PyPDF2
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Load NLP model
nlp = spacy.load("en_core_web_sm")

# Skill keywords
SKILL_KEYWORDS = [
    'python', 'java', 'c++', 'c', 'html', 'css', 'javascript', 'react', 'node',
    'sql', 'flask', 'django', 'machine learning', 'deep learning', 'nlp', 'data analysis',
    'excel', 'powerbi', 'tableau', 'pandas', 'numpy', 'tensorflow', 'pytorch',
    'git', 'aws', 'linux', 'docker', 'cybersecurity', 'iot', 'arduino', 'raspberry pi'
]


def extract_text_from_pdf(file_path):
    """Extract text from uploaded PDF"""
    text = ""
    try:
        reader = PyPDF2.PdfReader(file_path)
        for page in reader.pages:
            text += page.extract_text() or ""
    except Exception as e:
        print("Error reading PDF:", e)
    return text


def extract_skills(text):
    """Simple keyword-based skill extraction"""
    text = text.lower()
    found = [skill for skill in SKILL_KEYWORDS if skill in text]
    return list(set(found))


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/analyze', methods=['POST'])
def analyze():
    resume = request.files['resume']
    jd = request.form['job_description']

    if not resume or not jd.strip():
        return "Missing input data!"

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], resume.filename)
    resume.save(file_path)

    resume_text = extract_text_from_pdf(file_path)

    # Calculate similarity
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf = vectorizer.fit_transform([resume_text, jd])
    similarity = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0] * 100

    # Extract skills
    resume_skills = extract_skills(resume_text)
    jd_skills = extract_skills(jd)
    missing_skills = [s for s in jd_skills if s not in resume_skills]

    # Personalized HR-style feedback
    match_percent = round(similarity, 2)
    if match_percent >= 80:
        message = f"🎉 Excellent, you are a perfect fit for this role at VSS Company!"
    elif match_percent >= 60:
        message = f"✅ Great! You are a good candidate for this job at VSS Company. Improve a few skills to reach 100%!"
    elif match_percent >= 40:
        message = f"⚠️ You match some of the requirements for this role at VSS Company. Try adding more relevant skills."
    else:
        message = f"❌ Currently, you are not a strong fit for this job at VSS Company. Focus on building your technical foundation."

    return render_template(
        'result.html',
        match=match_percent,
        message=message,
        resume_skills=resume_skills,
        jd_skills=jd_skills,
        missing_skills=missing_skills,
        filename=resume.filename
    )


if __name__ == "__main__":
    app.run(debug=True)
