from src import MarkdownDirectory
import sys

if __name__ == "__main__":
    mydir = MarkdownDirectory(sys.argv[1])
    mydir.add_all_backlinks()
