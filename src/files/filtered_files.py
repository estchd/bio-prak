from src.files.file_category import FileCategory
from src.files.file import File
from src.files.full_files import FullFiles
from src.files.compute import filter_fna, filter_gtf, filter_bed

class FilteredFiles(FileCategory):
    def __init__(self, full_files, base_path = "data"):
        super().__init__("filtered", base_path)

        self.full_files = full_files
        
        self.genome_file = None
        self.annotations_file = None
        self.modifications_file = None

    def get_genome_file(self):
        if self.genome_file == None:
            self.genome_file = File(self.get_file_path_in_category("genome_NC_000008.11.fna"), filter_fna, self.full_files.get_genome_file())

        return self.genome_file

    def get_annotations_file(self):
        if self.annotations_file == None:
            self.annotations_file = File(self.get_file_path_in_category("annotated_NC_000008.11.gtf"), filter_gtf, self.full_files.get_annotations_file())

        return self.annotations_file
    
    def get_modifications_file(self):
        if self.modifications_file == None:
            self.modifications_file = File(self.get_file_path_in_category("modifications_chr8.bed"), filter_bed, self.full_files.get_modifications_file())

        return self.modifications_file