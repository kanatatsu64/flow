import os
import sys
import subprocess

def exec(command, suppress_error=False):
    env = os.environ.copy()
    stty = subprocess.run("stty size", capture_output=True, text=True, shell=True).stdout
    if not (stty == ""):
        lines, columns = stty.split()
        env["LINES"] = lines
        env["COLUMNS"] = columns

    result = subprocess.run(command, capture_output=True, text=True, shell=True, env=env)

    if (not (result.returncode == 0)) and (not suppress_error):
        print(command)
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
        sys.exit(1)

    return result.stdout

def usage():
    print("flow init <flow_name> [<base_branch>]", file=sys.stderr)
    print("flow start <flow_name>", file=sys.stderr)
    print("flow checkout <feature_name>", file=sys.stderr)
    print("flow delete <feature_name>", file=sys.stderr)
    print("flow feature-list", file=sys.stderr)
    print("flow flow-list", file=sys.stderr)
    print("flow push", file=sys.stderr)
    print("flow rebase", file=sys.stderr)
    sys.exit(1)

class Flow:
    def __init__(self, exec, print):
        self.exec = exec
        self.print = print

    def init(self, flow_name, base_branch = None):
        if base_branch is None:
            base_branch = f"develop/{flow_name}"
        elif base_branch == "develop":
            base_branch = f"develop/{flow_name}"
        elif base_branch == "feature":
            base_branch = f"feature/{flow_name}/base"
        
        if not self.exists(base_branch):
            self.exec(f"git checkout -b {base_branch}")
        
        self.set_flow_name(flow_name)
        self.set_base_branch(flow_name, base_branch)
        self.checkout_base()

    def start(self, flow_name):
        base_branch = self.get_base_branch(flow_name)

        if base_branch == "":
            usage()

        self.set_flow_name(flow_name)
        self.checkout_base()
    
    def checkout(self, feature_name=None):
        if feature_name is None:
            self.checkout_base()
            return

        self.set_feature_name(feature_name)

        flow_name = self.get_flow_name()
        base_branch = self.get_base_branch(flow_name)
        feature_branch = f"feature/{flow_name}/{feature_name}"
        exists = self.exists(feature_branch)

        if exists:
            self.exec(f"git checkout {feature_branch}")
        else:
            self.exec(f"git checkout -b {feature_branch} {base_branch}")
    
    def checkout_base(self):
        self.set_feature_name("")

        flow_name = self.get_flow_name()
        base_branch = self.get_base_branch(flow_name)

        self.exec(f"git checkout {base_branch}")

    def delete(self, feature_name):
        flow_name = self.get_flow_name()
        feature_branch = f"feature/{flow_name}/{feature_name}"

        if not self.exists(feature_branch):
            usage()

        self.exec(f"git branch -D {feature_branch}")
    
    def feature_list(self):
        flow_name = self.get_flow_name()
        pattern = f"feature/{flow_name}/*"
        lines = self.exec(f"git branch --list '{pattern}' | sed 's/^[* ] //'").splitlines()
        for line in lines:
            self.print(line.strip()[len(pattern)-1:])

    def flow_list(self):
        flow_names = self.get_flow_names()
        for flow_name in flow_names:
            self.print(flow_name)

    def diff(self, options):
        flow_name = self.get_flow_name()
        feature_name = self.get_feature_name()
        feature_branch = f"feature/{flow_name}/{feature_name}"
        base_branch = self.get_base_branch(flow_name)

        if options['test']:
            result = self.exec(f"git diff --stat {feature_branch} {base_branch}")
        else:
            result = self.exec(f"git diff --stat {feature_branch} {base_branch} -- ':(exclude)test/*'")

        if options['oneline']:
            self.print(result.splitlines()[-1])
        else:
            self.print(result)

    def push(self):
        flow_name = self.get_flow_name()
        feature_name = self.get_feature_name()
        feature_branch = f"feature/{flow_name}/{feature_name}"

        if feature_name == "":
            usage()
    
        self.exec(f"git push -u origin {feature_branch}")

    def exists(self, branch):
        return not (self.exec(f"git branch --list {branch}").strip() == "")
    
    def rebase(self):
        flow_name = self.get_flow_name()
        base_branch = self.get_base_branch(flow_name)
        
        self.exec(f"git fetch origin {base_branch}")
        self.exec(f"git rebase origin/{base_branch}")

    def reset(self):
        flow_name = self.get_flow_name()
        base_branch = self.get_base_branch(flow_name)
        
        self.exec(f"git reset {base_branch}")
    
    def set_flow_name(self, flow_name):
        self.exec(f"echo \"{flow_name}\" > .git/flow_current")

    def get_flow_name(self):
        return self.exec("cat .git/flow_current").strip()

    def get_flow_names(self):
        paths = self.exec("ls .git/flow/*", True).split()
        return [path.split("/")[-1].replace("_#_", "/") for path in paths]

    def set_base_branch(self, flow_name, base_branch):
        parsed_flow_name = flow_name.replace("/", "_#_")
        self.exec(f"mkdir -p .git/flow")
        self.exec(f"echo \"{base_branch}\" > .git/flow/{parsed_flow_name}")
    
    def get_base_branch(self, flow_name):
        parsed_flow_name = flow_name.replace("/", "_#_")
        return self.exec(f"cat .git/flow/{parsed_flow_name}", True).strip()

    def set_feature_name(self, feature_name):
        self.exec(f"echo \"{feature_name}\" > .git/flow_current_feature")
    
    def get_feature_name(self):
        return self.exec("cat .git/flow_current_feature").strip()

if __name__ == '__main__':
    flow = Flow(exec, print)
    args = sys.argv[1:]

    if len(args) == 0:
        usage()

    if args[0] == "init":
        if len(args) == 2:
            flow.init(args[1])
            sys.exit(0)
        elif len(args) == 3:
            flow.init(args[1], args[2])
            sys.exit(0)
    elif args[0] == "start":
        if len(args) == 2:
            flow.start(args[1])
            sys.exit(0)
    elif args[0] == "checkout":
        if len(args) == 1:
            flow.checkout()
            sys.exit(0)
        elif len(args) == 2:
            flow.checkout(args[1])
            sys.exit(0)
    elif args[0] == "delete":
        if len(args) == 2:
            flow.delete(args[1])
            sys.exit(0)
    elif args[0] == "feature-list":
        flow.feature_list()
        sys.exit(0)
    elif args[0] == "flow-list":
        flow.flow_list()
        sys.exit(0)
    elif args[0] == "diff":
        options = {
            "test": False,
            "oneline": False
        }
        if "--test" in args[1:]:
            options["test"] = True
        if "--oneline" in args[1:]:
            options["oneline"] = True
        flow.diff(options)
        sys.exit(0)
    elif args[0] == "push":
        flow.push()
        sys.exit(0)
    elif args[0] == "rebase":
        flow.rebase()
        sys.exit(0)
    elif args[0] == "reset":
        flow.reset()
        sys.exit(0)
    
    usage()