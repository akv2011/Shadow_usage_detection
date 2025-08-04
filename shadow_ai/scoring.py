"""
Confidence Scoring Module for Shadow AI Detection Tool

This module implements sophisticated confidence scoring logic that converts
raw heuristic detection results into quantitative confidence scores (0-100%)
and qualitative risk levels (Low, Medium, High).

Author: Shadow AI Detection Tool
Created: 2025-08-04
"""

from typing import Dict, Any, Tuple
import math


class ConfidenceScorer:
    """
    Advanced confidence scoring system for AI detection heuristics.
    
    This class implements a weighted scoring algorithm that considers multiple
    factors and provides both quantitative scores and qualitative risk levels.
    """
    
    # Heuristic weights - these determine the relative importance of each check
    HEURISTIC_WEIGHTS = {
        'comment_patterns': {
            'generic_comments': 8.0,           # High weight - strong AI indicator
            'comment_to_code_ratio': 6.0,      # Medium-high weight
            'repetitive_patterns': 7.0,        # High weight - very suspicious
        },
        'variable_names': {
            'generic_percentage': 5.0,         # Medium weight
        },
        'code_structure': {
            'structural_uniformity': 4.0,      # Medium weight
            'function_length_variance': 3.0,   # Lower weight - less reliable
            'nesting_depth_consistency': 3.5,  # Medium-low weight
        },
        'ai_language_patterns': {
            'ai_phrases': 9.0,                 # Very high weight - strong indicator
            'conversational_indicators': 8.5,  # Very high weight
            'disclaimer_patterns': 7.5,        # High weight
        },
        'style_inconsistency': {
            'inconsistency_score': 6.5,        # Medium-high weight - suspicious patterns
            'pattern_diversity': 4.0,          # Medium weight - multiple different patterns
        }
    }
    
    # Risk level thresholds
    RISK_THRESHOLDS = {
        'low': (0, 40),       # 0-40%: Low risk
        'medium': (40, 70),   # 40-70%: Medium risk  
        'high': (70, 100),    # 70-100%: High risk
    }
    
    # Maximum possible scores for normalization
    MAX_SCORES = {
        'comment_patterns': {
            'generic_comments': 20,        # Max reasonable generic comments
            'comment_to_code_ratio': 1.0,  # Max ratio of 1.0 (100%)
            'repetitive_patterns': 10,     # Max reasonable repetitive patterns
        },
        'variable_names': {
            'generic_percentage': 100,     # Max percentage
        },
        'code_structure': {
            'structural_uniformity': 100,  # Max uniformity score
            'function_length_variance': 0, # Min variance (high uniformity)
            'nesting_depth_consistency': 100, # Max consistency score
        },
        'ai_language_patterns': {
            'ai_phrases': 15,              # Max reasonable AI phrases
            'conversational_indicators': 10, # Max conversational indicators
            'disclaimer_patterns': 5,      # Max disclaimer patterns
        },
        'style_inconsistency': {
            'inconsistency_score': 100,    # Max inconsistency score
            'pattern_count': 5,            # Max reasonable pattern count
        }
    }
    
    @classmethod
    def calculate_confidence_score(cls, heuristic_results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate comprehensive confidence score from heuristic results.
        
        Args:
            heuristic_results: Dictionary containing results from all heuristic checks
            
        Returns:
            Dictionary containing:
            - confidence_score: Float from 0-100
            - risk_level: String ('low', 'medium', 'high')
            - component_scores: Breakdown of scores by category
            - weighted_factors: Detailed scoring breakdown
        """
        component_scores = {}
        weighted_factors = {}
        total_weighted_score = 0.0
        total_possible_score = 0.0
        
        # Process comment pattern results
        comment_results = heuristic_results.get('comment_patterns', {})
        comment_score, comment_factors = cls._score_comment_patterns(comment_results)
        component_scores['comment_patterns'] = comment_score
        weighted_factors['comment_patterns'] = comment_factors
        
        # Process variable naming results
        variable_results = heuristic_results.get('variable_names', {})
        variable_score, variable_factors = cls._score_variable_names(variable_results)
        component_scores['variable_names'] = variable_score
        weighted_factors['variable_names'] = variable_factors
        
        # Process code structure results
        structure_results = heuristic_results.get('code_structure', {})
        structure_score, structure_factors = cls._score_code_structure(structure_results)
        component_scores['code_structure'] = structure_score
        weighted_factors['code_structure'] = structure_factors
        
        # Process AI language pattern results
        ai_language_results = heuristic_results.get('ai_language_patterns', {})
        ai_score, ai_factors = cls._score_ai_language_patterns(ai_language_results)
        component_scores['ai_language_patterns'] = ai_score
        weighted_factors['ai_language_patterns'] = ai_factors
        
        # Process style inconsistency results
        style_results = heuristic_results.get('style_inconsistency', {})
        style_score, style_factors = cls._score_style_inconsistency(style_results)
        component_scores['style_inconsistency'] = style_score
        weighted_factors['style_inconsistency'] = style_factors
        
        # Calculate total score
        total_weighted_score = sum(component_scores.values())
        
        # Calculate maximum possible score for normalization
        max_possible = (
            cls._get_max_comment_score() +
            cls._get_max_variable_score() +
            cls._get_max_structure_score() +
            cls._get_max_ai_language_score() +
            cls._get_max_style_score()
        )
        
        # Normalize to 0-100 scale
        if max_possible > 0:
            confidence_score = min(100.0, (total_weighted_score / max_possible) * 100.0)
        else:
            confidence_score = 0.0
        
        # Determine risk level
        risk_level = cls._determine_risk_level(confidence_score)
        
        return {
            'confidence_score': round(confidence_score, 2),
            'risk_level': risk_level,
            'component_scores': component_scores,
            'weighted_factors': weighted_factors,
            'total_weighted_score': round(total_weighted_score, 2),
            'max_possible_score': round(max_possible, 2)
        }
    
    @classmethod
    def _score_comment_patterns(cls, results: Dict[str, Any]) -> Tuple[float, Dict[str, float]]:
        """Score comment pattern heuristics."""
        weights = cls.HEURISTIC_WEIGHTS['comment_patterns']
        max_scores = cls.MAX_SCORES['comment_patterns']
        factors = {}
        
        # Generic comments score
        generic_count = results.get('generic_comments', 0)
        generic_normalized = min(1.0, generic_count / max_scores['generic_comments'])
        factors['generic_comments'] = generic_normalized * weights['generic_comments']
        
        # Comment-to-code ratio score
        ratio = results.get('comment_to_code_ratio', 0.0)
        # Handle infinite ratios (divide by zero cases)
        if math.isinf(ratio):
            ratio_normalized = 1.0
        else:
            ratio_normalized = min(1.0, ratio / max_scores['comment_to_code_ratio'])
        factors['comment_to_code_ratio'] = ratio_normalized * weights['comment_to_code_ratio']
        
        # Repetitive patterns score
        repetitive_count = results.get('repetitive_patterns', 0)
        repetitive_normalized = min(1.0, repetitive_count / max_scores['repetitive_patterns'])
        factors['repetitive_patterns'] = repetitive_normalized * weights['repetitive_patterns']
        
        total_score = sum(factors.values())
        return total_score, factors
    
    @classmethod
    def _score_variable_names(cls, results: Dict[str, Any]) -> Tuple[float, Dict[str, float]]:
        """Score variable naming heuristics."""
        weights = cls.HEURISTIC_WEIGHTS['variable_names']
        max_scores = cls.MAX_SCORES['variable_names']
        factors = {}
        
        # Generic percentage score
        generic_percentage = results.get('generic_percentage', 0.0)
        generic_normalized = generic_percentage / max_scores['generic_percentage']
        factors['generic_percentage'] = generic_normalized * weights['generic_percentage']
        
        total_score = sum(factors.values())
        return total_score, factors
    
    @classmethod
    def _score_code_structure(cls, results: Dict[str, Any]) -> Tuple[float, Dict[str, float]]:
        """Score code structure heuristics."""
        weights = cls.HEURISTIC_WEIGHTS['code_structure']
        max_scores = cls.MAX_SCORES['code_structure']
        factors = {}
        
        # Structural uniformity score
        uniformity = results.get('structural_uniformity_score', 0.0)
        uniformity_normalized = uniformity / max_scores['structural_uniformity']
        factors['structural_uniformity'] = uniformity_normalized * weights['structural_uniformity']
        
        # Function length variance (inverse scoring - low variance = high AI likelihood)
        variance = results.get('function_length_variance', 10.0)  # Default to high variance
        total_functions = results.get('total_functions', 0)
        if total_functions > 1:
            # Lower variance suggests AI generation (more uniform functions)
            # Use inverse scoring: variance of 0-2 gets high score, variance >5 gets low score
            variance_score = max(0.0, (5.0 - variance) / 5.0)
            factors['function_length_variance'] = variance_score * weights['function_length_variance']
        else:
            factors['function_length_variance'] = 0.0
        
        # Nesting depth consistency (if available in future enhancements)
        nesting_consistency = results.get('nesting_depth_consistency', 0.0)
        nesting_normalized = nesting_consistency / max_scores['nesting_depth_consistency']
        factors['nesting_depth_consistency'] = nesting_normalized * weights['nesting_depth_consistency']
        
        total_score = sum(factors.values())
        return total_score, factors
    
    @classmethod
    def _score_ai_language_patterns(cls, results: Dict[str, Any]) -> Tuple[float, Dict[str, float]]:
        """Score AI language pattern heuristics."""
        weights = cls.HEURISTIC_WEIGHTS['ai_language_patterns']
        max_scores = cls.MAX_SCORES['ai_language_patterns']
        factors = {}
        
        # AI phrases count
        ai_phrase_count = results.get('ai_phrase_count', 0)
        ai_normalized = min(1.0, ai_phrase_count / max_scores['ai_phrases'])
        factors['ai_phrases'] = ai_normalized * weights['ai_phrases']
        
        # Conversational indicators
        conversational = results.get('conversational_indicators', 0)
        conv_normalized = min(1.0, conversational / max_scores['conversational_indicators'])
        factors['conversational_indicators'] = conv_normalized * weights['conversational_indicators']
        
        # Disclaimer patterns
        disclaimers = results.get('disclaimer_patterns', 0)
        disc_normalized = min(1.0, disclaimers / max_scores['disclaimer_patterns'])
        factors['disclaimer_patterns'] = disc_normalized * weights['disclaimer_patterns']
        
        total_score = sum(factors.values())
        return total_score, factors
    
    @classmethod
    def _score_style_inconsistency(cls, results: Dict[str, Any]) -> Tuple[float, Dict[str, float]]:
        """Score style inconsistency heuristics."""
        weights = cls.HEURISTIC_WEIGHTS['style_inconsistency']
        max_scores = cls.MAX_SCORES['style_inconsistency']
        factors = {}
        
        # Inconsistency score
        inconsistency_score = results.get('inconsistency_score', 0.0)
        inconsistency_normalized = min(1.0, inconsistency_score / max_scores['inconsistency_score'])
        factors['inconsistency_score'] = inconsistency_normalized * weights['inconsistency_score']
        
        # Pattern diversity (number of different types of inconsistencies)
        pattern_count = results.get('inconsistency_count', 0)
        pattern_normalized = min(1.0, pattern_count / max_scores['pattern_count'])
        factors['pattern_diversity'] = pattern_normalized * weights['pattern_diversity']
        
        total_score = sum(factors.values())
        return total_score, factors
    
    @classmethod
    def _get_max_comment_score(cls) -> float:
        """Calculate maximum possible comment pattern score."""
        weights = cls.HEURISTIC_WEIGHTS['comment_patterns']
        return sum(weights.values())
    
    @classmethod
    def _get_max_variable_score(cls) -> float:
        """Calculate maximum possible variable naming score."""
        weights = cls.HEURISTIC_WEIGHTS['variable_names']
        return sum(weights.values())
    
    @classmethod
    def _get_max_structure_score(cls) -> float:
        """Calculate maximum possible code structure score."""
        weights = cls.HEURISTIC_WEIGHTS['code_structure']
        return sum(weights.values())
    
    @classmethod
    def _get_max_ai_language_score(cls) -> float:
        """Calculate maximum possible AI language pattern score."""
        weights = cls.HEURISTIC_WEIGHTS['ai_language_patterns']
        return sum(weights.values())
    
    @classmethod
    def _get_max_style_score(cls) -> float:
        """Calculate maximum possible style inconsistency score."""
        weights = cls.HEURISTIC_WEIGHTS['style_inconsistency']
        return sum(weights.values())
    
    @classmethod
    def _determine_risk_level(cls, confidence_score: float) -> str:
        """Determine risk level based on confidence score."""
        if confidence_score >= cls.RISK_THRESHOLDS['high'][0]:
            return 'high'
        elif confidence_score >= cls.RISK_THRESHOLDS['medium'][0]:
            return 'medium'
        else:
            return 'low'
    
    @classmethod
    def get_risk_level_thresholds(cls) -> Dict[str, Tuple[int, int]]:
        """Get the risk level thresholds for external use."""
        return cls.RISK_THRESHOLDS.copy()
    
    @classmethod
    def get_heuristic_weights(cls) -> Dict[str, Dict[str, float]]:
        """Get the heuristic weights for external use."""
        return cls.HEURISTIC_WEIGHTS.copy()


def calculate_confidence_score(heuristic_results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Convenience function for calculating confidence scores.
    
    Args:
        heuristic_results: Dictionary containing results from all heuristic checks
        
    Returns:
        Dictionary containing confidence score and related metrics
    """
    return ConfidenceScorer.calculate_confidence_score(heuristic_results)
