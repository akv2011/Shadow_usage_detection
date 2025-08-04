

import pytest
from shadow_ai.scoring import ConfidenceScorer, calculate_confidence_score


class TestConfidenceScorer:


    def test_calculate_confidence_score_empty_results(self):

        empty_results = {
            'comment_patterns': {'generic_comments': 0, 'comment_to_code_ratio': 0.0, 'repetitive_patterns': 0},
            'variable_names': {'generic_percentage': 0.0},
            'code_structure': {'structural_uniformity_score': 0.0, 'function_length_variance': 10.0, 'total_functions': 1},
            'ai_language_patterns': {'ai_phrase_count': 0, 'conversational_indicators': 0, 'disclaimer_patterns': 0}
        }

        result = ConfidenceScorer.calculate_confidence_score(empty_results)

        assert result['confidence_score'] == 0.0
        assert result['risk_level'] == 'low'
        assert all(score == 0.0 for score in result['component_scores'].values())

    def test_calculate_confidence_score_high_ai_patterns(self):

        high_ai_results = {
            'comment_patterns': {'generic_comments': 15, 'comment_to_code_ratio': 0.9, 'repetitive_patterns': 8},
            'variable_names': {'generic_percentage': 85.0},
            'code_structure': {'structural_uniformity_score': 90.0, 'function_length_variance': 0.5, 'total_functions': 5},
            'ai_language_patterns': {'ai_phrase_count': 10, 'conversational_indicators': 5, 'disclaimer_patterns': 3}
        }

        result = ConfidenceScorer.calculate_confidence_score(high_ai_results)

        assert result['confidence_score'] >= 60.0
        assert result['risk_level'] == 'medium' or result['risk_level'] == 'high'
        assert result['component_scores']['comment_patterns'] > 15.0
        assert result['component_scores']['ai_language_patterns'] > 10.0

    def test_calculate_confidence_score_medium_patterns(self):

        medium_results = {
            'comment_patterns': {'generic_comments': 5, 'comment_to_code_ratio': 0.6, 'repetitive_patterns': 2},
            'variable_names': {'generic_percentage': 60.0},
            'code_structure': {'structural_uniformity_score': 50.0, 'function_length_variance': 2.0, 'total_functions': 3},
            'ai_language_patterns': {'ai_phrase_count': 2, 'conversational_indicators': 1, 'disclaimer_patterns': 0}
        }

        result = ConfidenceScorer.calculate_confidence_score(medium_results)

        assert 20.0 <= result['confidence_score'] < 50.0
        assert result['risk_level'] == 'low' or result['risk_level'] == 'medium'

    def test_calculate_confidence_score_low_patterns(self):

        low_results = {
            'comment_patterns': {'generic_comments': 1, 'comment_to_code_ratio': 0.2, 'repetitive_patterns': 0},
            'variable_names': {'generic_percentage': 20.0},
            'code_structure': {'structural_uniformity_score': 30.0, 'function_length_variance': 5.0, 'total_functions': 2},
            'ai_language_patterns': {'ai_phrase_count': 0, 'conversational_indicators': 0, 'disclaimer_patterns': 0}
        }

        result = ConfidenceScorer.calculate_confidence_score(low_results)

        assert result['confidence_score'] < 40.0
        assert result['risk_level'] == 'low'

    def test_risk_level_thresholds(self):

        thresholds = ConfidenceScorer.get_risk_level_thresholds()

        assert ConfidenceScorer._determine_risk_level(0.0) == 'low'
        assert ConfidenceScorer._determine_risk_level(39.9) == 'low'
        assert ConfidenceScorer._determine_risk_level(40.0) == 'medium'
        assert ConfidenceScorer._determine_risk_level(69.9) == 'medium'
        assert ConfidenceScorer._determine_risk_level(70.0) == 'high'
        assert ConfidenceScorer._determine_risk_level(100.0) == 'high'

    def test_comment_patterns_scoring(self):

        results = {'generic_comments': 10, 'comment_to_code_ratio': 0.8, 'repetitive_patterns': 5}

        score, factors = ConfidenceScorer._score_comment_patterns(results)

        assert score > 0
        assert 'generic_comments' in factors
        assert 'comment_to_code_ratio' in factors
        assert 'repetitive_patterns' in factors
        assert factors['generic_comments'] > 0

    def test_variable_names_scoring(self):

        results = {'generic_percentage': 75.0}

        score, factors = ConfidenceScorer._score_variable_names(results)

        assert score > 0
        assert 'generic_percentage' in factors
        assert factors['generic_percentage'] > 0

    def test_code_structure_scoring(self):

        results = {
            'structural_uniformity_score': 80.0,
            'function_length_variance': 1.0,
            'total_functions': 3
        }

        score, factors = ConfidenceScorer._score_code_structure(results)

        assert score > 0
        assert 'structural_uniformity' in factors
        assert 'function_length_variance' in factors
        assert factors['function_length_variance'] > 0

    def test_ai_language_patterns_scoring(self):

        results = {
            'ai_phrase_count': 5,
            'conversational_indicators': 3,
            'disclaimer_patterns': 2
        }

        score, factors = ConfidenceScorer._score_ai_language_patterns(results)

        assert score > 0
        assert 'ai_phrases' in factors
        assert 'conversational_indicators' in factors
        assert 'disclaimer_patterns' in factors
        assert all(factor > 0 for factor in factors.values())

    def test_infinite_comment_ratio_handling(self):

        results = {'generic_comments': 2, 'comment_to_code_ratio': float('inf'), 'repetitive_patterns': 1}

        score, factors = ConfidenceScorer._score_comment_patterns(results)

        assert score > 0
        assert not math.isinf(factors['comment_to_code_ratio'])
        assert factors['comment_to_code_ratio'] > 0

    def test_convenience_function(self):

        test_results = {
            'comment_patterns': {'generic_comments': 2, 'comment_to_code_ratio': 0.3, 'repetitive_patterns': 1},
            'variable_names': {'generic_percentage': 30.0},
            'code_structure': {'structural_uniformity_score': 40.0, 'function_length_variance': 3.0, 'total_functions': 2},
            'ai_language_patterns': {'ai_phrase_count': 1, 'conversational_indicators': 0, 'disclaimer_patterns': 0}
        }

        result = calculate_confidence_score(test_results)

        assert 'confidence_score' in result
        assert 'risk_level' in result
        assert 'component_scores' in result
        assert result['confidence_score'] >= 0.0
        assert result['confidence_score'] <= 100.0

    def test_score_normalization(self):

        extreme_results = {
            'comment_patterns': {'generic_comments': 1000, 'comment_to_code_ratio': 10.0, 'repetitive_patterns': 100},
            'variable_names': {'generic_percentage': 100.0},
            'code_structure': {'structural_uniformity_score': 100.0, 'function_length_variance': 0.0, 'total_functions': 10},
            'ai_language_patterns': {'ai_phrase_count': 100, 'conversational_indicators': 50, 'disclaimer_patterns': 20}
        }

        result = ConfidenceScorer.calculate_confidence_score(extreme_results)

        assert result['confidence_score'] <= 100.0
        assert result['confidence_score'] >= 90.0


import math


if __name__ == '__main__':
    print("Running quick confidence scoring test...")

    test_results = {
        'comment_patterns': {'generic_comments': 5, 'comment_to_code_ratio': 0.7, 'repetitive_patterns': 3},
        'variable_names': {'generic_percentage': 60.0},
        'code_structure': {'structural_uniformity_score': 70.0, 'function_length_variance': 1.5, 'total_functions': 4},
        'ai_language_patterns': {'ai_phrase_count': 2, 'conversational_indicators': 1, 'disclaimer_patterns': 1}
    }

    result = calculate_confidence_score(test_results)
    print(f"Test score: {result['confidence_score']}%")
    print(f"Risk level: {result['risk_level']}")
    print("Test completed successfully!")
