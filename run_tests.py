import unittest
import sys
import os

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import test cases
from tests.test_service import ServiceTestCase

def run_tests():
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(ServiceTestCase)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)

if __name__ == '__main__':
    run_tests() 