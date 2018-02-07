from UnitTests.test_FlowBlocks import TestFlowBlocks
from UnitTests.test_Variables import TestVar
from UnitTests.test_File import TestFileGrabber
from UnitTests.test_ThreadPool import TestThreadPool
import unittest

if __name__ == '__main__':
    loader = unittest.TestLoader()
    suite = unittest.TestSuite((
        loader.loadTestsFromTestCase(TestFlowBlocks),
        loader.loadTestsFromTestCase(TestVar),
        loader.loadTestsFromTestCase(TestFileGrabber),
        loader.loadTestsFromTestCase(TestThreadPool),
        ))

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)