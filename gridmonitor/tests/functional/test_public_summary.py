from gridmonitor.tests import *

class TestPublicSummaryController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='public_summary', action='index'))
        # Test response...
