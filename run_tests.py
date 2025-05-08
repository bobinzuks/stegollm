#!/usr/bin/env python3
"""
Test runner for StegoLLM.

This script runs the tests for the StegoLLM project.
"""

import os
import sys
import pytest

def main():
    """Run the tests."""
    # Add the project root to the path
    project_root = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, project_root)
    
    # Run the tests
    args = ["-xvs"]
    if len(sys.argv) > 1:
        args.extend(sys.argv[1:])
    else:
        args.append("tests")
    
    return pytest.main(args)

if __name__ == "__main__":
    sys.exit(main())