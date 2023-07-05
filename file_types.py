import sys
import json

################
# Parent Classes
################

class JsonFile():
    def __init__(self, path: str):
        try:
            with open(path, encoding= "utf-8") as f:
                self._file = json.load(f)
        except FileNotFoundError:
            print(f"{path} not found")
            sys.exit()
        else:
            print(f"{path} found!")
            self._initData()


    def get_file(self):
        return self._file

    def set_file(self, file: list[str]):
        self._file = file

    def _initData(self):
        pass

    file = property(get_file, set_file)

# Header files are immediatedly converted into a list of strings.
class CFile():
    instances = []
    def __init__(self, path: str):
        try:
            with open(path, encoding= "utf-8", newline='\n') as f:
                self._file = f.readlines()
        except FileNotFoundError:
            print(f"{path} not found!")
            sys.exit()
        else:
            self.__class__.instances.append(self)
            self._backup = self._file.copy()
            self._path = path
            print(f"{path} found!")

    # returns -1 if no matching string was found
    def findLine(self, string: str, start = 0) -> int:
        for idx, line in enumerate(self._file):
            if string in line and idx > start:
                return idx
        return -1

    # returns -1 if no matching string was found
    def findLineRegex(self, regstr: str, start = 0) -> int:
        pattern = re.compile(regstr)
        for idx, line in enumerate(self._file):
            match = re.search(regstr, line)
            if match and idx > start:
                return idx
        return -1

    def insertBlankLine(self, idx: int) -> None:
        self._file.insert(idx, "\n")

    def writeBack(self):
        try:
            with open(self._path, 'w', encoding='utf-8', newline='\n') as f:
                f.writelines(self._file)
        except IOError:
            print(f"Could not write to {self._path}")

    def restoreFile(self):
        self._file = self._backup.copy()
        self.writeBack()

    def _handleEndif(self, idx: int):
        if self.get_line(idx) == "#endif\n":
            idx += 1
            self.insertBlankLine(idx)       # insert extra blankline to create gap to following mons
        return idx

    def get_file(self):
        return self._file

    def set_file(self, file: list[str]):
        self._file = file

    def get_line(self, idx: int):
        return self._file[idx]

    def set_line(self, idx: int, line: str):
        self._file[idx] = line

    # this overrides the lines, useful for updating exisiting lines
    def set_lines(self, idx: int, string: str):
        lines = string.splitlines(keepends=True)
        for i in range(len(lines)):
            self.set_line(idx+i, lines[i])

    def get_backup(self):
        return self._backup

    backup = property(get_backup)
    file = property(get_file, set_file)

class HeaderFile(CFile):
    def __init__(self, path: str):
        super().__init__(path)

class SourceFile(CFile):
    def __init__(self, path: str):
        super().__init__(path)