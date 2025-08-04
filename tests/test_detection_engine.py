

import pytest
from shadow_ai.engine import analyze_comment_patterns, analyze_variable_names, analyze_code_structure, match_ai_language_patterns, analyze


class TestCommentPatternAnalysis:


    def test_analyze_comment_patterns_with_generic_comments(self):

        code_with_generic_comments = 

        result = analyze_comment_patterns(code_with_generic_comments)

        assert result['generic_comments'] >= 4
        assert result['total_comments'] == 5
        assert result['comment_to_code_ratio'] > 0.5

    def test_analyze_comment_patterns_with_human_comments(self):

        code_with_human_comments = 

        result = analyze_comment_patterns(code_with_human_comments)

        assert result['generic_comments'] == 0
        assert result['total_comments'] == 2
        assert result['comment_to_code_ratio'] < 0.5

    def test_analyze_comment_patterns_with_repetitive_patterns(self):

        code_with_repetitive_comments = 

        result = analyze_comment_patterns(code_with_repetitive_comments)

        assert result['repetitive_patterns'] >= 4
        assert result['generic_comments'] >= 3
        assert result['total_comments'] == 4

    def test_analyze_comment_patterns_empty_input(self):

        result = analyze_comment_patterns("")

        assert result['generic_comments'] == 0
        assert result['comment_to_code_ratio'] == 0.0
        assert result['repetitive_patterns'] == 0
        assert result['total_comments'] == 0

    def test_analyze_comment_patterns_none_input(self):

        result = analyze_comment_patterns(None)

        assert result['generic_comments'] == 0
        assert result['comment_to_code_ratio'] == 0.0
        assert result['repetitive_patterns'] == 0
        assert result['total_comments'] == 0

    def test_analyze_comment_patterns_no_comments(self):

        code_without_comments = 

        result = analyze_comment_patterns(code_without_comments)

        assert result['generic_comments'] == 0
        assert result['comment_to_code_ratio'] == 0.0
        assert result['repetitive_patterns'] == 0
        assert result['total_comments'] == 0

    def test_analyze_comment_patterns_only_comments(self):

        only_comments = 

        result = analyze_comment_patterns(only_comments)

        assert result['total_comments'] == 3
        assert result['comment_to_code_ratio'] == float('inf')

    def test_analyze_comment_patterns_mixed_content(self):

        mixed_code = 

        result = analyze_comment_patterns(mixed_code)

        assert result['generic_comments'] >= 1
        assert result['generic_comments'] < result['total_comments']
        assert 0 < result['comment_to_code_ratio'] < 1


class TestVariableNamingAnalysis:


    def test_analyze_variable_names_with_generic_names(self):

        code_with_generic_names = 

        result = analyze_variable_names(code_with_generic_names)

        assert result['generic_names_count'] >= 7
        assert result['generic_percentage'] > 50
        assert 'data' in result['generic_names_found']
        assert 'result' in result['generic_names_found']
        assert 'temp' in result['generic_names_found']

    def test_analyze_variable_names_with_descriptive_names(self):

        code_with_descriptive_names = 

        result = analyze_variable_names(code_with_descriptive_names)

        assert result['generic_percentage'] < 20
        assert result['total_names_count'] > 0

    def test_analyze_variable_names_mixed_names(self):

        code_with_mixed_names = 

        result = analyze_variable_names(code_with_mixed_names)

        assert 10 <= result['generic_percentage'] <= 60
        assert result['generic_names_count'] > 0
        assert result['total_names_count'] > result['generic_names_count']

    def test_analyze_variable_names_empty_input(self):

        result = analyze_variable_names("")

        assert result['generic_names_count'] == 0
        assert result['total_names_count'] == 0
        assert result['generic_percentage'] == 0.0
        assert result['generic_names_found'] == []

    def test_analyze_variable_names_none_input(self):

        result = analyze_variable_names(None)

        assert result['generic_names_count'] == 0
        assert result['total_names_count'] == 0
        assert result['generic_percentage'] == 0.0
        assert result['generic_names_found'] == []

    def test_analyze_variable_names_syntax_error(self):

        code_with_syntax_error = 

        result = analyze_variable_names(code_with_syntax_error)

        assert result['generic_names_count'] == 0
        assert result['total_names_count'] == 0
        assert result['generic_percentage'] == 0.0

    def test_analyze_variable_names_single_letter_variables(self):

        code_with_single_letters = 

        result = analyze_variable_names(code_with_single_letters)

        assert result['generic_names_count'] >= 6
        assert 'i' in result['generic_names_found']
        assert 'j' in result['generic_names_found']
        assert 'k' in result['generic_names_found']
        assert 'x' in result['generic_names_found']
        assert 'y' in result['generic_names_found']
        assert 'z' in result['generic_names_found']

    def test_analyze_variable_names_builtin_filtering(self):

        code_with_builtins = 

        result = analyze_variable_names(code_with_builtins)

        assert 'len' not in result['generic_names_found']
        assert 'print' not in result['generic_names_found']
        assert 'str' not in result['generic_names_found']
        assert 'result' in result['generic_names_found']
        assert 'item' in result['generic_names_found']


class TestCodeStructureAnalysis:


    def test_analyze_code_structure_uniform_functions(self):

        code_with_uniform_functions = 

        result = analyze_code_structure(code_with_uniform_functions)

        assert result['total_functions'] == 4
        assert result['function_length_variance'] < 2.0
        assert result['structural_uniformity_score'] > 50
        assert result['average_nesting_depth'] <= 1.0

    def test_analyze_code_structure_complex_varied_code(self):

        code_with_varied_structure = 

        result = analyze_code_structure(code_with_varied_structure)

        assert result['total_functions'] == 4
        assert result['function_length_variance'] > 3.0
        assert result['structural_uniformity_score'] < 40
        assert result['node_type_diversity'] > 15

    def test_analyze_code_structure_simple_repetitive(self):

        code_with_simple_patterns = 

        result = analyze_code_structure(code_with_simple_patterns)

        assert result['total_functions'] == 5
        assert result['function_length_variance'] == 0.0
        assert result['structural_uniformity_score'] > 70
        assert result['average_nesting_depth'] == 0.0
        assert result['control_flow_complexity'] == 0.0

    def test_analyze_code_structure_complex_nesting(self):

        code_with_complex_nesting = 

        result = analyze_code_structure(code_with_complex_nesting)

        assert result['total_functions'] == 2
        assert result['average_nesting_depth'] > 3.0
        assert result['control_flow_complexity'] > 5.0
        assert result['node_type_diversity'] > 20

    def test_analyze_code_structure_empty_input(self):

        result = analyze_code_structure("")

        assert result['function_length_variance'] == 0.0
        assert result['average_nesting_depth'] == 0.0
        assert result['node_type_diversity'] == 0
        assert result['control_flow_complexity'] == 0.0
        assert result['structural_uniformity_score'] == 0.0
        assert result['total_functions'] == 0

    def test_analyze_code_structure_none_input(self):

        result = analyze_code_structure(None)

        assert result['function_length_variance'] == 0.0
        assert result['average_nesting_depth'] == 0.0
        assert result['node_type_diversity'] == 0
        assert result['control_flow_complexity'] == 0.0
        assert result['structural_uniformity_score'] == 0.0
        assert result['total_functions'] == 0

    def test_analyze_code_structure_syntax_error(self):

        code_with_syntax_error = 

        result = analyze_code_structure(code_with_syntax_error)

        assert result['function_length_variance'] == 0.0
        assert result['total_functions'] == 0
        assert result['structural_uniformity_score'] == 0.0

    def test_analyze_code_structure_no_functions(self):

        code_without_functions = 

        result = analyze_code_structure(code_without_functions)

        assert result['total_functions'] == 0
        assert result['function_length_variance'] == 0.0
        assert result['average_nesting_depth'] == 0.0
        assert result['node_type_diversity'] > 5
        assert result['control_flow_complexity'] > 0

    def test_analyze_code_structure_single_function(self):

        code_with_single_function = 

        result = analyze_code_structure(code_with_single_function)

        assert result['total_functions'] == 1
        assert result['function_length_variance'] == 0.0
        assert result['average_nesting_depth'] > 2.0
        assert result['structural_uniformity_score'] < 50


class TestAILanguagePatternMatching:


    def test_match_ai_language_patterns_with_ai_references(self):

        code_with_ai_references = 

        result = match_ai_language_patterns(code_with_ai_references)

        assert result['ai_phrase_count'] > 0
        assert result['confidence_level'] > 50
        assert any('ai language model' in phrase.lower() for phrase in result['ai_phrases_found'])
        assert result['conversational_indicators'] >= 2
        assert result['disclaimer_patterns'] >= 1

    def test_match_ai_language_patterns_conversational_style(self):

        code_with_conversational_style = 

        result = match_ai_language_patterns(code_with_conversational_style)

        assert result['conversational_indicators'] >= 3
        assert result['confidence_level'] > 30
        assert any('here\'s an example' in phrase.lower() or 'here is an example' in phrase.lower() 
                 for phrase in result['ai_phrases_found'])

    def test_match_ai_language_patterns_disclaimer_patterns(self):

        code_with_disclaimers = 

        result = match_ai_language_patterns(code_with_disclaimers)

        assert result['disclaimer_patterns'] >= 3
        assert result['confidence_level'] > 40
        assert any('cannot access' in phrase.lower() for phrase in result['ai_phrases_found'])

    def test_match_ai_language_patterns_human_code(self):

        human_code = 

        result = match_ai_language_patterns(human_code)

        assert result['ai_phrase_count'] == 0 or result['confidence_level'] < 20
        assert result['conversational_indicators'] == 0
        assert result['disclaimer_patterns'] == 0

    def test_match_ai_language_patterns_mixed_content(self):

        mixed_code = 

        result = match_ai_language_patterns(mixed_code)

        assert 0 < result['confidence_level'] <= 100
        assert result['conversational_indicators'] >= 1

    def test_match_ai_language_patterns_empty_input(self):

        result = match_ai_language_patterns("")

        assert result['ai_phrases_found'] == []
        assert result['ai_phrase_count'] == 0
        assert result['conversational_indicators'] == 0
        assert result['disclaimer_patterns'] == 0
        assert result['confidence_level'] == 0.0

    def test_match_ai_language_patterns_none_input(self):

        result = match_ai_language_patterns(None)

        assert result['ai_phrases_found'] == []
        assert result['ai_phrase_count'] == 0
        assert result['conversational_indicators'] == 0
        assert result['disclaimer_patterns'] == 0
        assert result['confidence_level'] == 0.0

    def test_match_ai_language_patterns_no_comments(self):

        code_without_comments = 

        result = match_ai_language_patterns(code_without_comments)

        assert result['ai_phrases_found'] == []
        assert result['ai_phrase_count'] == 0
        assert result['confidence_level'] == 0.0

    def test_match_ai_language_patterns_case_insensitive(self):

        code_with_varied_cases = 

        result = match_ai_language_patterns(code_with_varied_cases)

        assert result['ai_phrase_count'] > 0
        assert result['confidence_level'] > 50
        assert any('ai language model' in phrase.lower() for phrase in result['ai_phrases_found'])
        assert result['conversational_indicators'] >= 2


class TestMainEngineOrchestrator:


    def test_analyze_ai_generated_code(self):

        ai_generated_code = 

        analysis_result = analyze(ai_generated_code)

    # Check structure of results
        assert 'comment_patterns' in analysis_result
        assert 'variable_names' in analysis_result
        assert 'code_structure' in analysis_result
        assert 'ai_language_patterns' in analysis_result
        assert 'summary' in analysis_result
        assert 'analysis_metadata' in analysis_result

        assert analysis_result['comment_patterns']['generic_comments'] > 0
        assert analysis_result['variable_names']['generic_percentage'] > 30
        assert analysis_result['ai_language_patterns']['ai_phrase_count'] > 0
        assert analysis_result['summary']['overall_suspicion_score'] > 25
        assert len(analysis_result['summary']['risk_factors']) > 0

    def test_analyze_human_written_code(self):

        human_code = 

        analysis_result = analyze(human_code)

        assert analysis_result['comment_patterns']['generic_comments'] == 0
        assert analysis_result['variable_names']['generic_percentage'] < 30
        assert analysis_result['ai_language_patterns']['ai_phrase_count'] == 0
        assert analysis_result['summary']['overall_suspicion_score'] < 30
        assert analysis_result['code_structure']['structural_uniformity_score'] < 90

    def test_analyze_empty_input(self):

        analysis_result = analyze("")

        assert analysis_result['comment_patterns']['generic_comments'] == 0
        assert analysis_result['variable_names']['total_names_count'] == 0
        assert analysis_result['code_structure']['total_functions'] == 0
        assert analysis_result['ai_language_patterns']['ai_phrase_count'] == 0
        assert analysis_result['summary']['overall_suspicion_score'] == 0.0
        assert analysis_result['analysis_metadata']['code_length'] == 0

    def test_analyze_none_input(self):

        analysis_result = analyze(None)

        assert analysis_result['summary']['overall_suspicion_score'] == 0.0
        assert analysis_result['analysis_metadata']['code_length'] == 0
        assert analysis_result['analysis_metadata']['analysis_timestamp'] is None

    def test_analyze_mixed_content(self):

        mixed_code = 

        analysis_result = analyze(mixed_code)

        assert 10 < analysis_result['summary']['overall_suspicion_score'] < 70
        assert analysis_result['ai_language_patterns']['conversational_indicators'] > 0
        assert analysis_result['variable_names']['generic_percentage'] > 0

    def test_analyze_metadata_structure(self):

        code = "def test(): pass"
        analysis_result = analyze(code)

        metadata = analysis_result['analysis_metadata']
        assert 'code_length' in metadata
        assert 'analysis_timestamp' in metadata
        assert 'heuristics_run' in metadata
        assert 'errors_encountered' in metadata

        assert metadata['code_length'] == len(code)
        assert metadata['heuristics_run'] == 4
        assert isinstance(metadata['errors_encountered'], list)

    def test_analyze_summary_structure(self):

        code = 
        analysis_result = analyze(code)

        summary = analysis_result['summary']
        assert 'total_indicators' in summary
        assert 'risk_factors' in summary
        assert 'overall_suspicion_score' in summary

        assert isinstance(summary['total_indicators'], int)
        assert isinstance(summary['risk_factors'], list)
        assert isinstance(summary['overall_suspicion_score'], (int, float))
        assert 0 <= summary['overall_suspicion_score'] <= 100

    def test_analyze_comprehensive_ai_code(self):

        comprehensive_ai_code = 

        analysis_result = analyze(comprehensive_ai_code)

        assert analysis_result['comment_patterns']['generic_comments'] >= 3
        assert analysis_result['variable_names']['generic_percentage'] > 60
        assert analysis_result['code_structure']['structural_uniformity_score'] > 70
        assert analysis_result['ai_language_patterns']['ai_phrase_count'] >= 2
        assert analysis_result['summary']['overall_suspicion_score'] > 30
        assert len(analysis_result['summary']['risk_factors']) >= 4


def test_ast_module_available():

    import ast

    code = "x = 1"
    tree = ast.parse(code)
    assert isinstance(tree, ast.AST), "AST parsing not working"

    nodes = list(ast.walk(tree))
    assert len(nodes) > 0, "AST node traversal not working"


def test_sqlite_available():

    import sqlite3

    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()

    cursor.execute("CREATE TABLE test (id INTEGER PRIMARY KEY)")
    cursor.execute("INSERT INTO test DEFAULT VALUES")
    cursor.fetchone()

    conn.close()
    assert True, "SQLite functionality verified"
