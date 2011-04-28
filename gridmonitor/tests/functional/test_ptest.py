from gridmonitor.tests import *

class TestPtestController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='ptest', action='index'))
        # Test response...
