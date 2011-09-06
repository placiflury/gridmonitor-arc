from gridmonitor.tests import *

class TestGridController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='grid', action='index'))
        # Test response...
