from src.files.file_category import FileCategory
from src.files.file import File
from src.files.renamed_files import RenamedFiles
from src.files.compute import assemble_regions

class AssembledRegionFiles(FileCategory):
    def __init__(self, renamed_files, base_path = "data"):
        super().__init__("regions", base_path)

        self.renamed_files = renamed_files
        
        self._3utr_file = None
        self._5utr_file = None
        self._5utr_start_file = None
        self.cds_file = None
        self.coding_exons_file = None
        self.coding_introns_file = None
        self.exons_file = None
        self.introns_file = None
        self.non_coding_exons_file = None
        self.non_coding_introns_file = None
            
    def get_files(self):
        return [self.get_3utr_file(), self.get_5utr_file(), self.get_5utr_start_file(), self.get_cds_file(), self.get_coding_exons_file(), self.get_coding_introns_file(), self.get_exons_file(), self.get_introns_file(), self.get_non_coding_exons_file(), self.get_non_coding_introns_file()]

    def get_files_dict(self):
        return {"3utr": self.get_3utr_file(), "5utr": self.get_5utr_file(), "5utr_start": self.get_5utr_start_file(), "cds": self.get_cds_file(), "coding_exons": self.get_coding_exons_file(), "coding_introns": self.get_coding_introns_file(), "exons": self.get_exons_file(), "introns": self.get_introns_file(), "non_coding_exons": self.get_non_coding_exons_file(), "non_coding_introns": self.get_non_coding_introns_file()}

    def multiple_outputs(self):
        return [self.get_3utr_file, self.get_5utr_file, self.get_5utr_start_file, self.get_cds_file, self.get_coding_exons_file, self.get_coding_introns_file, self.get_exons_file, self.get_introns_file, self.get_non_coding_exons_file, self.get_non_coding_introns_file]
    
    def get_3utr_file(self):
        if self._3utr_file == None:
            self._3utr_file = File(self.get_file_path_in_category("region_3utr.bed"), assemble_regions, self.renamed_files.get_annotations_file(), False, self.multiple_outputs())

        return self._3utr_file

    def get_5utr_file(self):
        if self._5utr_file == None:
            self._5utr_file = File(self.get_file_path_in_category("region_5utr.bed"), assemble_regions, self.renamed_files.get_annotations_file(), False, self.multiple_outputs())

        return self._5utr_file

    def get_5utr_start_file(self):
        if self._5utr_start_file == None:
            self._5utr_start_file = File(self.get_file_path_in_category("region_5utr_start.bed"), assemble_regions, self.renamed_files.get_annotations_file(), False, self.multiple_outputs())

        return self._5utr_start_file

        
    def get_cds_file(self):
        if self.cds_file == None:
            self.cds_file = File(self.get_file_path_in_category("region_cds.bed"), assemble_regions, self.renamed_files.get_annotations_file(), False, self.multiple_outputs())

        return self.cds_file

    def get_coding_exons_file(self):
        if self.coding_exons_file == None:
            self.coding_exons_file = File(self.get_file_path_in_category("region_codingexons.bed"), assemble_regions, self.renamed_files.get_annotations_file(), False, self.multiple_outputs())

        return self.coding_exons_file
        
    def get_coding_introns_file(self):
        if self.coding_introns_file == None:
            self.coding_introns_file = File(self.get_file_path_in_category("region_codingintrons.bed"), assemble_regions, self.renamed_files.get_annotations_file(), False, self.multiple_outputs())

        return self.coding_introns_file

    def get_exons_file(self):
        if self.exons_file == None:
            self.exons_file = File(self.get_file_path_in_category("region_exons.bed"), assemble_regions, self.renamed_files.get_annotations_file(), False, self.multiple_outputs())

        return self.exons_file

    def get_introns_file(self):
        if self.introns_file == None:
            self.introns_file = File(self.get_file_path_in_category("region_introns.bed"), assemble_regions, self.renamed_files.get_annotations_file(), False, self.multiple_outputs())

        return self.introns_file

    def get_non_coding_exons_file(self):
        if self.non_coding_exons_file == None:
            self.non_coding_exons_file = File(self.get_file_path_in_category("region_noncodingexons.bed"), assemble_regions, self.renamed_files.get_annotations_file(), False, self.multiple_outputs())

        return self.non_coding_exons_file

    def get_non_coding_introns_file(self):
        if self.non_coding_introns_file == None:
            self.non_coding_introns_file = File(self.get_file_path_in_category("region_noncodingintrons.bed"), assemble_regions, self.renamed_files.get_annotations_file(), False, self.multiple_outputs())

        return self.non_coding_introns_file
        