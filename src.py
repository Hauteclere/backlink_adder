from pathlib import Path, PosixPath
import markdown
import lxml.html
import os

class MarkdownDirectory:
    """Handles operations for a directory of markdown files.

    This class is responsible for managing a collection of markdown files in a
    directory. It keeps track of the files and their interconnections (links).

    Attributes:
        p_path (Path): The path to the directory.
        files (dict): A dictionary mapping from file paths to corresponding 
            `MarkdownFile` instances.
    """

    def __init__(self, path_string: str):
        """Creates a new MarkdownDirectory instance.

        This constructor takes the path to a directory, and creates a 
        `MarkdownFile` instance for each markdown file in the directory. It 
        also builds a map of links between the files.

        Args:
            path_string (str): The path to the directory.
        """
        self.p_path = Path(path_string)
        self.files = {
            resolved_path: MarkdownFile(self, eachpath) 
            for eachpath in self.p_path.rglob('*.md') 
            for resolved_path in [(self.p_path.parent.resolve() / str(eachpath)).resolve()]
        }

    # Needs to be a property because the links in the docs are updated at runtime.
    @property
    def link_map(self):
        return {
            resolved_path: self.files[resolved_path].links 
            for resolved_path in self.files.keys()
        }

    def add_all_backlinks(self):
        for file in self.files.values():
            file.add_backlinks()

class MarkdownFile:
    """Represents a markdown file within a directory.

    This class encapsulates the details of a markdown file, including its path,
    the directory it belongs to, its document tree, its first heading, and its links. 
    It also provides methods for working with the file's content, such as extracting links 
    and adding backlinks.

    Attributes:
        path (PosixPath): The file's path.
        markdown_dir (MarkdownDirectory): The directory the file is part of.
        doctree (lxml.html.HtmlElement): The file's document tree.
        heading (str): The first heading in the file.
        links (set): A set of links in the file.
    """

    def __init__(self, markdown_dir: MarkdownDirectory, path: PosixPath):
        """Initializes a new instance of the MarkdownFile class.

        Reads the file's content, parses it into a document tree, extracts the
        first heading, and identifies all markdown links within the file.

        Args:
            markdown_dir (MarkdownDirectory): The directory the file is part of.
            path (PosixPath): The file's path.
        """
        self.path = path
        self.markdown_dir = markdown_dir

        headings = self.doctree.xpath('//h1//text()')
        if headings:
            self.heading = headings[0]
        else:
            self.heading = self.path.name

    # Needs to be a property because the links in the docs are updated at runtime.
    @property
    def doctree(self):
        with open(self.path) as file:
            return lxml.html.fromstring(markdown.markdown(file.read()))

    # Needs to be a property because the links in the docs are updated at runtime.
    @property 
    def links(self):
        return set(
            filter(
                lambda somelink: os.path.splitext(str(somelink).split('#')[0])[1].lower() == '.md', 
                map(
                    self.get_absolute_path,
                    (eachlink.get('href') for eachlink in self.doctree.xpath('//a'))
                )
            )
        )

    def get_absolute_path(self, somepath: str):
        """Converts a link to an absolute path.

        If the link is a relative path, it is resolved to an absolute path
        relative to the file's directory. If the link is already an absolute
        path, it is returned as is.

        Args:
            somepath (str): The link to convert.

        Returns:
            Path: The absolute path of the link, or None if `somepath` is not a
            string or is empty.
        """
        if not isinstance(somepath, str) or not len(somepath):
            return None
        if somepath[0] == "/":
            return Path(somepath)
        return (self.path.parent.resolve() / somepath.split('#')[0]).resolve()

    def add_backlinks(self):
        """Adds backlinks to the markdown file.

        A backlink is a reverse of a link from another file that points to this 
        file. This method identifies all such links, and appends them to the end of the
        file under a "Backlinks" heading.
        """

        with open(self.path, 'r+') as file:
            content = file.read()
            index = content.find("\n\n---\n\n## Backlinks:\n")
            if index != -1:
                file.seek(index)
                file.truncate()

        with open(self.path, 'a+') as file:

            file.writelines(
                [
                    "\n\n---\n\n",
                    "## Backlinks:\n",
                    *[
                        f"- [{self.markdown_dir.files[each_backlink].heading}]({os.path.relpath(each_backlink, self.path.parent)})\n" 
                        for each_backlink in {
                            key for key, value in self.markdown_dir.link_map.items() if self.path in value
                        } - self.links
                    ]
                ]
            )
