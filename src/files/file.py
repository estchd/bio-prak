import hashlib
import os
import gzip
from contextlib import ExitStack
from pathlib import Path
from shutil import rmtree

def function_type():
    pass

def calculate_file_md5(filePath):
    hash_md5 = hashlib.md5()
    with open(filePath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

class File:
    def __init__(self, path, computation, prerequisites = None, isGzip = True, multipleOutputs = None):
        if path == None or type(path) != str:
            raise Exception("file path needs to be str")

        if computation == None or type(computation) != type(function_type):
            raise Exception("computation needs to be function")
            
        if prerequisites == None:
            self.prerequisites = []
        elif type(prerequisites) == list:
            for prerequisite in prerequisites:
                if type(prerequisite) != File:
                    raise Exception("prerequisites needs to be a File or list of Files")
            self.prerequisites = prerequisites
        else:
            if type(prerequisites) != File:
                raise Exception("prerequisites needs to be a File or list of Files")
            self.prerequisites = [prerequisites]

        if multipleOutputs == None:
            self.multipleOutputs = []
        elif type(multipleOutputs) == list:
            for multipleOutput in multipleOutputs:
                if type(multipleOutput) != type(function_type) and type(multipleOutput) != type(self.__init__):
                    print("Type was", type(multipleOutput))
                    raise Exception("multiple outputs need to be function or a list of functions")

                self.multipleOutputs = multipleOutputs
        else:
            if type(multipleOutputs) != type(function_type) and type(multipleOutput) != type(self.__init__):
                raise Exception("multiple outputs need to be function or a list of functions")

            self.multipleOutputs = [multipleOutputs]

        self.path = path
        self.isGzip = isGzip
        
        self.computation = computation
        self.hash = None

    def get_possibly_gzip_path(self):
        if self.isGzip:
            return self.path + ".gz"
        else:
            return self.path

    def get_hash_path(self):
        return self.path + ".md5"
    
    def file_exists(self):
        return os.path.exists(self.get_possibly_gzip_path())
    
    def get_computed_file_hash(self):
        return calculate_file_md5(self.get_possibly_gzip_path())

    def get_saved_file_hash(self):
        try:
            with open(self.get_hash_path(), "rt") as file:
                return file.read()
        except:
            return None

    def save_file_hash(self, new_hash):
        with open(self.get_hash_path(), "wt") as file:
            file.write(new_hash)
        
    def needs_computing(self):
        if not self.file_exists():
            return True
            
        existing_hash = self.hash

        if existing_hash == None:
            existing_hash = self.get_saved_file_hash()
            
        if existing_hash == None:
            return True

        self.hash = existing_hash

        computed_file_hash = self.get_computed_file_hash()

        needs_recomputing = existing_hash != computed_file_hash

        return existing_hash != computed_file_hash
        
    def open_or_recompute(self):
        if self.needs_computing():
            self.recompute()

        return self.open()
    
    def recompute(self):
        for prerequisite in self.prerequisites:
            prerequisite.open_or_recompute()

        if self.multipleOutputs == []:
            try:
                os.remove(Path(self.path))
            except:
                pass
        else:
            rmtree(Path(self.path).parent)
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)

        self.computation(self.prerequisites, self.get_possibly_gzip_path(), self.multipleOutputs)

        if not self.file_exists():
            raise Exception("File doesnt exist after recomputing")

        self.save_file_hash(self.get_computed_file_hash())
    
    def open(self, write = False):
        mode = "rt"

        if write:
            mode = "wt"
        
        if self.isGzip:
            return gzip.open(self.get_possibly_gzip_path(), mode)
        else:
            return open(self.get_possibly_gzip_path(), mode)