import unittest
from datetime import datetime
from HtmlTestRunner import HTMLTestRunner
from tests.test_auth import AuthTestCase

def run_tests():
    # Create a test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(AuthTestCase)
    
    # Generate timestamp for unique report name
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Configure the HTML report
    runner = HTMLTestRunner(
        output='test_reports',
        report_name=f'test_report_{timestamp}',
        combine_reports=True,
        report_title='Auth API Test Report'
    )
    
    # Run the tests
    runner.run(suite)

if __name__ == '__main__':
    run_tests() 