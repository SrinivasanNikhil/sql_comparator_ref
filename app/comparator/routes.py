from flask import render_template, request, jsonify, current_app
from flask_login import login_required
from werkzeug.utils import secure_filename
import os
import json
from app.comparator import bp
from app.comparator.services import SQLComparator

@bp.route('/')
@login_required
def index():
    return render_template('comparator/index.html')

@bp.route('/compare_files', methods=['POST'])
@login_required
def compare_files():
    try:
        # Get the reference file name
        reference_file = request.form['reference_file']
        
        # Get the uploaded file
        if 'user_file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['user_file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
            
        # Validate file
        if not file.filename.endswith('.json'):
            return jsonify({'error': 'File must be JSON format'}), 400
            
        # Parse uploaded JSON file
        try:
            user_file_content = json.loads(file.read())
        except json.JSONDecodeError:
            return jsonify({'error': 'Invalid JSON file'}), 400
            
        # Compare files
        comparison_results = SQLComparator.compare_files(reference_file, user_file_content)
        return jsonify(comparison_results)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/compare_single_query', methods=['POST'])
@login_required
def compare_single_query():
    module_name = request.form.get('module')
    question_number = request.form.get('questionNumber')
    user_query = request.form.get('query')
    
    if not all([module_name, question_number, user_query]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        # Load the questions file
        questions_path = os.path.join(current_app.root_path, 'questions', module_name)
        with open(questions_path, 'r') as f:
            questions_data = json.load(f)
        
        # Find the matching question
        question = next(
            (q for q in questions_data['questions'] 
             if str(q['number']) == str(question_number)),
            None
        )
        
        if not question:
            return jsonify({'error': 'Question not found'}), 404
        
        # Compare queries
        comparison_result = SQLComparator.compare_individual_queries(
            user_query, 
            question['solution_query']
        )
        
        return jsonify({
            'comparisons': [{
                'query_number': int(question_number),
                'question_text': question['text'],
                'user_query': user_query,
                'reference_query': question['solution_query'],
                **comparison_result
            }]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/get_question_modules')
@login_required
def get_question_modules():
    questions_dir = os.path.join(current_app.root_path, 'questions')
    try:
        modules = [f for f in os.listdir(questions_dir) 
                  if f.endswith('.json')]
        
        # Load module names for dropdown
        module_list = []
        for module in modules:
            try:
                with open(os.path.join(questions_dir, module), 'r') as f:
                    data = json.load(f)
                    # If file has a title, use it, otherwise use filename
                    title = data.get('title', module)
                    module_list.append({
                        'filename': module,
                        'title': title
                    })
            except:
                # If there's an error reading the file, just use the filename
                module_list.append({
                    'filename': module,
                    'title': module
                })
                
        return jsonify({'modules': module_list})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/get_module_questions/<module_name>')
@login_required
def get_module_questions(module_name):
    try:
        questions_path = os.path.join(current_app.root_path, 'questions', module_name)
        with open(questions_path, 'r') as f:
            questions_data = json.load(f)
        
        # Format questions for dropdown
        questions = [
            {
                'number': q['number'],
                'text': f"Question {q['number']}: {q['text']}"
            }
            for q in questions_data['questions']
        ]
        
        return jsonify({'questions': questions})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# @comparator_bp.route('/compare_files', methods=['POST'])
# @login_required
# def compare_files():
#     if 'userFile' not in request.files:
#         return jsonify({'error': 'User file is required'}), 400
    
#     user_file = request.files['userFile']
#     reference_filename = request.form.get('referenceFile')
    
#     if user_file.filename == '' or not reference_filename:
#         return jsonify({'error': 'Both files must be selected'}), 400
    
#     try:
#         user_queries = json.load(user_file)
        
#         reference_path = os.path.join(current_app.config['UPLOAD_FOLDER'], reference_filename)
#         with open(reference_path, 'r') as f:
#             reference_queries = json.load(f)
        
#         if not SQLComparator.validate_queries_json(user_queries) or \
#            not SQLComparator.validate_queries_json(reference_queries):
#             return jsonify({'error': 'Invalid file format'}), 400
        
#         comparison_results = SQLComparator.process_comparison(user_queries, reference_queries)
#         return jsonify({'comparisons': comparison_results})
        
#     except json.JSONDecodeError:
#         return jsonify({'error': 'Invalid JSON format'}), 400
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500
