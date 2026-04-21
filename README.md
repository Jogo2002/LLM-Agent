
# Interactive LLM Chat Aent

A command-line tool for chat-based file utilities, including calculation, file listing, file reading, and pattern search, with optional LLM integration. Designed for extensibility and easy automation.

[![Doctests](https://github.com/Jogo2002/LLM-Agent/actions/workflows/doctest.yml/badge.svg)](https://github.com/Jogo2002/LLM-Agent/actions/workflows/doctest.yml)
[![Lint](https://github.com/Jogo2002/LLM-Agent/actions/workflows/lint.yml/badge.svg)](https://github.com/Jogo2002/LLM-Agent/actions/workflows/lint.yml)
[![Integration Tests](https://github.com/Jogo2002/LLM-Agent/actions/workflows/integration.yml/badge.svg)](https://github.com/Jogo2002/LLM-Agent/actions/workflows/integration.yml)
[![PyPI version](https://img.shields.io/pypi/v/llm-agent.svg)](https://pypi.org/project/llm-agent/)
[![codecov](https://codecov.io/gh/Jogo2002/LLM-Agent/branch/main/graph/badge.svg)](https://codecov.io/gh/Jogo2002/LLM-Agent)

![Animated terminal demo](demo.gif)

---

## Usage Examples

### markdown_compiler

This example shows how to use the chat tool to check if a project uses regular expressions. It demonstrates the tool's ability to analyze code and answer technical questions about a submodule.

```sh
$ cd markdown_compiler
$ chat
chat>> does this project use regular expressions?
No. I grepped all of the python files for any uses of the `re` library and did not find any.
```

### ebay_scraper

This example demonstrates how the chat tool can summarize a project's purpose and answer legal/ethical questions about scraping, showing its usefulness for project documentation and compliance checks.

```sh
$ cd ebay_scraper
$ chat
chat>> tell me about this project
The README says this project is designed to scrape product information off of ebay.
chat>> is this legal?
Yes. It is generally legal to scrape webpages, but ebay offers an API that would be more efficient to use.
```


### Personal Website

This example shows how the chat tool can quickly analyze and answer questions about your portfolio projects without manually reading through files.

```sh
$ cd jogo2002.github.io
$ chat
chat>> what programming languages does this project use?
This project uses HTML, CSS, and JavaScript. The index.html file imports a stylesheet.css and includes JavaScript functionality.
chat>> are there any broken links in the markdown?
I found 3 markdown files. None of them contain broken http links.
```

Each example above is useful, as shows how the chat tool can answer real-world questions about code and project usage, making it valuable for both technical and non-technical users.

---

## Project Structure
- Command-line chat interface
- Tools 
    - Calculate math expressions
    - List files in directories
    - Read file contents
    - Search files with regex
    - Summarize information

## Testing & Linting
- **Doctests**: Run `python -m doctest chat.py tools/cat.py tools/grep.py tools/ls.py`
- **Lint**: Run `flake8 .`
- **Integration Tests**: Run `python -m unittest discover`

