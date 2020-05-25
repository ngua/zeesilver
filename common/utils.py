import os


class cd:
    """
    Context manager utility to change directories and return to the original
    directory upon exit
    """
    def __init__(self, path):
        self.path = path
        self.original_path = os.getcwd()

    def __enter__(self):
        os.chdir(self.path)
        return self

    def __exit__(self, *args):
        os.chdir(self.original_path)
