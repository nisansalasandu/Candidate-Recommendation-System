# Quick Start Guide - Candidate Recommendation System

## 🚀 Getting Started (5 Minutes)

### 1. Start the Server
```bash
cd "c:\Users\DELL\Desktop\new project\Candidate-Recommendation-System"
python app.py
```

### 2. Open Browser
Go to: **http://localhost:5000**

---

## 💡 Quick Test Example

### Method 1: Manual Input (Fastest)

1. **Job Description**:
   - Required Skills: `Python, Machine Learning, TensorFlow, Data Science`
   - Experience: `3+ years in software development`
   - Education: `Bachelor in Computer Science`
   - Job Description: `Looking for a data scientist with strong Python skills and ML experience`

2. **Add Candidate 1**:
   - Candidate ID: `C001`
   - Skills: `Python, TensorFlow, Keras, Machine Learning, Data Analysis`
   - Experience: `4 years as Data Scientist at Tech Corp`
   - Education: `MS in Computer Science`
   - CV Text: `Experienced in building ML models, data pipelines, and deploying production systems`

3. **Add Candidate 2**:
   - Candidate ID: `C002`
   - Skills: `Java, Spring Boot, Microservices, REST API`
   - Experience: `2 years as Backend Developer`
   - Education: `BS in Software Engineering`
   - CV Text: `Backend developer with Java expertise and cloud deployment experience`

4. **Add Candidate 3**:
   - Candidate ID: `C003`
   - Skills: `Python, Scikit-learn, Pandas, NumPy, Machine Learning`
   - Experience: `5 years as ML Engineer, worked on recommendation systems`
   - Education: `PhD in Artificial Intelligence`
   - CV Text: `Published researcher in ML, expert in recommendation algorithms and neural networks`

5. Click **"Get Recommendations"**

**Expected Result**: C003 ranks #1 (highest match), C001 ranks #2, C002 ranks #3 (lowest match for this ML job)

---

## 📁 CSV File Format Examples

### candidates.csv
```csv
candidate_id,skills,experience,education,cv_text
C001,"Python, TensorFlow, ML","4 years Data Scientist","MS Computer Science","ML models expert"
C002,"Java, Spring Boot","2 years Backend Dev","BS Software Eng","Java backend developer"
C003,"Python, Scikit-learn","5 years ML Engineer","PhD AI","Research in ML algorithms"
```

### jobs.csv
```csv
job_id,required_skills,experience_required,education_required,job_description
J001,"Python, ML, Data Science","3+ years","Bachelor CS","Data Scientist position with ML focus"
J002,"Java, Microservices","2+ years","Bachelor","Backend Java Developer needed"
```

---

## 🔑 Key Features to Try

### 1. Real-Time Scoring
Watch how different skill combinations affect match percentages

### 2. Batch Processing
Upload the sample CSV files from `data/` folder:
- `cvs_100.csv` - 100 candidates
- `jobs_10.csv` - 10 job descriptions

### 3. Export Results
Download recommendations as CSV for further analysis

### 4. Visual Ranking
- 🥇 Gold badge = Best match
- 🥈 Silver badge = Second best
- 🥉 Bronze badge = Third best

---

## 📊 Understanding Results

### Match Percentage Guide
- **90-100%**: Perfect or near-perfect match
- **70-89%**: Excellent match
- **50-69%**: Good match, suitable candidate
- **30-49%**: Moderate match, some skills align
- **0-29%**: Weak match, different skill set

### Cosine Similarity Score
- Raw score between 0 and 1
- Used for precise ranking
- 1.0 = identical skill profiles
- 0.0 = no common skills

---

## 🎯 API Testing with cURL

### Test Health Endpoint
```bash
curl http://localhost:5000/api/health
```

### Test Recommendation
```bash
curl -X POST http://localhost:5000/api/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "job": {
      "required_skills": "Python, ML",
      "job_description": "Data Scientist needed"
    },
    "candidates": [
      {
        "candidate_id": "C001",
        "skills": "Python, TensorFlow, ML",
        "cv_text": "ML expert with 5 years experience"
      }
    ],
    "top_n": 5
  }'
```

---

## 🐛 Common Issues

### Server won't start
```bash
# Check if port 5000 is already in use
netstat -ano | findstr :5000

# Kill the process if needed
taskkill /PID <process_id> /F
```

### NLTK errors
```bash
# Download all NLTK data
python -c "import nltk; nltk.download('all')"
```

### Models not found
```bash
# Train models first
cd src
python preprocessing.py
python vectorization.py
cd ..
python app.py
```

---

## 🎨 UI Tips

- **Switch Tabs**: Click on Manual Input / File Upload / Batch Process
- **Add/Remove Candidates**: Use + and X buttons
- **Scroll to Results**: Auto-scrolls after processing
- **Export**: Click "Export Results" button to download CSV

---

## 📱 Mobile Friendly

The interface is responsive and works on:
- Desktop computers
- Tablets
- Mobile phones

---

## 🔧 Configuration

### Change Port
Edit `app.py`:
```python
app.run(debug=True, port=5001)  # Change 5000 to 5001
```

### Increase File Size Limit
Edit `app.py`:
```python
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32MB
```

### Change Number of Features
Edit `src/vectorization.py`:
```python
vectorizer = TfidfVectorizer(max_features=10000)  # Increase from 5000
```

---

## 📚 Learn More

- **Full Documentation**: See `README_COMPLETE.md`
- **Code Examples**: Check `src/recommendation_pipeline.py`
- **Sample Data**: Look in `data/` folder
- **API Reference**: See API Endpoints section in README_COMPLETE.md

---

## 🎓 For Academic Submission

This system includes all required components:
1. ✅ Vector representations (TF-IDF)
2. ✅ Preprocessing pipeline
3. ✅ Similarity computation (Cosine)
4. ✅ Recommendation ranking
5. ✅ Evaluation metrics
6. ✅ Documentation
7. ✅ Working application

**Extra Features**:
- Full-stack web interface
- REST API
- Multiple input methods
- Export functionality
- Responsive design

---

**Need Help?** Check the terminal output for error messages and refer to the troubleshooting section.

**Ready to Deploy?** Consider using Gunicorn for production and Docker for containerization.

---

## 🏆 Success Checklist

- [ ] Server starts without errors
- [ ] Browser opens at http://localhost:5000
- [ ] Can add candidates manually
- [ ] Recommendations appear with scores
- [ ] Can upload CSV files
- [ ] Export button works
- [ ] All 3 tabs functional

---

**Happy Testing! 🚀**
