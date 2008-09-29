##############################################################################
#  The Combustion Flame Engine - pyflam3ng
#  http://combustion.sourceforge.net
#  http://github.com/bobbyrward/pyflam3ng/tree/master
#
#  Copyright (C) 2007-2008 by Bobby R. Ward <bobbyrward@gmail.com>
#
#  The Combustion Flame Engine is free software; you can redistribute
#  it and/or modify it under the terms of the GNU General Public
#  License as published by the Free Software Foundation; either
#  version 3 of the License, or (at your option) any later version.
#
#  This library is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  Library General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this library; see the file COPYING.LIB.  If not, write to
#  the Free Software Foundation, Inc., 59 Temple Place - Suite 330,
#  Boston, MA 02111-1307, USA.
##############################################################################

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

        if result.wasSuccessful():
            print 'All %d tests successful.' % result.testsRun
        #if not result.wasSuccessful():
            #print '%d tests failed' % len(result.errors)
            #for (test, traceback) in result.errors:
                #print 'Error in:', test.id()
                #print traceback
        #else:


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

