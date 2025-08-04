

import unittest
from shadow_ai.engine import analyze_style_inconsistency


class TestStyleInconsistencyDetector(unittest.TestCase):


    def test_consistent_code_style(self):

        consistent_code = 

        result = analyze_style_inconsistency(consistent_code)

        self.assertEqual(result['inconsistency_count'], 0)
        self.assertLessEqual(result['inconsistency_score'], 20.0)
        self.assertEqual(len(result['inconsistent_patterns']), 0)
        self.assertGreaterEqual(result['total_code_blocks'], 2)

    def test_mixed_indentation_styles(self):

        mixed_indentation_code = 

        result = analyze_style_inconsistency(mixed_indentation_code)

        self.assertGreater(result['inconsistency_count'], 0)
        self.assertGreater(result['inconsistency_score'], 0.0)

        patterns = ' '.join(result['inconsistent_patterns'])
        self.assertIn('indentation', patterns.lower())

    def test_mixed_naming_conventions(self):

        mixed_naming_code = 

        result = analyze_style_inconsistency(mixed_naming_code)

        self.assertGreater(result['inconsistency_count'], 0)
        self.assertGreater(result['inconsistency_score'], 0.0)

        patterns = ' '.join(result['inconsistent_patterns'])
        self.assertIn('naming', patterns.lower())

    def test_inconsistent_comment_density(self):

        inconsistent_comments_code = 

        result = analyze_style_inconsistency(inconsistent_comments_code)

        self.assertGreater(result['inconsistency_count'], 0)
        self.assertGreater(result['inconsistency_score'], 0.0)

        patterns = ' '.join(result['inconsistent_patterns'])
        self.assertIn('comment', patterns.lower())

    def test_inconsistent_line_length_patterns(self):

        inconsistent_line_length_code = 

        result = analyze_style_inconsistency(inconsistent_line_length_code)

        self.assertGreater(result['inconsistency_count'], 0)
        self.assertGreater(result['inconsistency_score'], 0.0)

        patterns = ' '.join(result['inconsistent_patterns'])
        self.assertIn('length', patterns.lower())

    def test_multiple_inconsistencies(self):

        multi_inconsistent_code = 

        result = analyze_style_inconsistency(multi_inconsistent_code)

        self.assertGreaterEqual(result['inconsistency_count'], 2)
        self.assertGreater(result['inconsistency_score'], 20.0)

        patterns = ' '.join(result['inconsistent_patterns'])
        self.assertTrue(
            'indentation' in patterns.lower() or 'naming' in patterns.lower(),
            "Should detect at least one of: indentation or naming inconsistencies"
        )

    def test_single_function_code(self):

        single_function_code = 

        result = analyze_style_inconsistency(single_function_code)

        self.assertEqual(result['inconsistency_count'], 0)
        self.assertEqual(result['inconsistency_score'], 0.0)
        self.assertEqual(len(result['inconsistent_patterns']), 0)

    def test_empty_code(self):

        result = analyze_style_inconsistency("")

        self.assertEqual(result['inconsistency_count'], 0)
        self.assertEqual(result['inconsistency_score'], 0.0)
        self.assertEqual(len(result['inconsistent_patterns']), 0)
        self.assertEqual(result['total_code_blocks'], 0)

    def test_syntax_error_code(self):

        syntax_error_code = 

        result = analyze_style_inconsistency(syntax_error_code)

        self.assertEqual(result['inconsistency_count'], 0)
        self.assertEqual(result['inconsistency_score'], 0.0)
        self.assertEqual(len(result['inconsistent_patterns']), 0)
        self.assertEqual(result['total_code_blocks'], 0)

    def test_global_scope_analysis(self):

        global_code = 

        result = analyze_style_inconsistency(global_code)

        self.assertGreaterEqual(result['total_code_blocks'], 0)

    def test_style_fingerprint_structure(self):

        code_with_functions = 

        result = analyze_style_inconsistency(code_with_functions)

    # Check fingerprint structure
        for fingerprint in result['style_fingerprints']:
            self.assertIn('node_type', fingerprint)
            self.assertIn('node_name', fingerprint)
            self.assertIn('line_range', fingerprint)
            self.assertIn('indentation_style', fingerprint)
            self.assertIn('naming_style', fingerprint)
            self.assertIn('comment_style', fingerprint)
            self.assertIn('line_length_style', fingerprint)


if __name__ == '__main__':
    unittest.main()
