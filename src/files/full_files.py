from src.files.file_category import FileCategory
from src.files.file import File
from src.files.original_files import OriginalFiles
from src.files.compute import copy_file

class FullFiles(FileCategory):
    def __init__(self, original_files, base_path = "data"):
        super().__init__("full", base_path)

        self.original_files = original_files
        
        self.genome_file = None
        self.annotations_file = None
        self.modifications_file = None

    def get_genome_file(self):
        if self.genome_file == None:
            self.genome_file = File(self.get_file_path_in_category("genome.fna"), copy_file, self.original_files.get_genome_file())

        return self.genome_file

    def get_annotations_file(self):
        if self.annotations_file == None:
            self.annotations_file = File(self.get_file_path_in_category("annotated.gtf"), copy_file, self.original_files.get_annotations_file())

        return self.annotations_file
    
    def get_modifications_file(self):
        if self.modifications_file == None:
            self.modifications_file = File(self.get_file_path_in_category("modifications.bed"), copy_file, self.original_files.get_modifications_file())

        return self.modifications_file