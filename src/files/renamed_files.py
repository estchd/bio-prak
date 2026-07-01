from src.files.file_category import FileCategory
from src.files.file import File
from src.files.filtered_files import FilteredFiles
from src.files.compute import copy_file, rename_fna, rename_gtf

class RenamedFiles(FileCategory):
    def __init__(self, filtered_files, base_path = "data"):
        super().__init__("renamed", base_path)

        self.filtered_files = filtered_files
        
        self.genome_file = None
        self.annotations_file = None
        self.modifications_file = None

    def get_genome_file(self):
        if self.genome_file == None:
            self.genome_file = File(self.get_file_path_in_category("genome_chr8.fna"), rename_fna, self.filtered_files.get_genome_file())

        return self.genome_file

    def get_annotations_file(self):
        if self.annotations_file == None:
            self.annotations_file = File(self.get_file_path_in_category("annotated_chr8.gtf"), rename_gtf, self.filtered_files.get_annotations_file())

        return self.annotations_file
    
    def get_modifications_file(self):
        if self.modifications_file == None:
            self.modifications_file = File(self.get_file_path_in_category("modifications_chr8.bed"), copy_file, self.filtered_files.get_modifications_file())

        return self.modifications_file