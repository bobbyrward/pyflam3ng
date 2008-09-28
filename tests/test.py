#!/usr/bin/env python
import unittest
import glob
import os
import sys
import re
import functools

try:
    import pyflam3ng
except ImportError:
    sys.path.insert(0,
            os.path.join(os.path.dirname(__file__), '..'))
    import pyflam3ng

def run_test(name, test, result):
    print 'Running %s:' % name
    test(result)

def get_test_case(module_name):
    module = __import__(module_name)
    suite = unittest.defaultTestLoader.loadTestsFromModule(module)
    return functools.partial(run_test, module_name, suite)

def get_all_test_cases():
    test_module_files = os.listdir('tests')

    for module_filename in test_module_files:
        match = re.match('^(test_.*)\.py$', module_filename)
        if not match:
            continue

        yield get_test_case(match.group(1))


def create_suite():
    pyflam3_suite = unittest.TestSuite()
    for test in get_all_test_cases():
        pyflam3_suite.addTest(test)
    return pyflam3_suite


class SimpleTestRunner(object):
    def __init__(self):
        pass

    def run(self, test):
        result = unittest.TestResult()
        test(result)

        #if not result.wasSuccessful():
            #print '%d tests failed' % len(result.errors)
            #for (test, traceback) in result.errors:
                #print 'Error in:', test.id()
                #print traceback
        #else:
            #print 'All %d tests successful.' % result.testsRun


def main():
    if os.path.exists('test.failures'):
        os.remove('test.failures')

    if len(sys.argv) == 1:
        SimpleTestRunner().run(create_suite())
    else:
        runner = SimpleTestRunner()
        for test in sys.argv[1:]:
            runner.run(get_test_case('test_' + test))


if __name__ == '__main__':
    main()

