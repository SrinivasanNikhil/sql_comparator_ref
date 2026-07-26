from flask import render_template, request, jsonify, current_app, session, g
from flask_login import login_required
from werkzeug.utils import secure_filename
import os
import json
from app.comparator import bp
from app.comparator.services import SQLComparator
#from flask import current_app


@bp.route('/')
@login_required
def index():
    return render_template('comparator/index.html')

@bp.route('/get_modules', methods=['GET'])
@login_required
def get_modules():
    try:
        # Get the selected database from query parameter or session
        selected_db = request.args.get('database') or session.get('current_database', 'ClassicModels')
        reference_dir = current_app.config['REFERENCE_FILES_DIR']
        modules = []
        
        # List all JSON files in the reference directory
        for filename in os.listdir(reference_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(reference_dir, filename)
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                        # Only include files that match the selected database
                        if data.get('database', 'ClassicModels') == selected_db:
                            modules.append({
                                'filename': filename,
                                'title': data.get('title', filename)
                            })
                except Exception as e:
                    current_app.logger.error(f"Error reading file {filename}: {str(e)}")
                    continue
        
        return jsonify({'modules': modules})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


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
        questions_path = os.path.join(current_app.root_path, 'reference_files', module_name)
        if not os.path.abspath(os.path.realpath(questions_path)).startswith(os.getcwd()): # import os
            raise RuntimeError('Filepath falls outside the base directory')
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
    try:
        selected_db = request.args.get('database') or session.get('current_database', 'ClassicModels')
        questions_dir = current_app.config['REFERENCE_FILES_DIR']
        module_list = []
        
        for filename in os.listdir(questions_dir):
            if filename.endswith('.json'):
                try:
                    with open(os.path.join(questions_dir, filename), 'r') as f:
                        data = json.load(f)
                        # Only include files that match the selected database
                        if data.get('database', 'ClassicModels') == selected_db:
                            module_list.append({
                                'filename': filename,
                                'title': data.get('title', filename)
                            })
                except Exception as e:
                    current_app.logger.error(f"Error reading module {filename}: {e}")
                    continue
                    
        return jsonify({'modules': module_list})
    except Exception as e:
        current_app.logger.error(f"Error listing modules: {e}")
        return jsonify({'error': str(e)}), 500


@bp.route('/get_module_questions/<module_name>')
@login_required
def get_module_questions(module_name):
    try:
        questions_path = os.path.join(current_app.config['REFERENCE_FILES_DIR'], module_name)
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

@bp.route('/switch_database/<database>', methods=['POST'])
@login_required
def switch_database(database):
    try:
        if database not in current_app.config['AVAILABLE_DATABASES']:
            return jsonify({
                'success': False,
                'error': f'Invalid database selection: {database}'
            }), 400

        # Get the actual database name from the mapping
        db_name = current_app.config['AVAILABLE_DATABASES'][database]
        
        # Update the application configuration
        current_app.config['DB_CONFIG'] = current_app.config['DB_CONFIG'].copy()
        current_app.config['DB_CONFIG']['database'] = db_name
        
        # Store in session and force it to persist
        session['current_database'] = database
        session.modified = True  # Force the session to be saved
        
        # Force reconnection to the new database
        if hasattr(g, 'db'):
            delattr(g, 'db')
        
        return jsonify({
            'success': True, 
            'database': database,
            'message': f'Successfully switched to {database} database'
        })
    except Exception as e:
        current_app.logger.error(f"Error switching database: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error switching database: {str(e)}'
        }), 500
