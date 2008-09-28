from __future__ import with_statement
import traceback

def print_test_name(test):
    def callit(*args, **kwargs):
        try:
            retval= test(*args, **kwargs)
        except:
            with open('test.failures', 'a') as fd:
                print >>fd, 'FAILURE IN %s:' %  test.__name__
                print >>fd, traceback.format_exc()
                print >>fd

            print '\tX %s' %  test.__name__
            raise
        else:
            print '\tO %s' % test.__name__

    return callit

