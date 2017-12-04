# -*- coding: utf-8 -*-

from .context import mas

import unittest


class MASTestSuite(unittest.TestCase):
    """COPDAI core test cases."""

    def setUp(self):
        self.agent = mas.Agent()

    def test_agent_default_state(self):
        self.assertEqual(self.agent.state, mas.AgentState.UNKNOWN)

    def tearDown(self):
        self.agent = None

if __name__ == '__main__':
    unittest.main()
