# Backlink Adder 🔗🐍
If a one-way link exists from one markdown document to another, this package will add a link in the other direction. 

To use, clone down this repo. Create a venv, activate it, and install the requirements. Then run `main.py` in the shell, supplying the address of your markdown folder as an argument.

For example, to add backlinks to the example docs in this repo you can run `python main.py ./example_docs/`.

Refresh the backlinks any time by running the script again. Ensure that no content exists below the 

```md
\n\n---\n\n
## Backlinks:\n
```

section, since the documents will be truncated when the script is run.