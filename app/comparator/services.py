from typing import Dict, List
from flask import current_app
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

        return {
            'columns': {
                'user': user_columns,
                'reference': reference_columns,
                'match': set(user_columns) == set(reference_columns)
            },
            'record_counts': {
                'user': len(user_results),
                'reference': len(reference_results)
            },
            'exact_match': user_results == reference_results
        }
