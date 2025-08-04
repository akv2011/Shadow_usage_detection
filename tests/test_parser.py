

import os
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open

import pytest

from shadow_ai.parser import (
    LanguageMapper, 
    read_source, 
    read_source_with_language,
    parse_directory,
    get_directory_stats,
    parse,
    parse_with_stats,
    validate_file_input,
    validate_string_input,
    ParserError,
    FileTooLargeError,
    InvalidInputError,
    UnsupportedFileTypeError,
    MAX_FILE_SIZE_BYTES,
    MAX_STRING_LENGTH
)


class TestCoreFileReading:


    def test_read_source_with_utf8_file(self):

        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False, suffix='.py') as f:
            test_content = "
            f.write(test_content)
            temp_path = f.name

        try:
            content, source_id = read_source(temp_path)
            assert content == test_content
            assert source_id == temp_path
        finally:
            os.unlink(temp_path)

    def test_read_source_with_latin1_file(self):

        test_content = "

        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.py') as f:
            f.write(test_content.encode('latin-1'))
            temp_path = f.name

        try:
            content, source_id = read_source(temp_path)
            assert isinstance(content, str)
            assert source_id == temp_path
            assert len(content) > 0
        finally:
            os.unlink(temp_path)

    def test_read_source_with_raw_string(self):

        test_string = "def example():\n    return 'This is raw code'"
        content, source_id = read_source(test_string)

        assert content == test_string
        assert source_id == 'raw_string'

    def test_read_source_with_empty_file(self):

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as f:
            f.write("")
            temp_path = f.name

        try:
            content, source_id = read_source(temp_path)
            assert content == ""
            assert source_id == temp_path
        finally:
            os.unlink(temp_path)

    def test_read_source_nonexistent_file_as_string(self):

        fake_path = "/this/path/does/not/exist.py"
        content, source_id = read_source(fake_path)

        assert content == fake_path
        assert source_id == 'raw_string'


class TestLanguageMapper:


    def test_get_language_python(self):

        assert LanguageMapper.get_language('script.py') == 'Python'
        assert LanguageMapper.get_language(Path('app.py')) == 'Python'

    def test_get_language_javascript(self):

        assert LanguageMapper.get_language('app.js') == 'JavaScript'
        assert LanguageMapper.get_language('component.jsx') == 'JavaScript'

    def test_get_language_typescript(self):

        assert LanguageMapper.get_language('app.ts') == 'TypeScript'
        assert LanguageMapper.get_language('component.tsx') == 'TypeScript'

    def test_get_language_various_extensions(self):

        test_cases = [
            ('server.go', 'Go'),
            ('main.rs', 'Rust'),
            ('App.java', 'Java'),
            ('main.cpp', 'C++'),
            ('header.h', 'C/C++'),
            ('script.php', 'PHP'),
            ('app.rb', 'Ruby'),
            ('Model.swift', 'Swift'),
            ('Main.kt', 'Kotlin'),
            ('Program.cs', 'C
            ('script.sh', 'Shell'),
            ('config.json', 'JSON'),
            ('config.yaml', 'YAML'),
            ('query.sql', 'SQL'),
        ]

        for filename, expected_language in test_cases:
            assert LanguageMapper.get_language(filename) == expected_language

    def test_get_language_unknown_extension(self):

        assert LanguageMapper.get_language('notes.txt') == 'plaintext'
        assert LanguageMapper.get_language('README.md') == 'plaintext'
        assert LanguageMapper.get_language('file.xyz') == 'plaintext'

    def test_get_language_no_extension(self):

        assert LanguageMapper.get_language('Makefile') == 'plaintext'
        assert LanguageMapper.get_language('LICENSE') == 'plaintext'

    def test_get_language_case_insensitive(self):

        assert LanguageMapper.get_language('Script.PY') == 'Python'
        assert LanguageMapper.get_language('App.JS') == 'JavaScript'
        assert LanguageMapper.get_language('Main.CPP') == 'C++'

    def test_is_code_file_positive(self):

        code_files = [
            'app.py', 'server.js', 'main.cpp', 'lib.go', 
            'component.tsx', 'style.css', 'config.json'
        ]

        for filename in code_files:
            assert LanguageMapper.is_code_file(filename), f"{filename} should be recognized as code"

    def test_is_code_file_negative(self):

        non_code_files = [
            'README.md', 'notes.txt', 'image.png', 'document.pdf',
            'archive.zip', 'video.mp4', 'unknown.xyz'
        ]

        for filename in non_code_files:
            assert not LanguageMapper.is_code_file(filename), f"{filename} should not be recognized as code"


class TestSourceWithLanguage:


    def test_read_source_with_language_file(self):

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as f:
            test_content = "def test():\n    pass"
            f.write(test_content)
            temp_path = f.name

        try:
            content, language, source_id = read_source_with_language(temp_path)
            assert content == test_content
            assert language == 'Python'
            assert source_id == temp_path
        finally:
            os.unlink(temp_path)

    def test_read_source_with_language_raw_string(self):

        test_string = "function test() { return true; }"
        content, language, source_id = read_source_with_language(test_string)

        assert content == test_string
        assert language == 'plaintext'
        assert source_id == 'raw_string'

    def test_read_source_with_language_unknown_extension(self):

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.unknown') as f:
            test_content = "Some content"
            f.write(test_content)
            temp_path = f.name

        try:
            content, language, source_id = read_source_with_language(temp_path)
            assert content == test_content
            assert language == 'plaintext'
            assert source_id == temp_path
        finally:
            os.unlink(temp_path)

    def test_read_source_with_language_various_files(self):

        test_cases = [
            ('.js', 'console.log("Hello");', 'JavaScript'),
            ('.go', 'package main\nfunc main() {}', 'Go'),
            ('.rs', 'fn main() {\n    println!("Hello");\n}', 'Rust'),
            ('.java', 'public class Test {\n    public static void main(String[] args) {}\n}', 'Java'),
        ]

        for extension, content, expected_language in test_cases:
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=extension) as f:
                f.write(content)
                temp_path = f.name

            try:
                read_content, language, source_id = read_source_with_language(temp_path)
                assert read_content == content
                assert language == expected_language
                assert source_id == temp_path
            finally:
                os.unlink(temp_path)


class TestInputValidation:


    def test_validate_file_input_success(self):

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as f:
            f.write("print('hello')")
            temp_path = Path(f.name)

        try:
            validate_file_input(temp_path)
        finally:
            os.unlink(temp_path)

    def test_validate_file_input_not_found(self):

        fake_path = Path("/this/path/does/not/exist.py")

        with pytest.raises(FileNotFoundError, match="File not found"):
            validate_file_input(fake_path)

    def test_validate_file_input_directory(self):

        temp_dir = Path(tempfile.mkdtemp())

        try:
            with pytest.raises(IsADirectoryError, match="Path is a directory"):
                validate_file_input(temp_dir)
        finally:
            os.rmdir(temp_dir)

    def test_validate_file_input_permission_denied(self):

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as f:
            f.write("print('hello')")
            temp_path = Path(f.name)

        try:
            with patch('os.access', return_value=False):
                with pytest.raises(PermissionError, match="permission denied"):
                    validate_file_input(temp_path)
        finally:
            os.unlink(temp_path)

    def test_validate_file_input_too_large(self):

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as f:
            temp_path = Path(f.name)

        try:
            with patch('shadow_ai.parser.MAX_FILE_SIZE_BYTES', 100):
                with open(temp_path, 'w') as f:
                    f.write('x' * 200)

                with pytest.raises(FileTooLargeError, match="File too large"):
                    validate_file_input(temp_path)
        finally:
            os.unlink(temp_path)

    def test_validate_string_input_success(self):

        valid_strings = [
            "def hello(): pass",
            "print('Hello, world!')",
            "x" * 1000,
        ]

        for test_string in valid_strings:
            validate_string_input(test_string)

    def test_validate_string_input_empty(self):

        with pytest.raises(InvalidInputError, match="cannot be empty"):
            validate_string_input("")

    def test_validate_string_input_too_long(self):

        long_string = "x" * (MAX_STRING_LENGTH + 1)

        with pytest.raises(InvalidInputError, match="too long"):
            validate_string_input(long_string)

    def test_validate_string_input_null_bytes(self):

        string_with_null = "def hello():\x00 pass"

        with pytest.raises(InvalidInputError, match="null bytes"):
            validate_string_input(string_with_null)

    def test_validate_string_input_wrong_type(self):

        with pytest.raises(InvalidInputError, match="must be a string"):
            validate_string_input(123)

        with pytest.raises(InvalidInputError, match="must be a string"):
            validate_string_input(None)

        with pytest.raises(InvalidInputError, match="must be a string"):
            validate_string_input(['not', 'a', 'string'])


class TestEnhancedFileReading:


    def test_read_source_with_validation_success(self):

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as f:
            test_content = "def test(): return True"
            f.write(test_content)
            temp_path = f.name

        try:
            content, source_id = read_source(temp_path)
            assert content == test_content
            assert source_id == temp_path
        finally:
            os.unlink(temp_path)

    def test_read_source_directory_error(self):

        temp_dir = tempfile.mkdtemp()

        try:
            with pytest.raises(IsADirectoryError):
                read_source(temp_dir)
        finally:
            os.rmdir(temp_dir)

    def test_read_source_file_too_large(self):

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as f:
            temp_path = Path(f.name)

        try:
            with patch('shadow_ai.parser.MAX_FILE_SIZE_BYTES', 100):
                with open(temp_path, 'w') as f:
                    f.write('x' * 200)

                with pytest.raises(FileTooLargeError):
                    read_source(temp_path)
        finally:
            os.unlink(temp_path)

    def test_read_source_string_validation(self):

        valid_code = "def hello(): pass"
        content, source_id = read_source(valid_code)
        assert content == valid_code
        assert source_id == 'raw_string'

        with pytest.raises(InvalidInputError):
            read_source("")

        with pytest.raises(InvalidInputError):
            read_source("def hello():\x00 pass")

    def test_read_source_with_language_validation(self):

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as f:
            test_content = "def test(): return True"
            f.write(test_content)
            temp_path = f.name

        try:
            content, language, source_id = read_source_with_language(temp_path)
            assert content == test_content
            assert language == 'Python'
            assert source_id == temp_path
        finally:
            os.unlink(temp_path)

        temp_dir = tempfile.mkdtemp()
        try:
            with pytest.raises(IsADirectoryError):
                read_source_with_language(temp_dir)
        finally:
            os.rmdir(temp_dir)


class TestParserExceptions:


    def test_parser_error_hierarchy(self):

        assert issubclass(FileTooLargeError, ParserError)
        assert issubclass(InvalidInputError, ParserError)
        assert issubclass(UnsupportedFileTypeError, ParserError)

    def test_file_too_large_error_message(self):

        error = FileTooLargeError("Test file too large")
        assert "Test file too large" in str(error)

    def test_invalid_input_error_message(self):

        error = InvalidInputError("Test invalid input")
        assert "Test invalid input" in str(error)


class TestErrorScenarios:


    def test_read_source_nonexistent_file_as_string(self):

        fake_path = "/this/path/does/not/exist.py"
        content, source_id = read_source(fake_path)

        assert content == fake_path
        assert source_id == 'raw_string'

    def test_language_mapper_edge_cases(self):

        assert LanguageMapper.get_language('') == 'plaintext'

        assert LanguageMapper.get_language('.py') == 'plaintext'

        assert LanguageMapper.get_language('file.test.py') == 'Python'

        assert LanguageMapper.get_language(Path('test.js')) == 'JavaScript'


class TestBatchProcessing:


    def create_test_directory_with_files(self, num_code_files=5, num_non_code_files=2):

        temp_dir = Path(tempfile.mkdtemp())

        code_files = [
            ('app.py', 'def main():\n    print("Hello from Python")'),
            ('server.js', 'console.log("Hello from JavaScript");'),
            ('main.go', 'package main\nfunc main() {\n    fmt.Println("Hello from Go")\n}'),
            ('component.tsx', 'const Component = () => <div>Hello from TypeScript</div>;'),
            ('style.css', 'body { color: blue; }'),
            ('config.json', '{"name": "test", "version": "1.0.0"}'),
            ('script.sh', '
        ]

        for i in range(min(num_code_files, len(code_files))):
            filename, content = code_files[i]
            (temp_dir / filename).write_text(content)

        non_code_files = [
            ('README.md', '
            ('notes.txt', 'Some random notes here.'),
            ('image.png', 'fake binary content'),
        ]

        for i in range(min(num_non_code_files, len(non_code_files))):
            filename, content = non_code_files[i]
            (temp_dir / filename).write_text(content)

        return temp_dir

    def test_parse_directory_success(self):

        test_dir = self.create_test_directory_with_files(3, 2)

        try:
            results = parse_directory(test_dir, max_files=5)

            assert len(results) == 3

    # Check structure of results
            for result in results:
                assert 'content' in result
                assert 'language' in result
                assert 'source' in result
                assert isinstance(result['content'], str)
                assert isinstance(result['language'], str)
                assert isinstance(result['source'], str)
                assert len(result['content']) > 0

            sources = [result['source'] for result in results]
            filenames = [Path(source).name for source in sources]
            assert filenames == sorted(filenames)

        finally:
            for file in test_dir.iterdir():
                file.unlink()
            test_dir.rmdir()

    def test_parse_directory_max_files_limit(self):

        test_dir = self.create_test_directory_with_files(7, 2)

        try:
            results = parse_directory(test_dir, max_files=3)
            assert len(results) == 3

            results = parse_directory(test_dir, max_files=10)
            assert len(results) == 7

        finally:
            for file in test_dir.iterdir():
                file.unlink()
            test_dir.rmdir()

    def test_parse_directory_empty_directory(self):

        test_dir = Path(tempfile.mkdtemp())

        try:
            results = parse_directory(test_dir)
            assert results == []
        finally:
            test_dir.rmdir()

    def test_parse_directory_no_code_files(self):

        test_dir = self.create_test_directory_with_files(0, 3)

        try:
            results = parse_directory(test_dir)
            assert results == []
        finally:
            for file in test_dir.iterdir():
                file.unlink()
            test_dir.rmdir()

    def test_parse_directory_validation_errors(self):

        fake_dir = Path("/this/path/does/not/exist")
        with pytest.raises(FileNotFoundError, match="Directory not found"):
            parse_directory(fake_dir)

        test_dir = Path(tempfile.mkdtemp())
        try:
            with pytest.raises(InvalidInputError, match="max_files must be positive"):
                parse_directory(test_dir, max_files=0)

            with pytest.raises(InvalidInputError, match="max_files must be positive"):
                parse_directory(test_dir, max_files=-1)
        finally:
            test_dir.rmdir()

        with tempfile.NamedTemporaryFile(delete=False, suffix='.py') as f:
            f.write(b"print('hello')")
            temp_file = Path(f.name)

        try:
            with pytest.raises(NotADirectoryError, match="not a directory"):
                parse_directory(temp_file)
        finally:
            temp_file.unlink()

    def test_parse_directory_permission_denied(self):

        test_dir = Path(tempfile.mkdtemp())

        try:
            with patch('os.access', return_value=False):
                with pytest.raises(PermissionError, match="permission denied"):
                    parse_directory(test_dir)
        finally:
            test_dir.rmdir()

    def test_parse_directory_skip_problematic_files(self):

        test_dir = self.create_test_directory_with_files(2, 0)

        large_file = test_dir / "large.py"
        large_file.write_text("print('hello')")

        try:
            original_validate = validate_file_input
            def mock_validate(file_path):
                if file_path.name == "large.py":
                    raise FileTooLargeError("File too large")
                return original_validate(file_path)

            with patch('shadow_ai.parser.validate_file_input', side_effect=mock_validate):
                results = parse_directory(test_dir)
                assert len(results) == 2

                sources = [Path(result['source']).name for result in results]
                assert "large.py" not in sources

        finally:
            for file in test_dir.iterdir():
                file.unlink()
            test_dir.rmdir()


class TestDirectoryStats:


    def test_get_directory_stats_mixed_files(self):

        temp_dir = Path(tempfile.mkdtemp())

        files_to_create = [
            ('app.py', 'print("hello")'),
            ('server.js', 'console.log("hello")'),
            ('main.go', 'package main'),
            ('README.md', '
            ('data.txt', 'some data'),
            ('style.css', 'body {}'),
        ]

        for filename, content in files_to_create:
            (temp_dir / filename).write_text(content)

        try:
            stats = get_directory_stats(temp_dir)

            assert stats['total_files'] == 6
            assert stats['code_files'] == 4

            expected_languages = {
                'Python': 1,
                'JavaScript': 1, 
                'Go': 1,
                'CSS': 1
            }
            assert stats['languages'] == expected_languages

        finally:
            for file in temp_dir.iterdir():
                file.unlink()
            temp_dir.rmdir()

    def test_get_directory_stats_empty_directory(self):

        temp_dir = Path(tempfile.mkdtemp())

        try:
            stats = get_directory_stats(temp_dir)

            assert stats['total_files'] == 0
            assert stats['code_files'] == 0
            assert stats['languages'] == {}

        finally:
            temp_dir.rmdir()

    def test_get_directory_stats_validation_errors(self):

        fake_dir = Path("/this/path/does/not/exist")
        with pytest.raises(FileNotFoundError, match="Directory not found"):
            get_directory_stats(fake_dir)

        with tempfile.NamedTemporaryFile(delete=False, suffix='.py') as f:
            f.write(b"print('hello')")
            temp_file = Path(f.name)

        try:
            with pytest.raises(NotADirectoryError, match="not a directory"):
                get_directory_stats(temp_file)
        finally:
            temp_file.unlink()

    def test_get_directory_stats_permission_denied(self):

        temp_dir = Path(tempfile.mkdtemp())

        try:
            with patch('os.access', return_value=False):
                with pytest.raises(PermissionError, match="cannot be read"):
                    get_directory_stats(temp_dir)
        finally:
            temp_dir.rmdir()


class TestErrorScenarios:


    def test_read_source_nonexistent_file_as_string(self):

        fake_path = "/this/path/does/not/exist.py"
        content, source_id = read_source(fake_path)

        assert content == fake_path
        assert source_id == 'raw_string'

    def test_language_mapper_edge_cases(self):

        assert LanguageMapper.get_language('') == 'plaintext'

        assert LanguageMapper.get_language('.py') == 'plaintext'

        assert LanguageMapper.get_language('file.test.py') == 'Python'

        assert LanguageMapper.get_language(Path('test.js')) == 'JavaScript'
