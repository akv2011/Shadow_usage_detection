

import argparse
import sys
from pathlib import Path
from typing import Dict, Any, List

from .engine import analyze
from .parser import parse, ParserError, InvalidInputError, FileTooLargeError


def format_analysis_results(results: List[Dict[str, Any]]) -> str:

    if not results:
        return "No results to display."

    output_lines = []

    for i, result in enumerate(results):
        if len(results) > 1:
            output_lines.append(f"\n=== File {i+1}: {result.get('source', 'Unknown')} ===")

        analysis = result.get('analysis', {})

    # Extract key metrics
        summary = analysis.get('summary', {})
        suspicion_score = summary.get('overall_suspicion_score', 0.0)
        risk_factors = summary.get('risk_factors', [])

        if suspicion_score >= 70.0:
            risk_level = "HIGH"
            result_verdict = "Likely AI-Generated"
        elif suspicion_score >= 40.0:
            risk_level = "MEDIUM" 
            result_verdict = "Possibly AI-Generated"
        else:
            risk_level = "LOW"
            result_verdict = "Likely Human-Written"

        output_lines.append(f"Source: {result.get('source', 'Unknown')}")
        output_lines.append(f"Language: {result.get('language', 'Unknown')}")
        output_lines.append(f"Result: {result_verdict}")
        output_lines.append(f"Confidence: {suspicion_score:.1f}%")

        if risk_factors:
            primary_reasons = risk_factors[:2]
            reason = ", ".join(primary_reasons)
            output_lines.append(f"Reason: {reason}")

            patterns_list = [factor.split('(')[0].strip() for factor in risk_factors]
            patterns_str = "[" + ", ".join(patterns_list) + "]"
            output_lines.append(f"Patterns Found: {patterns_str}")
        else:
            output_lines.append("Reason: No significant AI patterns detected")
            output_lines.append("Patterns Found: []")

        metadata = analysis.get('analysis_metadata', {})
        if metadata.get('errors_encountered'):
            output_lines.append("Warnings:")
            for error in metadata['errors_encountered']:
                output_lines.append(f"  - {error}")

    return "\n".join(output_lines)


def analyze_single_file(file_path: str) -> int:

    try:
    # Parse the file
        parsed_results = parse(file_path)

    # Analyze each result
        for result in parsed_results:
            content = result['content']
            analysis = analyze(content)
            result['analysis'] = analysis

        output = format_analysis_results(parsed_results)
        print(output)

        return 0

    except FileNotFoundError:
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        return 1
    except PermissionError:
        print(f"Error: Permission denied accessing file: {file_path}", file=sys.stderr)
        return 1
    except FileTooLargeError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error analyzing file: {e}", file=sys.stderr)
        return 1


def check_text_string(text: str) -> int:

    try:
    # Parse the text string
        parsed_results = parse(text)

    # Analyze each result
        for result in parsed_results:
            content = result['content']
            analysis = analyze(content)
            result['analysis'] = analysis

        output = format_analysis_results(parsed_results)
        print(output)

        return 0

    except InvalidInputError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error analyzing text: {e}", file=sys.stderr)
        return 1


def scan_directory(directory_path: str, max_files: int = 5, recursive: bool = False) -> int:

    if recursive:
        print("Warning: Recursive scanning not yet implemented. Scanning top level only.")

    try:
    # Parse the directory
        parsed_results = parse(directory_path, max_files=max_files)

        if not parsed_results:
            print(f"No code files found in directory: {directory_path}")
            return 0

        print(f"Found {len(parsed_results)} code files to analyze...")

    # Analyze each result
        for result in parsed_results:
            content = result['content']
            analysis = analyze(content)
            result['analysis'] = analysis

        output = format_analysis_results(parsed_results)
        print(output)

        return 0

    except FileNotFoundError:
        print(f"Error: Directory not found: {directory_path}", file=sys.stderr)
        return 1
    except PermissionError:
        print(f"Error: Permission denied accessing directory: {directory_path}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error scanning directory: {e}", file=sys.stderr)
        return 1


def create_parser() -> argparse.ArgumentParser:

    parser = argparse.ArgumentParser(
        prog='shadow-detect',
        description='Shadow AI Detection Tool - Analyze code for AI-generated patterns',
        epilog='Example: shadow-detect analyze myfile.py'
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Analyze command - single file
    analyze_parser = subparsers.add_parser(
        'analyze',
        help='Analyze a single file for AI-generated content'
    )
    analyze_parser.add_argument(
        'file',
        help='Path to the file to analyze'
    )

    # Check command - raw text
    check_parser = subparsers.add_parser(
        'check',
        help='Analyze raw code text for AI-generated content'
    )
    check_parser.add_argument(
        '--text',
        required=True,
        help='Code text to analyze (in quotes)'
    )

    scan_parser = subparsers.add_parser(
        'scan',
        help='Scan a directory for code files and analyze them'
    )
    scan_parser.add_argument(
        'directory',
        help='Path to the directory to scan'
    )
    scan_parser.add_argument(
        '--max-files',
        type=int,
        default=5,
        help='Maximum number of files to process (default: 5)'
    )
    scan_parser.add_argument(
        '--recursive',
        action='store_true',
        help='Scan subdirectories recursively (not yet implemented)'
    )

    return parser


def main() -> int:

    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    try:
        if args.command == 'analyze':
            return analyze_single_file(args.file)
        elif args.command == 'check':
            return check_text_string(args.text)
        elif args.command == 'scan':
            return scan_directory(
                args.directory, 
                max_files=args.max_files,
                recursive=args.recursive
            )
        else:
            print(f"Unknown command: {args.command}", file=sys.stderr)
            return 1

    except KeyboardInterrupt:
        print("\nOperation cancelled by user.", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
