from shadow_ai.scoring import ConfidenceScorer

print("=== High AI patterns test ===")
high_ai_results = {
    'comment_patterns': {'generic_comments': 15, 'comment_to_code_ratio': 0.9, 'repetitive_patterns': 8},
    'variable_names': {'generic_percentage': 85.0},
    'code_structure': {'structural_uniformity_score': 90.0, 'function_length_variance': 0.5, 'total_functions': 5},
    'ai_language_patterns': {'ai_phrase_count': 10, 'conversational_indicators': 5, 'disclaimer_patterns': 3}
}

result = ConfidenceScorer.calculate_confidence_score(high_ai_results)
print(f"Score: {result['confidence_score']}%")
print(f"Components: {result['component_scores']}")

print("\n=== Medium AI patterns test ===")
medium_results = {
    'comment_patterns': {'generic_comments': 5, 'comment_to_code_ratio': 0.6, 'repetitive_patterns': 2},
    'variable_names': {'generic_percentage': 60.0},
    'code_structure': {'structural_uniformity_score': 50.0, 'function_length_variance': 2.0, 'total_functions': 3},
    'ai_language_patterns': {'ai_phrase_count': 2, 'conversational_indicators': 1, 'disclaimer_patterns': 0}
}

result2 = ConfidenceScorer.calculate_confidence_score(medium_results)
print(f"Score: {result2['confidence_score']}%")
print(f"Components: {result2['component_scores']}")

print(f"\nMax possible score: {result['max_possible_score']}")
print(f"Weights: {ConfidenceScorer.get_heuristic_weights()}")
