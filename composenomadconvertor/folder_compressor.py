import tarfile
import os

class FolderCompressor(object):
    def __init__(self, path,dest_path):
        self.path = path
        self.dest_path = dest_path
        self.cwd = os.getcwd()

    def archive(self):
        
        with tarfile.open(self.dest_path, "x:gz") as tar:
            os.chdir(self.path)
            for name in os.listdir(os.getcwd()):
                tar.add(name)
            os.chdir(self.cwd)