from pathlib import Path

class FileCategory:
    def __init__(self, category_name, base_path = "data"):
        self.name = category_name
        self.base_path = base_path

    def get_file_path_in_category(self, file_name):
        return str(Path(self.base_path).joinpath(self.name).joinpath(file_name))