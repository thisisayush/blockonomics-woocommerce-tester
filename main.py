import unittest

from tests import (
    BTCLiteJSWooCommerceTest, BTCLiteNoJSWooCommerceTest, BTCNormalJSWooCommerceTest, BTCNormalNoJSWooCommerceTest,
    BCHLiteJSWooCommerceTest, BCHLiteNoJSWooCommerceTest, BCHNormalJSWooCommerceTest, BCHNormalNoJSWooCommerceTest
)

test_cases = [
    BTCLiteJSWooCommerceTest, BTCLiteNoJSWooCommerceTest, BTCNormalJSWooCommerceTest, BTCNormalNoJSWooCommerceTest,
    BCHLiteJSWooCommerceTest, BCHLiteNoJSWooCommerceTest, BCHNormalJSWooCommerceTest, BCHNormalNoJSWooCommerceTest
]

loaded_tests = []

for case in test_cases:
    loaded_tests.append(unittest.TestLoader().loadTestsFromTestCase(case))

test_suite = unittest.TestSuite(loaded_tests)

unittest.TextTestRunner(
    failfast=True,
    warnings='ignore',
    verbosity=2
).run(test_suite)
