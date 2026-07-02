from src.files.original_files import OriginalFiles
from src.files.full_files import FullFiles
from src.files.filtered_files import FilteredFiles
from src.files.renamed_files import RenamedFiles
from src.files.bgzipped_files import BgzippedFiles
from src.files.assembled_region_files import AssembledRegionFiles
from src.files.assembled_region_fasta_files import AssembledRegionFastaFiles
from src.files.assembled_region_intersects_files import AssembledRegionIntersectsFiles
from src.files.assembled_region_local_intersects_files import AssembledRegionLocalIntersectsFiles
from src.files.assembled_region_local_intersects_assembled_files import AssembledRegionLocalIntersectsAssembledFiles


class Files:
    def __init__(self, base_path = "data"):
        self.base_path = base_path

        self.original_files = None
        self.full_files = None
        self.filtered_files = None
        self.renamed_files = None
        self.bgzipped_files = None
        self.assembled_region_files = None
        self.assembled_region_fasta_files = None
        self.assembled_region_intersects_files = None
        self.assembled_region_local_intersects_files = None
        self.assembled_region_local_intersects_assembled_files = None

    def get_original_files(self):
        if self.original_files == None:
            self.original_files = OriginalFiles(self.base_path)

        return self.original_files

    def get_full_files(self):
        if self.full_files == None:
            self.full_files = FullFiles(self.get_original_files(), self.base_path)

        return self.full_files

    def get_filtered_files(self):
        if self.filtered_files == None:
            self.filtered_files = FilteredFiles(self.get_full_files(), self.base_path)

        return self.filtered_files

    def get_renamed_files(self):
        if self.renamed_files == None:
            self.renamed_files = RenamedFiles(self.get_filtered_files(), self.base_path)

        return self.renamed_files

    def get_bgzipped_files(self):
        if self.bgzipped_files == None:
            self.bgzipped_files = BgzippedFiles(self.get_renamed_files(), self.base_path)

        return self.bgzipped_files

    def get_assembled_region_files(self):
        if self.assembled_region_files == None:
            self.assembled_region_files = AssembledRegionFiles(self.get_renamed_files(), self.base_path)

        return self.assembled_region_files

    def get_assembled_region_fasta_files(self):
        if self.assembled_region_fasta_files == None:
            self.assembled_region_fasta_files = AssembledRegionFastaFiles(self.get_bgzipped_files(), self.get_assembled_region_files(), self.base_path)

        return self.assembled_region_fasta_files

    def get_assembled_region_intersects_files(self):
        if self.assembled_region_intersects_files == None:
            self.assembled_region_intersects_files = AssembledRegionIntersectsFiles(self.get_renamed_files(), self.get_assembled_region_files(), self.base_path)

        return self.assembled_region_intersects_files

    def get_assembled_region_local_intersects_files(self):
        if self.assembled_region_local_intersects_files == None:
            self.assembled_region_local_intersects_files = AssembledRegionLocalIntersectsFiles(self.get_assembled_region_intersects_files(), self.base_path)

        return self.assembled_region_local_intersects_files

    def get_assembled_region_local_intersects_assembled_files(self):
        if self.assembled_region_local_intersects_assembled_files == None:
            self.assembled_region_local_intersects_assembled_files = AssembledRegionLocalIntersectsAssembledFiles(self.get_assembled_region_local_intersects_files(), self.base_path)

        return self.assembled_region_local_intersects_assembled_files

files = None

def get_files():
    global files
    if files == None:
        files = Files("data")

    return files