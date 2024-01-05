import unittest
from flow import *

class ProcessMock:
    def __init__(self):
        self.history = []
        self.caches = {}

    def clear(self):
        self.history = []
    
    def get(self, pattern):
        return list(filter(lambda command: command.startswith(pattern), self.history))

    def default(self, command, value=None):
        self.caches[command] = value

    def exec(self, command):
        self.history.append(command)

        for key in self.caches.keys():
            if key == command:
                return self.caches[key]

class TestFlow(unittest.TestCase):
    def test_flow_start_1(self):
        mock = ProcessMock()
        flow = Flow(mock.exec)

        flow_name = "sample/1234"
        base_branch = "base_branch"
        flow.start(flow_name, base_branch)

        commands = [
            'echo "sample/1234" > .git/flow_current',
            'echo "base_branch" > .git/flow/sample_1234'
        ]
        history = mock.get("echo")
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0], commands[0])
        self.assertEqual(history[1], commands[1])

    def test_flow_start_2(self):
        mock = ProcessMock()
        flow = Flow(mock.exec)

        flow_name = "sample/1234"
        flow.start(flow_name)

        commands = [
            'echo "sample/1234" > .git/flow_current',
            'echo "develop/sample/1234" > .git/flow/sample_1234'
        ]
        history = mock.get("echo")
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0], commands[0])
        self.assertEqual(history[1], commands[1])

    def test_flow_checkout_1(self):
        mock = ProcessMock()
        mock.default("cat .git/flow_current", "sample/1234")
        mock.default("cat .git/flow/sample_1234", "base_branch")
        mock.default("git show-ref", False)
        flow = Flow(mock.exec)

        feature_name = "new"
        flow.checkout(feature_name)

        command = "git checkout -b feature/sample/1234/new base_branch"
        history = mock.get("git checkout")
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0], command)

    def test_flow_checkout_2(self):
        mock = ProcessMock()
        mock.default("cat .git/flow_current", "sample/1234")
        mock.default("cat .git/flow/sample_1234", "base_branch")
        mock.default("git show-ref --quiet refs/heads/feature/sample/1234/new", True)
        flow = Flow(mock.exec)

        feature_name = "new"
        flow.checkout(feature_name)

        command = "git checkout feature/sample/1234/new"
        history = mock.get("git checkout")
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0], command)

    def test_flow_checkout_3(self):
        mock = ProcessMock()
        mock.default("cat .git/flow_current", "sample/1234")
        mock.default("cat .git/flow/sample_1234", "base_branch")
        flow = Flow(mock.exec)

        flow.checkout()

        command = "git checkout base_branch"
        history = mock.get("git checkout")
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0], command)
    
    def test_flow_exists_1(self):
        mock = ProcessMock()
        mock.default("git show-ref --quiet refs/heads/feature/sample/1234/new", True)
        flow = Flow(mock.exec)

        branch = "feature/sample/1234/new"
        exists = flow.exists(branch)

        self.assertTrue(exists)

    def test_flow_exists_2(self):
        mock = ProcessMock()
        mock.default("git show-ref --quiet refs/heads/feature/sample/1234/new", False)
        flow = Flow(mock.exec)

        branch = "feature/sample/1234/new"
        exists = flow.exists(branch)

        self.assertFalse(exists)

    def test_flow_push(self):
        mock = ProcessMock()
        mock.default("cat .git/flow_current", "sample/1234")
        mock.default("cat .git/flow_current_feature", "new")
        flow = Flow(mock.exec)

        flow.push()

        command = "git push -u origin feature/sample/1234/new"
        history = mock.get("git push")
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0], command)

    def test_flow_rebase(self):
        mock = ProcessMock()
        mock.default("cat .git/flow_current", "sample/1234")
        mock.default("cat .git/flow/sample_1234", "base_branch")
        flow = Flow(mock.exec)

        flow.rebase()

        commands = [
            "git fetch origin base_branch",
            "git rebase origin/base_branch"
        ]
        history = mock.get("git")
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0], commands[0])
        self.assertEqual(history[1], commands[1])
    
    def test_flow_list(self):
        mock = ProcessMock()
        mock.default("cat .git/flow_current", "sample/1234")
        mock.default("git branch --list 'feature/sample/1234/*' | tr '*' ' '", " feature/sample/1234/new\n feature/sample/1234/old")
        flow = Flow(mock.exec)

        flow.list()

        commands = [
            'echo "new"',
            'echo "old"'
        ]
        history = mock.get("echo")
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0], commands[0])
        self.assertEqual(history[1], commands[1])

if __name__ == '__main__':
    unittest.main()