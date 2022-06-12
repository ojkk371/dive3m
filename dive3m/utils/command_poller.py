import shlex
import subprocess


class CommandPoller(object):
    def __init__(self, command):
        self.command = shlex.split(command)

    def __enter__(self):
        self.popen = subprocess.Popen(
                self.command, stdout=subprocess.PIPE, universal_newlines=True
        )
        return self

    def __exit__(self, type, value, trace_back):
        self.popen.stdout.close()
        self.popen.wait()

    def __iter__(self):
        return iter(self.popen.stdout.readline, "")


if __name__ == "__main__":
    
    with CommandPoller("nvidia-smi -l 1") as poller:
        for out in poller:
            print(out)
