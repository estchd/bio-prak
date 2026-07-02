from src.files.file_category import FileCategory
from src.files.file import File
from src.files.renamed_files import RenamedFiles
from src.files.compute import bgzip_file

class BgzippedFiles(FileCategory):
    def __init__(self, renamed_files, base_path = "data"):
        super().__init__("bgzip", base_path)

        self.renamed_files = renamed_files
        
        self.genome_file = None

    def get_files(self):
        return [self.get_genome_file()]

    def get_files_dict(self):
        return {"genome": self.get_genome_file()}
    
    def get_genome_file(self):
        if self.genome_file == None:
            self.genome_file = File(self.get_file_path_in_category("genome_chr8.fna.bgz"), bgzip_file, self.renamed_files.get_genome_file(), False)

        return self.genome_file