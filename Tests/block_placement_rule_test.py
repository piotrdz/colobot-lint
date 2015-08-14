#!/usr/bin/env python3
import test_support

class BlockPlacementRuleTest(test_support.TestBase):
    def setUp(self):
        self.set_default_rules_selection(['BlockPlacementRule'])
        self.set_default_error_id('code block placement')
        self.set_default_error_severity('style')

    # namespaces
    def test_namespace_braces_in_separate_lines(self):
        self.assert_colobot_lint_result(
            source_file_lines = [
                'namespace test',
                '{',
                '}'
            ],
            expected_errors = [])

    def test_namespace_opening_and_closing_brace_in_same_line(self):
        self.assert_colobot_lint_result(
            source_file_lines = [
                'namespace test { }'
            ],
            expected_errors = [])

    def test_namespace_opening_brace_in_same_line(self):
        self.assert_colobot_lint_result(
            source_file_lines = [
                'namespace test {',
                '}'
            ],
            expected_errors = [
            ])

    def test_other_declaration_just_before_closing_namespace_brace(self):
        self.assert_colobot_lint_result(
            source_file_lines = [
                'namespace test',
                '{',
                'void foo(); }'
            ],
            expected_errors = [
                {
                    'msg': 'Body of declaration or statement ends in a style that is not allowed',
                    'line': '3'
                }
            ])

    def test_other_declaration_after_closing_namespace_brace(self):
        self.assert_colobot_lint_result(
            source_file_lines = [
                'namespace test',
                '{',
                '} namespace foo { }'
            ],
            expected_errors = [
                {
                    'msg': 'Body of declaration or statement ends in a style that is not allowed',
                    'line': '3'
                }
            ])

    # classes, enums, unions, etc.
    def test_union_braces_in_separate_lines(self):
        self.assert_colobot_lint_result(
            source_file_lines = [
                'union test',
                '{',
                '  int x;',
                '  float y;',
                '};'
            ],
            expected_errors = [])

    def test_union_opening_and_closing_brace_in_same_line(self):
        self.assert_colobot_lint_result(
            source_file_lines = [
                'class test { };'
            ],
            expected_errors = [])

    def test_enum_opening_brace_in_same_line(self):
        self.assert_colobot_lint_result(
            source_file_lines = [
                'enum test {',
                '  foo',
                '};'
            ],
            expected_errors = [
                {
                    'msg': 'Body of declaration or statement begins in a style that is not allowed',
                    'line': '1'
                }
            ])

    def test_other_declaration_just_before_closing_enum_brace(self):
        self.assert_colobot_lint_result(
            source_file_lines = [
                'enum test',
                '{',
                ' foo };'
            ],
            expected_errors = [
                {
                    'msg': 'Body of declaration or statement ends in a style that is not allowed',
                    'line': '3'
                }
            ])

    def test_other_declaration_after_closing_enum_class_brace(self):
        self.assert_colobot_lint_result(
            source_file_lines = [
                'enum class test',
                '{',
                '  foo',
                '}; namespace foo { }'
            ],
            expected_errors = [
                {
                    'msg': 'Body of declaration or statement ends in a style that is not allowed',
                    'line': '4'
                }
            ])

    def test_nested_class_has_braces_in_invalid_style(self):
        self.assert_colobot_lint_result(
            source_file_lines = [
                'class foo',
                '{',
                '  class bar {',
                '  };',
                '};'
            ],
            expected_errors = [
                {
                    'msg': 'Body of declaration or statement begins in a style that is not allowed',
                    'line': '3'
                }
            ])

    # functions
    def test_function_braces_in_separate_lines(self):
        self.assert_colobot_lint_result(
            source_file_lines = [
                'void foo()',
                '{',
                '}'
            ],
            expected_errors = [])

    def test_function_opening_and_closing_brace_in_same_line(self):
        self.assert_colobot_lint_result(
            source_file_lines = [
                'void foo()',
                '{ }'
            ],
            expected_errors = [])

    def test_function_opening_brace_in_same_line(self):
        self.assert_colobot_lint_result(
            source_file_lines = [
                'void foo() {',
                'int x;',
                '}'
            ],
            expected_errors = [
                {
                    'msg': 'Body of declaration or statement begins in a style that is not allowed',
                    'line': '1'
                }
            ])

    def test_other_statement_just_before_closing_function_brace(self):
        self.assert_colobot_lint_result(
            source_file_lines = [
                'void foo()',
                '{',
                'int x; }'
            ],
            expected_errors = [
                {
                    'msg': 'Body of declaration or statement ends in a style that is not allowed',
                    'line': '3'
                }
            ])

    def test_other_declaration_after_closing_function_brace(self):
        self.assert_colobot_lint_result(
            source_file_lines = [
                'void test()',
                '{',
                '  int x;',
                '} namespace foo { }'
            ],
            expected_errors = [
                {
                    'msg': 'Body of declaration or statement ends in a style that is not allowed',
                    'line': '4'
                }
            ])

    def test_nested_statement_block_has_braces_in_invalid_style(self):
        self.assert_colobot_lint_result(
            source_file_lines = [
                'void foo()',
                '{',
                '  if (true) {',
                '  }',
                '}'
            ],
            expected_errors = [
                {
                    'msg': 'Body of declaration or statement begins in a style that is not allowed',
                    'line': '3'
                }
            ])

    def test_multiline_function_argument_list_opening_brace_in_same_line(self):
        self.assert_colobot_lint_result(
            source_file_lines = [
                'void foo(int a,',
                '  int b) {',
                '}'
            ],
            expected_errors = [
                {
                    'msg': 'Body of declaration or statement begins in a style that is not allowed',
                    'line': '2'
                }
            ])

    def test_multiline_function_argument_list_opening_brace_in_new_line(self):
        self.assert_colobot_lint_result(
            source_file_lines = [
                'void foo(int a,',
                'int b)',
                '{',
                '}'
            ],
            expected_errors = [])

    def test_while_loop(self):
        self.assert_colobot_lint_result(
            source_file_lines = [
                'bool foo(int c, int d)',
                '{',
                '  while (true)',
                '  {'
                '    if (c == 1) return true;',
                '    if (d == 0) return false;',
                '  }',
                '}'
            ],
            expected_errors = [])

    def test_for_loop(self):
        self.assert_colobot_lint_result(
            source_file_lines = [
                'bool foo(int c, int d)',
                '{',
                '  for (int i = 0; i < 10; ++i)',
                '  {'
                '    if (c == 1) return true;',
                '    if (d == 0) return false;',
                '  }',
                '  return false;',
                '}'
            ],
            expected_errors = [])

    def test_initializer_list(self):
        self.assert_colobot_lint_result(
            source_file_lines = [
                '#include <vector>',
                'void foo()',
                '{',
                '  std::vector<int> vec{1,2,3,4,5};',
                '}'
            ],
            expected_errors = [])

    def test_lambda_function(self):
        self.assert_colobot_lint_result(
            source_file_lines = [
                'void foo()',
                '{',
                '  auto l = [](int x) { return x+1; };',
                '}'
            ],
            expected_errors = [])

if __name__ == '__main__':
    test_support.main()
