#!/usr/bin/env python3
import test_support
from test_support import TempBuildDir, write_file_lines, write_compilation_database, run_colobot_lint
import os

class TestIncludeStyleRule(test_support.TestBase):
    def setUp(self):
        self.set_rules_selection(['IncludeStyleRule'])

    def assert_colobot_lint_result_with_project_headers(self,
                                                        source_file_lines,
                                                        cpp_file_path,
                                                        project_header_paths,
                                                        expected_errors):
        with TempBuildDir() as temp_dir:
            src_dir = temp_dir + '/src'
            os.mkdir(src_dir)

            cpp_file_name = src_dir + '/' + cpp_file_path
            os.makedirs(os.path.dirname(cpp_file_name), exist_ok = True)
            write_file_lines(cpp_file_name, source_file_lines)

            for header_path in project_header_paths:
                header_file_name = src_dir + '/' + header_path
                os.makedirs(os.path.dirname(header_file_name), exist_ok = True)
                write_file_lines(header_file_name, [''])

            write_compilation_database(
                build_directory = temp_dir,
                source_file_names = [cpp_file_name],
                additional_compile_flags = '-I' + src_dir)

            xml_output = run_colobot_lint(build_directory = temp_dir,
                                          source_dir = src_dir,
                                          source_paths = [cpp_file_name],
                                          rules_selection = self.rules_selection)
            self.assert_xml_output_match(xml_output, expected_errors)

    def assert_colobot_lint_result_with_project_headers_and_fake_header_source(self,
                                                                               source_file_lines,
                                                                               header_file_path,
                                                                               fake_header_source_path,
                                                                               project_headers,
                                                                               expected_errors):
        with TempBuildDir() as temp_dir:
            src_dir = temp_dir + '/src'
            os.mkdir(src_dir)

            fake_header_source_file_name = temp_dir + '/' + fake_header_source_path
            os.makedirs(os.path.dirname(fake_header_source_file_name), exist_ok = True)
            write_file_lines(fake_header_source_file_name, [
                '#include "{0}"'.format(header_file_path)
            ])

            header_file_name = src_dir + '/' + header_file_path
            os.makedirs(os.path.dirname(header_file_name), exist_ok = True)
            write_file_lines(header_file_name, source_file_lines)

            for header in project_headers:
                header_file_name = src_dir + '/' + header['path']
                os.makedirs(os.path.dirname(header_file_name), exist_ok = True)
                write_file_lines(header_file_name, header['source_lines'])

            write_compilation_database(
                build_directory = temp_dir,
                source_file_names = [fake_header_source_file_name],
                additional_compile_flags = '-I' + src_dir)

            xml_output = run_colobot_lint(build_directory = temp_dir,
                                          source_dir = src_dir,
                                          source_paths = [fake_header_source_file_name],
                                          rules_selection = self.rules_selection)
            self.assert_xml_output_match(xml_output, expected_errors)

    def test_no_includes(self):
        self.assert_colobot_lint_result(
            source_file_lines = [
                ''
            ],
            expected_errors = [])

    def test_local_includes_sorted_alphabetically(self):
        self.assert_colobot_lint_result_with_project_headers(
            source_file_lines = [
                '#include "abc.h"',
                '#include "def.h"',
                '#include "def/abc.h"',
                '#include "def/def.h"',
            ],
            cpp_file_path = 'src.cpp',
            project_header_paths = [
                'abc.h',
                'def.h',
                'def/abc.h',
                'def/def.h'
            ],
            expected_errors = [])

    def test_local_includes_not_sorted_alphabetically(self):
        self.assert_colobot_lint_result_with_project_headers(
            source_file_lines = [
                '#include "abc.h"',
                '#include "def.h"',
                '#include "def/def.h"',
                '#include "def/abc.h"',
            ],
            cpp_file_path = 'src.cpp',
            project_header_paths = [
                'abc.h',
                'def.h',
                'def/abc.h',
                'def/def.h'
            ],
            expected_errors = [
                {
                    'id': 'include style',
                    'severity': 'style',
                    'msg': "Include 'def/def.h' breaks alphabetical ordering",
                    'line': '3'
                }
            ])

    def test_system_includes_dont_need_to_be_sorted_alphabetically(self):
        self.assert_colobot_lint_result(
            source_file_lines = [
                '#include <string>',
                '#include <iostream>',
            ],
            expected_errors = [])

    def test_local_include_in_angle_brackets(self):
        self.assert_colobot_lint_result_with_project_headers(
            source_file_lines = [
                '#include "abc.h"',
                '#include "def.h"',
                '#include <def/abc.h>',
                '#include "def/def.h"',
            ],
            cpp_file_path = 'src.cpp',
            project_header_paths = [
                'abc.h',
                'def.h',
                'def/abc.h',
                'def/def.h'
            ],
            expected_errors = [
                {
                    'id': 'include style',
                    'severity': 'style',
                    'msg': "Local include 'def/abc.h' should be included with quotes, not angled brackets",
                    'line': '3'
                }
            ])

    def test_global_include_in_quotes(self):
        self.assert_colobot_lint_result(
            source_file_lines = [
                '#include <string>',
                '#include "sstream"',
                '#include <iostream>',
            ],
            expected_errors = [
                {
                    'id': 'include style',
                    'severity': 'style',
                    'msg': "Global include 'sstream' should be included with angled brackets, not quotes",
                    'line': '2'
                }
            ])

    def test_local_include_not_full_path_from_project_root(self):
        self.assert_colobot_lint_result_with_project_headers(
            source_file_lines = [
                '#include "abc.h"',
                '#include "def.h"',
                '#include "def/ghi.h"',
                '#include "jkl.h"',
            ],
            cpp_file_path = 'def/mno.cpp',
            project_header_paths = [
                'abc.h',
                'def.h',
                'def/ghi.h',
                'def/jkl.h'
            ],
            expected_errors = [
                {
                    'id': 'include style',
                    'severity': 'style',
                    'msg': "Expected local include to be full relative path from project root directory: 'def/jkl.h', not 'jkl.h'",
                    'line': '4'
                }
            ])

    def test_local_and_global_includes_in_one_block(self):
        self.assert_colobot_lint_result_with_project_headers(
            source_file_lines = [
                '#include "abc.h"',
                '#include "def.h"',
                '#include  <iostream>',
                '#include "<sstream>',
            ],
            cpp_file_path = 'def/ghi.cpp',
            project_header_paths = [
                'abc.h',
                'def.h'
            ],
            expected_errors = [
                {
                    'id': 'include style',
                    'severity': 'style',
                    'msg': "Expected empty line between include directives",
                    'line': '3'
                }
            ])

    def test_local_and_global_includes_in_separate_blocks(self):
        self.assert_colobot_lint_result_with_project_headers(
            source_file_lines = [
                '#include "abc.h"',
                '#include "def.h"',
                '',
                '#include <iostream>',
                '#include <sstream>',
            ],
            cpp_file_path = 'def/ghi.cpp',
            project_header_paths = [
                'abc.h',
                'def.h'
            ],
            expected_errors = [])

    def test_local_include_after_global_include(self):
        self.assert_colobot_lint_result_with_project_headers(
            source_file_lines = [
                '#include "abc.h"',
                '',
                '#include <iostream>',
                '#include <sstream>',
                '#include "def.h"'
            ],
            cpp_file_path = 'def/ghi.cpp',
            project_header_paths = [
                'abc.h',
                'def.h'
            ],
            expected_errors = [
                {
                    'id': 'include style',
                    'severity': 'style',
                    'msg': "Local include 'def.h' should not be placed after global includes",
                    'line': '5'
                }
            ])

    def test_config_header_at_the_top(self):
        self.assert_colobot_lint_result_with_project_headers(
            source_file_lines = [
                '#include "config/config.h"',
                '',
                '#include "abc.h"',
                '#include "def.h"',
                '#include "def/abc.h"',
                '#include "def/def.h"',
            ],
            cpp_file_path = 'src.cpp',
            project_header_paths = [
                'config/config.h',
                'abc.h',
                'def.h',
                'def/abc.h',
                'def/def.h'
            ],
            expected_errors = [])

    def test_config_header_in_one_block_at_the_top(self):
        self.assert_colobot_lint_result_with_project_headers(
            source_file_lines = [
                '#include "config/config.h"',
                '#include "abc.h"',
                '#include "def.h"',
                '#include "def/abc.h"',
                '#include "def/def.h"',
            ],
            cpp_file_path = 'src.cpp',
            project_header_paths = [
                'config/config.h',
                'abc.h',
                'def.h',
                'def/abc.h',
                'def/def.h'
            ],
            expected_errors = [
                {
                    'id': 'include style',
                    'severity': 'style',
                    'msg': "Expected empty line between include directives",
                    'line': '2'
                }
            ])

    def test_config_header_not_at_the_top(self):
        self.assert_colobot_lint_result_with_project_headers(
            source_file_lines = [
                '#include "abc.h"',
                '#include "config/config.h"',
                '#include "def.h"',
                '#include "def/abc.h"',
                '#include "def/def.h"',
            ],
            cpp_file_path = 'src.cpp',
            project_header_paths = [
                'config/config.h',
                'abc.h',
                'def.h',
                'def/abc.h',
                'def/def.h'
            ],
            expected_errors = [
                {
                    'id': 'include style',
                    'severity': 'style',
                    'msg': "Expected config include directive: 'config/config.h', not 'abc.h'",
                    'line': '1'
                },
                {
                    'id': 'include style',
                    'severity': 'style',
                    'msg': "Expected empty line between include directives",
                    'line': '2'
                }
            ])

    def test_matching_header_at_the_top(self):
        self.assert_colobot_lint_result_with_project_headers(
            source_file_lines = [
                '#include "src.h"',
                '',
                '#include "abc.h"',
                '#include "def.h"',
                '#include "def/abc.h"',
                '#include "def/def.h"',
            ],
            cpp_file_path = 'src.cpp',
            project_header_paths = [
                'src.h',
                'abc.h',
                'def.h',
                'def/abc.h',
                'def/def.h'
            ],
            expected_errors = [])

    def test_matching_header_in_one_block(self):
        self.assert_colobot_lint_result_with_project_headers(
            source_file_lines = [
                '#include "src.h"',
                '#include "abc.h"',
                '#include "def.h"',
                '#include "def/abc.h"',
                '#include "def/def.h"',
            ],
            cpp_file_path = 'src.cpp',
            project_header_paths = [
                'src.h',
                'abc.h',
                'def.h',
                'def/abc.h',
                'def/def.h'
            ],
            expected_errors = [
                {
                    'id': 'include style',
                    'severity': 'style',
                    'msg': "Expected empty line between include directives",
                    'line': '2'
                }
            ])

    def test_matching_header_and_config_file(self):
        self.assert_colobot_lint_result_with_project_headers(
            source_file_lines = [
                '#include "src.h"',
                '',
                '#include "config.h"',
                '',
                '#include "abc.h"',
                '#include "def.h"',
                '#include "def/abc.h"',
                '#include "def/def.h"',
            ],
            cpp_file_path = 'src.cpp',
            project_header_paths = [
                'config.h',
                'src.h',
                'abc.h',
                'def.h',
                'def/abc.h',
                'def/def.h'
            ],
            expected_errors = [])

    def test_matching_header_not_at_the_top(self):
        self.assert_colobot_lint_result_with_project_headers(
            source_file_lines = [
                '#include "abc.h"',
                '#include "src.h"',
                '#include "def.h"',
                '#include "def/abc.h"',
                '#include "def/def.h"',
            ],
            cpp_file_path = 'src.cpp',
            project_header_paths = [
                'src.h',
                'abc.h',
                'def.h',
                'def/abc.h',
                'def/def.h'
            ],
            expected_errors = [
                {
                    'id': 'include style',
                    'severity': 'style',
                    'msg': "Expected first include directive to be matching header file: 'src.h', not 'abc.h'",
                    'line': '1'
                },
                {
                    'id': 'include style',
                    'severity': 'style',
                    'msg': "Expected empty line between include directives",
                    'line': '2'
                },
                {
                    'id': 'include style',
                    'severity': 'style',
                    'msg': "Include 'src.h' breaks alphabetical ordering",
                    'line': '2'
                }
            ])

    def test_base_class_header_at_the_top(self):
        self.assert_colobot_lint_result_with_project_headers_and_fake_header_source(
            source_file_lines = [
                '#include "def/base.h"',
                '',
                '#include "abc/abc.h"',
                '#include "abc/def.h"',
                '#include "def/abc.h"',
                '#include "def/def.h"',
                '',
                'class Derived : public Base {};'
            ],
            header_file_path = 'def/src.h',
            fake_header_source_path = 'fake_header_sources/def/src.cpp',
            project_headers = [
                {
                    'path': 'abc/abc.h',
                    'source_lines': []
                },
                {
                    'path': 'abc/def.h',
                    'source_lines': []
                },
                {
                    'path': 'def/abc.h',
                    'source_lines': []
                },
                {
                    'path': 'def/def.h',
                    'source_lines': []
                },
                {
                    'path': 'def/base.h',
                    'source_lines': [
                        'class Base {};'
                    ]
                },
            ],
            expected_errors = [])

    def test_base_class_header_in_one_block(self):
        self.assert_colobot_lint_result_with_project_headers_and_fake_header_source(
            source_file_lines = [
                '#include "def/base.h"',
                '#include "abc/abc.h"',
                '#include "abc/def.h"',
                '#include "def/abc.h"',
                '#include "def/def.h"',
                '',
                'class Derived : public Base {};'
            ],
            header_file_path = 'def/src.h',
            fake_header_source_path = 'fake_header_sources/def/src.cpp',
            project_headers = [
                {
                    'path': 'abc/abc.h',
                    'source_lines': []
                },
                {
                    'path': 'abc/def.h',
                    'source_lines': []
                },
                {
                    'path': 'def/abc.h',
                    'source_lines': []
                },
                {
                    'path': 'def/def.h',
                    'source_lines': []
                },
                {
                    'path': 'def/base.h',
                    'source_lines': [
                        'class Base {};'
                    ]
                },
            ],
            expected_errors = [
                {
                    'id': 'include style',
                    'severity': 'style',
                    'msg': "Expected empty line between include directives",
                    'line': '2'
                }
            ])

    def test_base_class_header_and_config_file(self):
        self.assert_colobot_lint_result_with_project_headers_and_fake_header_source(
            source_file_lines = [
                '#include "def/base.h"',
                '',
                '#include "config/config.h"',
                '',
                '#include "abc/abc.h"',
                '#include "abc/def.h"',
                '#include "def/abc.h"',
                '#include "def/def.h"',
                '',
                '#include <string>',
                '',
                'class Derived : public Base {};'
            ],
            header_file_path = 'def/src.h',
            fake_header_source_path = 'fake_header_sources/def/src.cpp',
            project_headers = [
                {
                    'path': 'config/config.h',
                    'source_lines': []
                },
                {
                    'path': 'abc/abc.h',
                    'source_lines': []
                },
                {
                    'path': 'abc/def.h',
                    'source_lines': []
                },
                {
                    'path': 'def/abc.h',
                    'source_lines': []
                },
                {
                    'path': 'def/def.h',
                    'source_lines': []
                },
                {
                    'path': 'def/base.h',
                    'source_lines': [
                        'class Base {};'
                    ]
                },
            ],
            expected_errors = [])

if __name__ == '__main__':
    test_support.main()