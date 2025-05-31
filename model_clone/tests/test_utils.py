from django.test import TestCase

from model_clone.utils import clean_value


class CleanValueTestCase(TestCase):
    def test_clean_value_with_single_digit(self):
        """Test cleaning value with single digit suffix."""
        result = clean_value("Test Copy 1", "Copy")
        self.assertEqual(result, "Test")

    def test_clean_value_with_multi_digit(self):
        """Test cleaning value with multi-digit suffix."""
        result = clean_value("Test Copy 10", "Copy")
        self.assertEqual(result, "Test")

        result = clean_value("Test Copy 123", "Copy")
        self.assertEqual(result, "Test")

    def test_clean_value_with_hyphen_separator(self):
        """Test cleaning value with hyphen separator."""
        result = clean_value("test-copy-1", "copy")
        self.assertEqual(result, "test")

        result = clean_value("test-copy-42", "copy")
        self.assertEqual(result, "test")

    def test_clean_value_case_insensitive(self):
        """Test that cleaning is case insensitive."""
        result = clean_value("Test COPY 1", "copy")
        self.assertEqual(result, "Test")

        result = clean_value("test copy 1", "COPY")
        self.assertEqual(result, "test")

    def test_clean_value_with_regex_special_characters(self):
        """Test cleaning value when suffix contains regex special characters."""
        result = clean_value("Test (Copy) 1", "(Copy)")
        self.assertEqual(result, "Test")

        result = clean_value("Test Copy+ 2", "Copy+")
        self.assertEqual(result, "Test")

        result = clean_value("Test Copy* 5", "Copy*")
        self.assertEqual(result, "Test")

        result = clean_value("Test Copy? 3", "Copy?")
        self.assertEqual(result, "Test")

        result = clean_value("Test Copy[1] 4", "Copy[1]")
        self.assertEqual(result, "Test")

    def test_clean_value_with_dots_and_brackets(self):
        """Test cleaning with complex regex characters."""
        result = clean_value("Test Copy.exe 1", "Copy.exe")
        self.assertEqual(result, "Test")

        result = clean_value("Test (v2.0) 15", "(v2.0)")
        self.assertEqual(result, "Test")

    def test_clean_value_no_match(self):
        """Test that value is unchanged when pattern doesn't match."""
        result = clean_value("Test Copy", "Copy")
        self.assertEqual(result, "Test Copy")

        result = clean_value("Test Different 1", "Copy")
        self.assertEqual(result, "Test Different 1")

        result = clean_value("Test Copy A", "Copy")
        self.assertEqual(result, "Test Copy A")

    def test_clean_value_partial_match(self):
        """Test that partial matches are not cleaned."""
        result = clean_value("Test Copying 1", "Copy")
        self.assertEqual(result, "Test Copying 1")

        result = clean_value("Test Copy Something 1", "Copy")
        self.assertEqual(result, "Test Copy Something 1")

    def test_clean_value_middle_of_string(self):
        """Test that pattern in middle of string is not cleaned."""
        result = clean_value("Test Copy 1 More", "Copy")
        self.assertEqual(result, "Test Copy 1 More")

    def test_clean_value_with_empty_suffix(self):
        """Test behavior with empty suffix."""
        result = clean_value("Test  1", "")
        self.assertEqual(result, "Test")

    def test_clean_value_with_space_before_suffix(self):
        """Test cleaning when there's a space before suffix."""
        result = clean_value("Test Copy 25", "Copy")
        self.assertEqual(result, "Test")

    def test_clean_value_with_hyphen_before_suffix(self):
        """Test cleaning when there's a hyphen before suffix."""
        result = clean_value("test-copy-99", "copy")
        self.assertEqual(result, "test")

    def test_clean_value_zero_digit(self):
        """Test cleaning with zero as digit."""
        result = clean_value("Test Copy 0", "Copy")
        self.assertEqual(result, "Test")

    def test_clean_value_leading_zeros(self):
        """Test cleaning with leading zeros in digits."""
        result = clean_value("Test Copy 001", "Copy")
        self.assertEqual(result, "Test")

        result = clean_value("Test Copy 010", "Copy")
        self.assertEqual(result, "Test")

    def test_clean_value_complex_example(self):
        """Test with a complex real-world example."""
        result = clean_value("my-awesome-slug-copy-42", "copy")
        self.assertEqual(result, "my-awesome-slug")

        result = clean_value("Product (v1.0) Copy 123", "(v1.0) Copy")
        self.assertEqual(result, "Product")
