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

    def exec(self, command, suppress_error=False):
        self.history.append(command)

        for key in self.caches.keys():
            if key == command:
                return self.caches[key]

    def print(self, message):
        self.history.append(f"echo \"{message}\"")

class TestFlow(unittest.TestCase):
    def test_flow_init_1(self):
        mock = ProcessMock()
        mock.default("git branch --list base_branch", "* base_branch")
        mock.default("cat .git/flow_current", "sample/1234")
        mock.default("cat .git/flow/sample_#_1234", "base_branch")
        flow = Flow(mock.exec, mock.print)

        flow_name = "sample/1234"
        base_branch = "base_branch"
        flow.init(flow_name, base_branch)

        commands = [
            'echo "sample/1234" > .git/flow_current',
            'echo "base_branch" > .git/flow/sample_#_1234',
            'echo "" > .git/flow_current_feature',
        ]
        history = mock.get("echo")
        self.assertEqual(len(history), 3)
        self.assertEqual(history[0], commands[0])
        self.assertEqual(history[1], commands[1])
        self.assertEqual(history[2], commands[2])

    def test_flow_init_2(self):
        mock = ProcessMock()
        mock.default("git branch --list develop/sample/1234", "* develop/sample/1234")
        mock.default("cat .git/flow_current", "sample/1234")
        mock.default("cat .git/flow/sample_#_1234", "develop/sample/1234")
        flow = Flow(mock.exec, mock.print)

        flow_name = "sample/1234"
        flow.init(flow_name)

        commands = [
            'echo "sample/1234" > .git/flow_current',
            'echo "develop/sample/1234" > .git/flow/sample_#_1234',
            'echo "" > .git/flow_current_feature',
        ]
        history = mock.get("echo")
        self.assertEqual(len(history), 3)
        self.assertEqual(history[0], commands[0])
        self.assertEqual(history[1], commands[1])
        self.assertEqual(history[2], commands[2])

    def test_flow_init_3(self):
        mock = ProcessMock()
        mock.default("git branch --list develop/sample/1234", "")
        mock.default("cat .git/flow_current", "sample/1234")
        mock.default("cat .git/flow/sample_#_1234", "develop/sample/1234")
        flow = Flow(mock.exec, mock.print)

        flow_name = "sample/1234"
        flow.init(flow_name)

        command = "git checkout -b develop/sample/1234"
        history = mock.get("git checkout -b")
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0], command)

        commands = [
            'echo "sample/1234" > .git/flow_current',
            'echo "develop/sample/1234" > .git/flow/sample_#_1234',
            'echo "" > .git/flow_current_feature',
        ]
        history = mock.get("echo")
        self.assertEqual(len(history), 3)
        self.assertEqual(history[0], commands[0])
        self.assertEqual(history[1], commands[1])
        self.assertEqual(history[2], commands[2])

    def test_flow_init_4(self):
        mock = ProcessMock()
        mock.default("git branch --list develop/sample/1234", "* develop/sample/1234")
        mock.default("cat .git/flow_current", "sample/1234")
        mock.default("cat .git/flow/sample_#_1234", "develop/sample/1234")
        flow = Flow(mock.exec, mock.print)

        flow_name = "sample/1234"
        flow.init(flow_name, "develop")

        commands = [
            'echo "sample/1234" > .git/flow_current',
            'echo "develop/sample/1234" > .git/flow/sample_#_1234',
            'echo "" > .git/flow_current_feature',
        ]
        history = mock.get("echo")
        self.assertEqual(len(history), 3)
        self.assertEqual(history[0], commands[0])
        self.assertEqual(history[1], commands[1])
        self.assertEqual(history[2], commands[2])

    def test_flow_init_5(self):
        mock = ProcessMock()
        mock.default("git branch --list feature/sample/1234/base", "* feature/sample/1234/base")
        mock.default("cat .git/flow_current", "sample/1234")
        mock.default("cat .git/flow/sample_#_1234", "feature/sample/1234/base")
        flow = Flow(mock.exec, mock.print)

        flow_name = "sample/1234"
        flow.init(flow_name, "feature")

        commands = [
            'echo "sample/1234" > .git/flow_current',
            'echo "feature/sample/1234/base" > .git/flow/sample_#_1234',
            'echo "" > .git/flow_current_feature',
        ]
        history = mock.get("echo")
        self.assertEqual(len(history), 3)
        self.assertEqual(history[0], commands[0])
        self.assertEqual(history[1], commands[1])
        self.assertEqual(history[2], commands[2])

    def test_start(self):
        mock = ProcessMock()
        mock.default("cat .git/flow_current", "sample/1234")
        mock.default("cat .git/flow/sample_#_1234", "base_branch")
        flow = Flow(mock.exec, mock.print)

        flow_name = "sample/1234"
        flow.start(flow_name)

        commands = [
            'echo "sample/1234" > .git/flow_current',
            'echo "" > .git/flow_current_feature',
        ]
        history = mock.get("echo")
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0], commands[0])
        self.assertEqual(history[1], commands[1])

    def test_delete_1(self):
        mock = ProcessMock()
        mock.default("cat .git/flow_current", "sample/1234")
        mock.default("git branch --list feature/sample/1234/new", " feature/sample/1234/new")
        flow = Flow(mock.exec, mock.print)

        feature_name = "new"
        flow.delete(feature_name)

        command = 'git branch -D feature/sample/1234/new'
        history = mock.get("git branch -D")
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0], command)

    def test_delete_2(self):
        mock = ProcessMock()
        mock.default("cat .git/flow_current", "sample/1234")
        mock.default("cat .git/flow_current_feature", "new")
        mock.default("cat .git/flow/sample_#_1234", "base_branch")
        mock.default("git branch --list feature/sample/1234/new", " feature/sample/1234/new")
        flow = Flow(mock.exec, mock.print)

        flow.delete()

        command = 'git checkout base_branch'
        history = mock.get("git checkout")
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0], command)

        command = 'git branch -D feature/sample/1234/new'
        history = mock.get("git branch -D")
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0], command)

    def test_flow_checkout_1(self):
        mock = ProcessMock()
        mock.default("cat .git/flow_current", "sample/1234")
        mock.default("cat .git/flow/sample_#_1234", "base_branch")
        mock.default("git branch --list feature/sample/1234/new", "")
        flow = Flow(mock.exec, mock.print)

        feature_name = "new"
        flow.checkout(feature_name)

        command = "git checkout -b feature/sample/1234/new base_branch"
        history = mock.get("git checkout")
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0], command)

    def test_flow_checkout_2(self):
        mock = ProcessMock()
        mock.default("cat .git/flow_current", "sample/1234")
        mock.default("cat .git/flow/sample_#_1234", "base_branch")
        mock.default("git branch --list feature/sample/1234/new", "* feature/sample/1234/new")
        flow = Flow(mock.exec, mock.print)

        feature_name = "new"
        flow.checkout(feature_name)

        command = "git checkout feature/sample/1234/new"
        history = mock.get("git checkout")
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0], command)

    def test_flow_checkout_3(self):
        mock = ProcessMock()
        mock.default("cat .git/flow_current", "sample/1234")
        mock.default("cat .git/flow/sample_#_1234", "base_branch")
        flow = Flow(mock.exec, mock.print)

        flow.checkout()

        command = "git checkout base_branch"
        history = mock.get("git checkout")
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0], command)
    
    def test_flow_exists_1(self):
        mock = ProcessMock()
        mock.default("git branch --list feature/sample/1234/new", "* feature/sample/1234/new")
        flow = Flow(mock.exec, mock.print)

        branch = "feature/sample/1234/new"
        exists = flow.exists(branch)

        self.assertTrue(exists)

    def test_flow_exists_2(self):
        mock = ProcessMock()
        mock.default("git branch --list feature/sample/1234/new", "")
        flow = Flow(mock.exec, mock.print)

        branch = "feature/sample/1234/new"
        exists = flow.exists(branch)

        self.assertFalse(exists)

    def test_flow_push(self):
        mock = ProcessMock()
        mock.default("cat .git/flow_current", "sample/1234")
        mock.default("cat .git/flow_current_feature", "new")
        flow = Flow(mock.exec, mock.print)

        flow.push()

        command = "git push -u origin feature/sample/1234/new"
        history = mock.get("git push")
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0], command)

    def test_flow_rebase(self):
        mock = ProcessMock()
        mock.default("cat .git/flow_current", "sample/1234")
        mock.default("cat .git/flow/sample_#_1234", "base_branch")
        flow = Flow(mock.exec, mock.print)

        flow.rebase()

        commands = [
            "git fetch origin base_branch",
            "git rebase origin/base_branch"
        ]
        history = mock.get("git")
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0], commands[0])
        self.assertEqual(history[1], commands[1])

    def test_flow_reset(self):
        mock = ProcessMock()
        mock.default("cat .git/flow_current", "sample/1234")
        mock.default("cat .git/flow/sample_#_1234", "base_branch")
        flow = Flow(mock.exec, mock.print)

        flow.reset()

        commands = [
            "git reset base_branch",
        ]
        history = mock.get("git")
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0], commands[0])
    
    def test_flow_feature_list(self):
        mock = ProcessMock()
        mock.default("cat .git/flow_current", "sample/1234")
        mock.default("git branch --list 'feature/sample/1234/*' | sed 's/^[* ] //'", "feature/sample/1234/new\nfeature/sample/1234/old")
        flow = Flow(mock.exec, mock.print)

        flow.feature_list()

        commands = [
            'echo "new"',
            'echo "old"'
        ]
        history = mock.get("echo")
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0], commands[0])
        self.assertEqual(history[1], commands[1])

    def test_flow_flow_list(self):
        mock = ProcessMock()
        mock.default("ls .git/flow/*", ".git/flow/sample .git/flow/sample_#_1234")
        flow = Flow(mock.exec, mock.print)

        flow.flow_list()

        commands = [
            'echo "sample"',
            'echo "sample/1234"'
        ]
        history = mock.get("echo")
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0], commands[0])
        self.assertEqual(history[1], commands[1])

if __name__ == '__main__':
    unittest.main()