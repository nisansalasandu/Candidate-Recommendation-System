from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import pandas as pd
import os
from datetime import datetime
from src.document_parser import DocumentParser
from src.recommendation_pipeline import CandidateRecommendationPipeline
import uuid

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max for multiple files
app.config['UPLOAD_FOLDER'] = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}

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
        'supported_formats': ['pdf', 'docx', 'txt']
    })


@app.route('/api/upload-cvs-bulk', methods=['POST'])
def upload_cvs_bulk():
    """
    Upload multiple CV files at once
    Automatically generates IDs and extracts names from filenames
    """
    try:
        if 'files[]' not in request.files:
            return jsonify({'error': 'No files provided'}), 400
        
        files = request.files.getlist('files[]')
        
        if not files or len(files) == 0:
            return jsonify({'error': 'No files selected'}), 400
        
        successful_uploads = []
        failed_uploads = []
        
        for file in files:
            if file.filename == '':
                continue
                
            if not allowed_file(file.filename):
                failed_uploads.append({
                    'filename': file.filename,
                    'error': 'Invalid file format'
                })
                continue
            
            try:
                # Generate unique ID
                candidate_id = str(uuid.uuid4())[:8]
                
                # Extract name from filename (remove extension)
                name = os.path.splitext(file.filename)[0]
                
                # Save file
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                unique_filename = f"cv_{candidate_id}_{timestamp}_{filename}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(file_path)
                
                # Parse document
                extracted_text = document_parser.parse_file(file_path)
                sections = document_parser.extract_sections(extracted_text)
                
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
                
                successful_uploads.append({
                    'filename': filename,
                    'candidate_id': candidate_id,
                    'name': name,
                    'text_length': len(extracted_text)
                })
                
            except Exception as e:
                failed_uploads.append({
                    'filename': file.filename,
                    'error': str(e)
                })
                if os.path.exists(file_path):
                    os.remove(file_path)
        
        return jsonify({
            'success': True,
            'message': f'Processed {len(successful_uploads)} CVs successfully',
            'successful': successful_uploads,
            'failed': failed_uploads,
            'total_cvs': len(cvs_data)
        }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/upload-job-file', methods=['POST'])
def upload_job_file():
    """
    Upload Job Description as document file (PDF, DOCX, TXT)
    """
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file format. Use PDF, DOCX, or TXT'}), 400
        
        # Generate unique ID
        job_id = str(uuid.uuid4())[:8]
        
        # Extract title from filename
        title = os.path.splitext(file.filename)[0]
        
        # Save file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"job_{job_id}_{timestamp}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        
        # Parse document
        try:
            extracted_text = document_parser.parse_file(file_path)
            sections = document_parser.extract_sections(extracted_text)
        except Exception as e:
            os.remove(file_path)
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
            'timestamp': datetime.now().isoformat(),
            'source': 'file'
        }
        
        # Process with pipeline
        if pipeline:
            combined_text = f"{job_entry['required_skills']} {job_entry['experience_required']} {job_entry['education_required']} {job_entry['job_description']}"
            job_entry['cleaned_text'] = pipeline.clean_text(combined_text)
        
        # Store
        jobs_data.append(job_entry)
        
        return jsonify({
            'success': True,
            'message': 'Job description uploaded successfully',
            'job_id': job_id,
            'title': title,
            'text_length': len(extracted_text),
            'total_jobs': len(jobs_data)
        }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/add-job-text', methods=['POST'])
def add_job_text():
    """
    Add Job Description as plain text
    """
    try:
        data = request.json
        job_text = data.get('job_description', '').strip()
        title = data.get('title', 'Untitled Position').strip()
        
        if not job_text:
            return jsonify({'error': 'Job description text is required'}), 400
        
        # Generate unique ID
        job_id = str(uuid.uuid4())[:8]
        
        # Extract sections from text
        sections = document_parser.extract_sections(job_text)
        
        # Create job entry
        job_entry = {
            'job_id': job_id,
            'title': title,
            'required_skills': sections.get('skills', ''),
            'experience_required': sections.get('experience', ''),
            'education_required': sections.get('education', ''),
            'job_description': job_text,
            'filename': None,
            'upload_path': None,
            'timestamp': datetime.now().isoformat(),
            'source': 'text'
        }
        
        # Process with pipeline
        if pipeline:
            combined_text = f"{job_entry['required_skills']} {job_entry['experience_required']} {job_entry['education_required']} {job_entry['job_description']}"
            job_entry['cleaned_text'] = pipeline.clean_text(combined_text)
        
        # Store
        jobs_data.append(job_entry)
        
        return jsonify({
            'success': True,
            'message': 'Job description added successfully',
            'job_id': job_id,
            'title': title,
            'text_length': len(job_text),
            'total_jobs': len(jobs_data)
        }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/recommend', methods=['POST'])
def recommend():
    """Generate ranked recommendations with summarization"""
    try:
        data = request.json
        job_id = data.get('job_id', None)
        
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
        
        # Get all recommendations (rank all CVs for each job)
        recommendations_df = pipeline.batch_recommend(jobs_df, cvs_df, top_n=len(cvs_df))
        
        # Group recommendations by job and format response
        job_recommendations = []
        
        for _, job in jobs_df.iterrows():
            # Get recommendations for this job
            job_recs = recommendations_df[recommendations_df['job_id'] == job['job_id']]
            
            # Sort by similarity score (already ranked by batch_recommend)
            job_recs = job_recs.sort_values('similarity_score', ascending=False).reset_index(drop=True)
            
            # Generate summary for each candidate
            candidates_list = []
            for idx, row in job_recs.iterrows():
                # Find the CV data
                cv = next((c for c in cvs_data if c['candidate_id'] == row['candidate_id']), None)
                
                # Get candidate name from CV data
                candidate_name = cv['name'] if cv else 'Unknown'
                
                summary = generate_candidate_summary(cv, row['similarity_score'])
                
                candidates_list.append({
                    'rank': idx + 1,
                    'candidate_id': row['candidate_id'],
                    'name': candidate_name,
                    'similarity_score': round(row['similarity_score'], 4),
                    'match_percentage': round(row['similarity_score'] * 100, 2),
                    'summary': summary,
                    'skills': cv['skills'][:300] if cv else '',
                    'experience': cv['experience'][:300] if cv else '',
                    'education': cv['education'][:200] if cv else ''
                })
            
            job_recommendations.append({
                'job_id': job['job_id'],
                'job_title': job['title'],
                'candidates': candidates_list,
                'total_matches': len(candidates_list)
            })
        
        return jsonify({
            'success': True,
            'jobs': job_recommendations,
            'total_jobs': len(jobs_df),
            'total_candidates': len(cvs_data),
            'timestamp': datetime.now().isoformat()
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def generate_candidate_summary(cv, score):
    """Generate a brief summary of candidate suitability"""
    if not cv:
        return "No candidate data available"
    
    match_level = "Excellent" if score > 0.7 else "Good" if score > 0.5 else "Moderate" if score > 0.3 else "Low"
    
    skills_preview = cv['skills'][:100].strip() if cv['skills'] else "No skills data"
    exp_preview = cv['experience'][:100].strip() if cv['experience'] else "No experience data"
    
    summary = f"{match_level} match. "
    
    if skills_preview != "No skills data":
        summary += f"Key skills: {skills_preview}... "
    
    if exp_preview != "No experience data":
        summary += f"Experience: {exp_preview}..."
    
    return summary


@app.route('/api/cvs', methods=['GET'])
def get_cvs():
    """Get all uploaded CVs"""
    cv_list = [{
        'candidate_id': cv['candidate_id'],
        'name': cv['name'],
        'filename': cv['filename'],
        'timestamp': cv['timestamp']
    } for cv in cvs_data]
    
    return jsonify({
        'cvs': cv_list,
        'total': len(cvs_data)
    }), 200


@app.route('/api/jobs', methods=['GET'])
def get_jobs():
    """Get all uploaded jobs"""
    job_list = [{
        'job_id': job['job_id'],
        'title': job['title'],
        'source': job.get('source', 'file'),
        'timestamp': job['timestamp']
    } for job in jobs_data]
    
    return jsonify({
        'jobs': job_list,
        'total': len(jobs_data)
    }), 200


@app.route('/api/clear', methods=['POST'])
def clear_data():
    """Clear all data and uploaded files"""
    global cvs_data, jobs_data
    
    # Delete uploaded files
    for cv in cvs_data:
        if 'upload_path' in cv and cv['upload_path'] and os.path.exists(cv['upload_path']):
            try:
                os.remove(cv['upload_path'])
            except:
                pass
    
    for job in jobs_data:
        if 'upload_path' in job and job['upload_path'] and os.path.exists(job['upload_path']):
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
    print("\n📄 Supported Formats: PDF, DOCX, TXT")
    print("📊 Bulk CV upload with automatic ranking")
    print("✍️  Text input for job descriptions")
    print("\nEndpoints:")
    print("  GET  /                       - Web interface")
    print("  GET  /api/health             - Health check")
    print("  POST /api/upload-cvs-bulk    - Upload multiple CVs")
    print("  POST /api/upload-job-file    - Upload job document")
    print("  POST /api/add-job-text       - Add job as text")
    print("  POST /api/recommend          - Get ranked recommendations")
    print("  GET  /api/cvs                - List all CVs")
    print("  GET  /api/jobs               - List all jobs")
    print("  POST /api/clear              - Clear all data")
    print("\n" + "="*70)
    print(f"\n🌐 Server starting at: http://localhost:5000\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)