from src.files.file_category import FileCategory
from src.files.file import File
from src.files.compute import download_fna, download_gtf, download_m6A

class OriginalFiles(FileCategory):
    def __init__(self, base_path = "data"):
        super().__init__("original", base_path)

        self.genome_file = None
        self.annotations_file = None
        self.modifications_file = None

    def get_genome_file(self):
        if self.genome_file == None:
            self.genome_file = File(self.get_file_path_in_category("GCF_000001405.40_GRCh38.p14_genomic.fna"), download_fna)

        return self.genome_file

    def get_annotations_file(self):
        if self.annotations_file == None:
            self.annotations_file = File(self.get_file_path_in_category("GCF_000001405.40_GRCh38.p14_genomic.gtf"), download_gtf)

        return self.annotations_file
    
    def get_modifications_file(self):
        if self.modifications_file == None:
            self.modifications_file = File(self.get_file_path_in_category("hg38.m6A"), download_m6A)

        return self.modifications_file