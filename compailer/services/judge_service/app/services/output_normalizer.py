"""
Output normalization and comparison for test case validation
"""
import logging
import re
from typing import Tuple

logger = logging.getLogger(__name__)


class OutputNormalizer:
    """Normalize and compare program outputs"""
    
    @staticmethod
    def _normalize_whitespace(text: str, mode: str = "strict") -> str:
        """
        Normalize whitespace in text
        
        Modes:
        - 'strict': Strip leading/trailing, collapse internal whitespace
        - 'lines': Normalize each line separately, ignore empty lines
        - 'lenient': Only fix CRLF and basic whitespace
        """
        if not text:
            return ""
        
        # Always fix CRLF
        text = text.replace('\r\n', '\n')
        text = text.replace('\r', '\n')
        
        if mode == "strict":
            # Strip each line, remove empty lines, join
            lines = [line.strip() for line in text.split('\n')]
            lines = [line for line in lines if line]  # Remove empty
            return '\n'.join(lines).strip()
        
        elif mode == "lines":
            # Normalize each line, preserve structure
            lines = [line.rstrip() for line in text.split('\n')]
            text = '\n'.join(lines)
            return text.strip()
        
        else:  # lenient
            # Just strip globally
            return text.strip()
    
    @staticmethod
    def _parse_numbers(text: str) -> Tuple[list, bool]:
        """
        Try to extract numbers from text
        Returns (numbers, is_purely_numeric)
        """
        # Pattern: any number (int or float)
        pattern = r'-?\d+\.?\d*|-?\d*\.\d+'
        numbers = re.findall(pattern, text)
        
        if numbers:
            try:
                nums = [float(n) for n in numbers]
                return nums, True
            except ValueError:
                return [], False
        
        return [], False
    
    @staticmethod
    def compare(
        actual: str,
        expected: str,
        normalize_mode: str = "lines",
        fuzzy: bool = False,
        tolerance: float = 1e-6
    ) -> Tuple[bool, str]:
        """
        Compare actual vs expected output
        
        Args:
            actual: Actual program output
            expected: Expected output
            normalize_mode: 'strict', 'lines', or 'lenient'
            fuzzy: Allow numeric fuzzy matching
            tolerance: Tolerance for floating point comparison
        
        Returns:
            (match: bool, reason: str)
        """
        if not actual and not expected:
            return True, "Both empty"
        
        if not actual or not expected:
            return False, "One output is empty"
        
        # Try exact match first
        actual_norm = OutputNormalizer._normalize_whitespace(actual, normalize_mode)
        expected_norm = OutputNormalizer._normalize_whitespace(expected, normalize_mode)
        
        if actual_norm == expected_norm:
            return True, "Exact match"
        
        # Try line-by-line comparison
        actual_lines = actual_norm.split('\n')
        expected_lines = expected_norm.split('\n')
        
        if len(actual_lines) != len(expected_lines):
            return False, f"Line count mismatch: {len(actual_lines)} vs {len(expected_lines)}"
        
        # Check each line
        for i, (act, exp) in enumerate(zip(actual_lines, expected_lines)):
            if act == exp:
                continue  # Line matches
            
            # Try fuzzy numeric comparison if enabled
            if fuzzy:
                act_nums, act_numeric = OutputNormalizer._parse_numbers(act)
                exp_nums, exp_numeric = OutputNormalizer._parse_numbers(exp)
                
                if act_numeric and exp_numeric and len(act_nums) == len(exp_nums):
                    # Compare numbers with tolerance
                    if all(abs(a - e) <= tolerance for a, e in zip(act_nums, exp_nums)):
                        continue  # Numbers match within tolerance
            
            # Line doesn't match
            return False, f"Line {i+1} mismatch:\n  Actual:   '{act}'\n  Expected: '{exp}'"
        
        return True, "All lines match"
    
    @staticmethod
    def format_output(text: str, max_length: int = 1000) -> str:
        """Format output for display (truncate if too long)"""
        if not text:
            return "(empty)"
        
        text = text.strip()
        if len(text) > max_length:
            text = text[:max_length] + "\n... (truncated)"
        
        # Escape special characters for display
        text = text.replace('\n', '\\n')
        text = text.replace('\r', '\\r')
        text = text.replace('\t', '\\t')
        
        return text
