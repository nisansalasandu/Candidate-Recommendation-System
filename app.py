from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import pandas as pd
import os
from datetime import datetime
from src.document_parser import DocumentParser
from src.recommendation_pipeline import CandidateRecommendationPipeline

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt', 'csv'}

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize parsers
document_parser = DocumentParser()

# Initialize recommendation pipeline
try:
    pipeline = CandidateRecommendationPipeline(vectorizer_path='models/vectorizer.pkl')
    print("✓ Recommendation pipeline initialized")
except Exception as e:
    print(f"✗ Pipeline initialization error: {str(e)}")
    pipeline = None

# Global storage
cvs_data = []
jobs_data = []


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'pipeline_loaded': pipeline is not None,
        'supported_formats': ['pdf', 'docx', 'txt', 'csv']
    })


@app.route('/api/upload-cv-file', methods=['POST'])
def upload_cv_file():
    """
    Upload CV as document file (PDF, DOCX, TXT)
    Extracts text automatically
    """
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file format. Use PDF, DOCX, or TXT'}), 400
        
        # Get form data
        candidate_id = request.form.get('candidate_id')
        name = request.form.get('name', 'Unknown')
        
        if not candidate_id:
            return jsonify({'error': 'Candidate ID is required'}), 400
        
        # Save file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{candidate_id}_{timestamp}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        
        # Parse document
        try:
            extracted_text = document_parser.parse_file(file_path)
            sections = document_parser.extract_sections(extracted_text)
        except Exception as e:
            os.remove(file_path)  # Clean up
            return jsonify({'error': f'Failed to parse document: {str(e)}'}), 500
        
        # Create CV entry
        cv_entry = {
            'candidate_id': candidate_id,
            'name': name,
            'skills': sections.get('skills', ''),
            'experience': sections.get('experience', ''),
            'education': sections.get('education', ''),
            'cv_text': sections.get('full_text', ''),
            'filename': filename,
            'upload_path': file_path,
            'timestamp': datetime.now().isoformat()
        }
        
        # Process with pipeline
        if pipeline:
            combined_text = f"{cv_entry['skills']} {cv_entry['experience']} {cv_entry['education']} {cv_entry['cv_text']}"
            cv_entry['cleaned_text'] = pipeline.clean_text(combined_text)
        
        # Store
        cvs_data.append(cv_entry)
        
        return jsonify({
            'success': True,
            'message': 'CV uploaded and processed successfully',
            'candidate_id': candidate_id,
            'extracted_sections': {
                'skills': sections.get('skills', 'Not detected')[:200],
                'experience': sections.get('experience', 'Not detected')[:200],
                'education': sections.get('education', 'Not detected')[:200]
            },
            'text_length': len(extracted_text),
            'total_cvs': len(cvs_data)
        }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/upload-job-file', methods=['POST'])
def upload_job_file():
    """
    Upload Job Description as document file (PDF, DOCX, TXT)
    Extracts text automatically
    """
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file format. Use PDF, DOCX, or TXT'}), 400
        
        # Get form data
        job_id = request.form.get('job_id')
        title = request.form.get('title', 'Unknown Position')
        
        if not job_id:
            return jsonify({'error': 'Job ID is required'}), 400
        
        # Save file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{job_id}_{timestamp}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        
        # Parse document
        try:
            extracted_text = document_parser.parse_file(file_path)
            sections = document_parser.extract_sections(extracted_text)
        except Exception as e:
            os.remove(file_path)  # Clean up
            return jsonify({'error': f'Failed to parse document: {str(e)}'}), 500
        
        # Create job entry
        job_entry = {
            'job_id': job_id,
            'title': title,
            'required_skills': sections.get('skills', ''),
            'experience_required': sections.get('experience', ''),
            'education_required': sections.get('education', ''),
            'job_description': sections.get('full_text', ''),
            'filename': filename,
            'upload_path': file_path,
            'timestamp': datetime.now().isoformat()
        }
        
        # Process with pipeline
        if pipeline:
            combined_text = f"{job_entry['required_skills']} {job_entry['experience_required']} {job_entry['education_required']} {job_entry['job_description']}"
            job_entry['cleaned_text'] = pipeline.clean_text(combined_text)
        
        # Store
        jobs_data.append(job_entry)
        
        return jsonify({
            'success': True,
            'message': 'Job description uploaded and processed successfully',
            'job_id': job_id,
            'extracted_sections': {
                'skills': sections.get('skills', 'Not detected')[:200],
                'experience': sections.get('experience', 'Not detected')[:200],
                'education': sections.get('education', 'Not detected')[:200]
            },
            'text_length': len(extracted_text),
            'total_jobs': len(jobs_data)
        }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/recommend', methods=['POST'])
def recommend():
    """Generate recommendations"""
    try:
        data = request.json
        job_id = data.get('job_id', None)
        top_n = data.get('top_n', 5)
        
        if len(cvs_data) == 0:
            return jsonify({'error': 'No CVs uploaded yet'}), 400
        
        if len(jobs_data) == 0:
            return jsonify({'error': 'No jobs uploaded yet'}), 400
        
        if not pipeline:
            return jsonify({'error': 'Pipeline not initialized'}), 500
        
        # Convert to DataFrames
        cvs_df = pd.DataFrame(cvs_data)
        jobs_df = pd.DataFrame(jobs_data)
        
        # Filter for specific job if requested
        if job_id:
            jobs_df = jobs_df[jobs_df['job_id'] == job_id]
            if len(jobs_df) == 0:
                return jsonify({'error': f'Job ID {job_id} not found'}), 404
        
        # Get recommendations
        recommendations_df = pipeline.batch_recommend(jobs_df, cvs_df, top_n=top_n)
        
        return jsonify({
            'success': True,
            'recommendations': recommendations_df.to_dict('records'),
            'total_candidates': len(cvs_data),
            'total_jobs': len(jobs_df),
            'timestamp': datetime.now().isoformat()
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/cvs', methods=['GET'])
def get_cvs():
    """Get all uploaded CVs"""
    return jsonify({
        'cvs': cvs_data,
        'total': len(cvs_data)
    }), 200


@app.route('/api/jobs', methods=['GET'])
def get_jobs():
    """Get all uploaded jobs"""
    return jsonify({
        'jobs': jobs_data,
        'total': len(jobs_data)
    }), 200


@app.route('/api/clear', methods=['POST'])
def clear_data():
    """Clear all data and uploaded files"""
    global cvs_data, jobs_data
    
    # Delete uploaded files
    for cv in cvs_data:
        if 'upload_path' in cv and os.path.exists(cv['upload_path']):
            try:
                os.remove(cv['upload_path'])
            except:
                pass
    
    for job in jobs_data:
        if 'upload_path' in job and os.path.exists(job['upload_path']):
            try:
                os.remove(job['upload_path'])
            except:
                pass
    
    cvs_data = []
    jobs_data = []
    
    return jsonify({'message': 'All data cleared successfully'}), 200


if __name__ == '__main__':
    print("\n" + "="*70)
    print("   🚀 Enhanced Candidate Recommendation System")
    print("="*70)
    print("\n📁 Supported Formats: PDF, DOCX, TXT, CSV")
    print("🔍 Automatic text extraction and section detection")
    print("\nEndpoints:")
    print("  GET  /                       - Web interface")
    print("  GET  /api/health             - Health check")
    print("  POST /api/upload-cv-file     - Upload CV document")
    print("  POST /api/upload-job-file    - Upload job document")
    print("  POST /api/recommend          - Get recommendations")
    print("  GET  /api/cvs                - List all CVs")
    print("  GET  /api/jobs               - List all jobs")
    print("  POST /api/clear              - Clear all data")
    print("\n" + "="*70)
    print(f"\n🌐 Server starting at: http://localhost:5000\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)