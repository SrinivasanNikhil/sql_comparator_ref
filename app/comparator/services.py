from typing import Dict, List
from flask import current_app
import os
import json
from app.database import db

class SQLComparator:
    @staticmethod
    def compare_individual_queries(user_query: str, reference_query: str) -> Dict:
        """
        Compare a single user query against a reference query.
        Returns both query analysis and result comparison.
        """
        # Query text analysis
        query_analysis = SQLComparator._analyze_query_text(user_query, reference_query)
        
        try:
            # Execute queries and compare results
            user_results = db.execute_query(user_query)
            reference_results = db.execute_query(reference_query)
            
            result_comparison = SQLComparator._compare_results(user_results, reference_results)
            
            return {
                'query_analysis': query_analysis,
                'result_comparison': result_comparison,
                'status': 'success'
            }
            
        except Exception as e:
            return {
                'query_analysis': query_analysis,
                'result_comparison': None,
                'status': 'error',
                'error_message': str(e)
            }

    @staticmethod
    def compare_files(reference_file: str, user_file: Dict) -> Dict:
        """
        Compare JSON files containing SQL queries.
        Args:
            reference_file: Name of the reference file in questions directory
            user_file: Dict containing parsed JSON from uploaded file
        Returns:
            Dict containing comparison results and overall score
        """
        try:
            # Load reference file
            questions_path = os.path.join(current_app.root_path, 'reference_files', reference_file)
            with open(questions_path, 'r') as f:
                reference_data = json.load(f)

            results = []
            total_score = 0
            max_possible_score = 0

            # Compare each question's query
            for ref_q in reference_data['questions']:
                ref_num = ref_q['number']
                ref_query = ref_q['solution_query']
                
                # Find matching question in user file
                user_q = next((q for q in user_file['questions'] 
                             if q['number'] == ref_num), None)
                
                if user_q is None:
                    results.append({
                        'question_number': ref_num,
                        'status': 'missing',
                        'score': 0,
                        'max_score': 10
                    })
                    max_possible_score += 10
                    continue

                # Compare the queries
                comparison = SQLComparator.compare_individual_queries(
                    user_q['solution_query'], ref_query
                )
                
                #log the comparison
                current_app.logger.info(f"Comparison for question {ref_num}: {comparison}")
                
                # Calculate score based on query analysis and results
                score = SQLComparator._calculate_query_score(comparison)
                total_score += score['score']
                max_possible_score += score['max_score']
                
                results.append({
                    'question_number': ref_num,
                    'comparison': comparison,
                    'score': score['score'],
                    'max_score': score['max_score'],
                    'user_query': user_q['solution_query']
                })

            return {
                'results': results,
                'total_score': total_score,
                'max_possible_score': max_possible_score,
                'percentage': (total_score / max_possible_score * 100) if max_possible_score > 0 else 0
            }

        except Exception as e:
            return {'error': str(e)}

    @staticmethod
    def _calculate_query_score(comparison: Dict) -> Dict:
        """
        Calculate a score for a query comparison based on analysis and results.
        Args:
            comparison: Dict containing query_analysis and result_comparison
        Returns:
            Dict containing score and max possible score
        """
        max_score = 10
        score = max_score

        # Deduct points for missing or additional terms
        query_analysis = comparison['query_analysis']
        if query_analysis['missing_terms']:
            score -= len(query_analysis['missing_terms'])
        if query_analysis['additional_terms']:
            score -= len(query_analysis['additional_terms'])

        # Deduct points for result mismatches
        # if comparison['result_comparison']:
        #     result_comparison = comparison['result_comparison']
        #     if not result_comparison.get('columns_match', False):
        #         score -= 3
        #     if not result_comparison.get('row_count_match', False):
        #         score -= 3

        return {
            'score': max(0, score),  # Don't allow negative scores
            'max_score': max_score
        }

    @staticmethod
    def _analyze_query_text(user_query: str, reference_query: str) -> Dict:
        """
        Analyze the textual differences between queries.
        """
        # Normalize queries for comparison
        user_terms = set(SQLComparator._normalize_query(user_query))
        reference_terms = set(SQLComparator._normalize_query(reference_query))
        
        # Find differences
        missing_terms = reference_terms - user_terms
        additional_terms = user_terms - reference_terms
        
        return {
            'missing_terms': list(missing_terms),
            'additional_terms': list(additional_terms),
            'exact_match': user_terms == reference_terms
        }

    @staticmethod
    def _normalize_query(query: str) -> List[str]:
        """
        Normalize a SQL query for comparison.
        """
        normalized = query.lower()
        terms = normalized.split()
        return [term for term in terms if term not in {'select', 'from', 'where', 'and', 'or'}]


    @staticmethod
    def _compare_results(user_results: List[Dict], reference_results: List[Dict]) -> Dict:
        """
        Compare the results of two queries.
        """
        user_columns = list(user_results[0].keys()) if user_results else []
        reference_columns = list(reference_results[0].keys()) if reference_results else []

        #log the user columns and reference columns
        current_app.logger.info(f"User columns: {user_columns}")
        current_app.logger.info(f"Reference columns: {reference_columns}")
        
        # Sort results for consistent comparison
        user_results_sorted = sorted(user_results, key=lambda x: tuple(x.items()))
        reference_results_sorted = sorted(reference_results, key=lambda x: tuple(x.items()))

        return {
            'columns': {
                'user': user_columns,
                'reference': reference_columns,
                'match': set(user_columns) == set(reference_columns)
            },
            'record_counts': {
                'user': len(user_results_sorted),
                'reference': len(reference_results_sorted)
            },
            'exact_match': user_results_sorted == reference_results_sorted
        }
    
    # @staticmethod
    # def _compare_results(user_results: List[Dict], reference_results: List[Dict]) -> Dict:
    #     """
    #     Compare the results of two queries.
    #     """
    #     user_columns = list(user_results[0].keys()) if user_results else []
    #     reference_columns = list(reference_results[0].keys()) if reference_results else []

    #     return {
    #         'columns': {
    #             'user': user_columns,
    #             'reference': reference_columns,
    #             'match': set(user_columns) == set(reference_columns)
    #         },
    #         'record_counts': {
    #             'user': len(user_results),
    #             'reference': len(reference_results)
    #         },
    #         'exact_match': user_results == reference_results
    #     }
