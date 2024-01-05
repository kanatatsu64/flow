import sys
import subprocess

class Flow:
    def __init__(self, exec):
        self.exec = exec

    def start(self, flow_name, base_branch = None):
        if base_branch is None:
            base_branch = f"develop/{flow_name}"
        
        if not self.exists(base_branch):
            raise "base branch not found"
        
        parsed_flow_name = flow_name.replace("/", "_")

        self.exec(f"mkdir -p .git/flow")
        self.exec(f"echo \"{flow_name}\" > .git/flow_current")
        self.exec(f"echo \"{base_branch}\" > .git/flow/{parsed_flow_name}")
    
    def checkout(self, feature_name=None):
        if feature_name is None:
            self.checkout_base()
            return

        self.exec(f"echo \"{feature_name}\" > .git/flow_current_feature")

        flow_name = self.get_flow_name()
        base_branch = self.get_base_branch()
        feature_branch = f"feature/{flow_name}/{feature_name}"
        exists = self.exists(feature_branch)

        if exists:
            self.exec(f"git checkout {feature_branch}")
        else:
            self.exec(f"git checkout -b {feature_branch} {base_branch}")
    
    def checkout_base(self):
        self.exec(f"echo \"\" > .git/flow_current_feature")

        base_branch = self.get_base_branch()

        self.exec(f"git checkout {base_branch}")
    
    def list(self):
        flow_name = self.get_flow_name()
        pattern = f"feature/{flow_name}/*"
        lines = self.exec(f"git branch --list '{pattern}' | tr '*' ' '").splitlines()
        for line in lines:
            print(line.strip()[len(pattern)-1:])

    def push(self):
        flow_name = self.get_flow_name()
        feature_name = self.get_feature_name()
        feature_branch = f"feature/{flow_name}/{feature_name}"

        if feature_name == "":
            raise "not in feature branch"
    
        self.exec(f"git push -u origin {feature_branch}")

    def exists(self, branch):
        return not (self.exec(f"git branch --list {branch}").strip() == "")
    
    def rebase(self):
        base_branch = self.get_base_branch()
        
        self.exec(f"git fetch origin {base_branch}")
        self.exec(f"git rebase origin/{base_branch}")
    
    def get_flow_name(self):
        return self.exec("cat .git/flow_current").strip()
    
    def get_base_branch(self):
        flow_name = self.get_flow_name()
        parsed_flow_name = flow_name.replace("/", "_")
        return self.exec(f"cat .git/flow/{parsed_flow_name}").strip()
    
    def get_feature_name(self):
        return self.exec("cat .git/flow_current_feature").strip()

def exec(command):
    return subprocess.run(command, capture_output=True, text=True, shell=True).stdout

if __name__ == '__main__':
    flow = Flow(exec)
    args = sys.argv[1:]

    if args[0] == "start":
        if len(args) == 2:
            flow.start(args[1])
        elif len(args) == 3:
            flow.start(args[1], args[2])
    elif args[0] == "checkout":
        if len(args) == 1:
            flow.checkout()
        elif len(args) == 2:
            flow.checkout(args[1])
    elif args[0] == "list":
        flow.list()
    elif args[0] == "push":
        flow.push()
    elif args[0] == "rebase":
        flow.rebase()