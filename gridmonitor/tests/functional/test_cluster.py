from gridmonitor.tests import *

class TestClusterController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='cluster', action='index'))
        # Test response...
