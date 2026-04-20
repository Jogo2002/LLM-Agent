
# docsum

A command-line tool for chat-based file utilities, including calculation, file listing, file reading, and pattern search, with optional LLM integration. Designed for extensibility and easy automation.

[![Doctests](https://github.com/yourusername/docsum/actions/workflows/doctest.yml/badge.svg)](https://github.com/yourusername/docsum/actions/workflows/doctest.yml)
[![Lint](https://github.com/yourusername/docsum/actions/workflows/lint.yml/badge.svg)](https://github.com/yourusername/docsum/actions/workflows/lint.yml)
[![Integration Tests](https://github.com/yourusername/docsum/actions/workflows/integration.yml/badge.svg)](https://github.com/yourusername/docsum/actions/workflows/integration.yml)
[![PyPI version](https://img.shields.io/pypi/v/docsum.svg)](https://pypi.org/project/docsum/)
[![codecov](https://codecov.io/gh/yourusername/docsum/branch/main/graph/badge.svg)](https://codecov.io/gh/yourusername/docsum)

![Animated terminal demo](demo.gif)

---

## Usage Examples

### markdown_compiler

This example shows how to use the chat tool to check if a project uses regular expressions. It demonstrates the tool's ability to analyze code and answer technical questions about a submodule.

```sh
$ cd markdown_compiler
$ chat
chat> does this project use regular expressions?
No. I grepped all of the python files for any uses of the `re` library and did not find any.
```

### ebay_scraper

This example demonstrates how the chat tool can summarize a project's purpose and answer legal/ethical questions about scraping, showing its usefulness for project documentation and compliance checks.

```sh
$ cd ebay_scraper
$ chat
chat> tell me about this project
The README says this project is designed to scrape product information off of ebay.
chat> is this legal?
Yes. It is generally legal to scrape webpages, but ebay offers an API that would be more efficient to use.
```

Each example above is good because it shows how the chat tool can answer real-world questions about code and project usage, making it valuable for both technical and non-technical users.

---

## Project Structure
- Command-line chat interface
- Calculate math expressions
- List files in directories
- Read file contents
- Search files with regex
- Optional LLM support via Groq

## Testing & Linting
- **Doctests**: Run `python -m doctest chat.py tools/cat.py tools/grep.py tools/ls.py`
- **Lint**: Run `flake8 .`
- **Integration Tests**: Run `python -m unittest discover`

---

For more, see the [docs](https://github.com/yourusername/docsum).
