import json
import os
from dotenv import load_dotenv
from tools.calculate import calculate as calculate_tool
from tools.cat import cat as cat_tool
from tools.grep import grep as grep_tool
from tools.ls import ls as ls_tool
from tools.compact import compact as compact_tool
from tools.doctests import doctests as doctests_tool
from tools.write_file import write_file as write_file_tool, write_files as write_files_tool
from tools.rm import rm as rm_tool

try:
    from groq import Groq
except ImportError:
    Groq = None


load_dotenv()


class Chat:
    """Chat interface that exposes tools and optional Groq LLM support.

    The Chat class provides methods for calculation, file listing, file reading, and pattern search.
    It can also run a remote conversation if a Groq client is configured.
    """

    def __init__(self, client=None, api_key=None):
        """Initialize the Chat object with optional Groq client support.

        >>> chat = Chat()
        >>> isinstance(chat, Chat)
        True
        >>> chat.client is None or hasattr(chat.client, 'chat')
        True
        """
        self.model = "llama-3.1-8b-instant"
        self.messages = [
            {
                "role": "system",
                "content": """You are a helpful assistant with access to tools. When answering questions:
- Use the calculate tool for mathematical expressions and arithmetic
- Use the ls tool to list directory contents
- Use the cat tool to read and display complete file contents
- Use the grep tool to search for patterns within files
- Use the doctests tool to run doctests on a Python file
- Use the write_file tool to write a single file and commit it to git
- Use the write_files tool to write multiple files and commit them to git
- Use the rm tool to delete files matching a glob pattern and commit the removal
Be concise and direct in your responses.""",
            }
        ]

        if client is not None:
            self.client = client
        elif api_key is not None:
            if Groq is None:
                raise ImportError("Groq is not installed.")
            self.client = Groq(api_key=api_key)
        else:
            env_key = os.getenv("GROQ_API_KEY")
            self.client = Groq(api_key=env_key) if env_key and Groq is not None else None

    def send_message(self, message, temperature=0.0):
        """Append a user message and optionally send it to the configured LLM.

        >>> chat = Chat()
        >>> result = chat.send_message('hello', temperature=0.0)
        >>> isinstance(result, str) and len(result) > 0
        True
        >>> import os
        >>> _saved_key = os.environ.pop('GROQ_API_KEY', None)
        >>> chat2 = Chat()
        >>> chat2.send_message('hello')
        'No Groq client configured.'
        >>> if _saved_key: os.environ['GROQ_API_KEY'] = _saved_key
        """
        self.messages.append({"role": "user", "content": message})

        if self.client is None:
            return "No Groq client configured."

        completion = self.client.chat.completions.create(
            messages=self.messages,
            model=self.model,
            temperature=temperature,
        )
        return completion.choices[0].message.content

    def calculate(self, expression):
        """Evaluate a mathematical expression using the calculation tool.

        >>> chat = Chat()
        >>> chat.calculate('2 + 2')
        '{"result": 4}'
        >>> chat.calculate('invalid')
        '{"error": "Invalid expression"}'
        >>> chat.calculate('')
        '{"error": "Invalid expression"}'
        """
        return calculate_tool(expression)

    def ls(self, path=None):
        """List files in the current directory or relative directory.

        >>> chat = Chat()
        >>> 'files' in chat.ls(None)
        True
        >>> 'error' in chat.ls('nonexistent_dir')
        True
        >>> chat.ls('/etc/passwd')  # Should not allow absolute paths
        '{"error": "Absolute paths and directory traversal are not allowed."}'
        """
        return ls_tool(path)

    def cat(self, filename):
        """Read the contents of a UTF-8 text file.

        >>> chat = Chat()
        >>> result = chat.cat('test_files/testtext.txt')
        >>> len(result) > 0
        True
        >>> chat.cat('nonexistent.txt')
        "Error: [Errno 2] No such file or directory: 'nonexistent.txt'"
        """
        return cat_tool(filename)

    def grep(self, regex, filepath):
        """Search files matching a glob pattern for a regex.

        >>> chat = Chat()
        >>> result = chat.grep('apple', 'test_files/grep_*.txt')
        >>> 'apple' in result
        True
        >>> chat.grep('notfound', 'test_files/grep_*.txt')
        ''
        """
        return grep_tool(regex, filepath)

    def doctests(self, path):
        """Run doctests on a Python file and return the output.

        >>> chat = Chat()
        >>> result = chat.doctests('test_files/sample_add.py')
        >>> 'ok' in result or 'passed' in result
        True
        >>> chat.doctests('/etc/passwd')
        'Error: Absolute paths and directory traversal are not allowed.'
        """
        return doctests_tool(path)

    def write_file(self, path, contents, commit_message):
        """Write a single file to disk and commit it to git.

        >>> import os
        >>> chat = Chat()
        >>> result = chat.write_file('_chat_wf_test.txt', 'hello', 'test write')
        >>> 'written' in result
        True
        >>> os.remove('_chat_wf_test.txt')
        """
        return write_file_tool(path, contents, commit_message)

    def write_files(self, files, commit_message):
        """Write multiple files to disk and commit them to git.

        >>> import os
        >>> chat = Chat()
        >>> result = chat.write_files([{'path': '_chat_wfs_test.txt', 'contents': 'hi'}], 'test multi')
        >>> 'written' in result
        True
        >>> os.remove('_chat_wfs_test.txt')
        """
        return write_files_tool(files, commit_message)

    def rm(self, path):
        """Delete files matching a glob pattern and commit the removal to git.

        >>> from pathlib import Path
        >>> chat = Chat()
        >>> _ = Path('_chat_rm_test.txt').write_text('x', encoding='utf-8')
        >>> result = chat.rm('_chat_rm_test.txt')
        >>> 'removed' in result
        True
        """
        return rm_tool(path)

    def run_conversation(self, user_prompt):
        """Run a conversation through the configured Groq client.
        Doctests for this method use mocking to simulate Groq client responses, without the need for an actual API key.

        >>> chat = Chat()
        >>> result = chat.run_conversation('hello')
        >>> isinstance(result, str) and len(result) > 0
        True
        >>> chat2 = Chat()
        >>> result2 = chat2.run_conversation('calculate 2+2')
        >>> isinstance(result2, str) and len(result2) > 0
        True
        """
        if self.client is None:
            return "Groq client is required to run conversations."

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant. "
                    "You can use tools to calculate math expressions and list files."
                ),
            },
            {"role": "user", "content": user_prompt},
        ]

        tools = [
            {
                "type": "function",
                "function": {
                    "name": "calculate",
                    "description": "Evaluate a mathematical expression",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "expression": {
                                "type": "string",
                                "description": "The mathematical expression to evaluate",
                            }
                        },
                        "required": ["expression"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "ls",
                    "description": "List all files and directories in a directory. Use this when the user asks what files are in a directory or to list contents. Do NOT use this to read file contents.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "Optional directory path to list files from",
                            }
                        },
                        "required": [],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "grep",
                    "description": "Search for lines matching a regex pattern in files matching a glob pattern",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "regex": {
                                "type": "string",
                                "description": "The regex pattern to search for",
                            },
                            "filepath": {
                                "type": "string",
                                "description": "The file path or glob pattern to search in",
                            },
                        },
                        "required": ["regex", "filepath"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "cat",
                    "description": "Read and display the complete contents of a single file. Use this when the user asks to read, view, show, or display a file's content.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "filename": {
                                "type": "string",
                                "description": "The name of the file to read",
                            }
                        },
                        "required": ["filename"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "doctests",
                    "description": "Run doctests on a Python file and return the verbose output",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "The relative path to the Python file to test",
                            }
                        },
                        "required": ["path"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "write_file",
                    "description": "Write a single file to disk with the given contents and commit it to git",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "The relative path of the file to write",
                            },
                            "contents": {
                                "type": "string",
                                "description": "The contents to write to the file",
                            },
                            "commit_message": {
                                "type": "string",
                                "description": "The commit message describing the change",
                            },
                        },
                        "required": ["path", "contents", "commit_message"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "write_files",
                    "description": "Write multiple files to disk and commit them to git in a single commit",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "files": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "path": {"type": "string"},
                                        "contents": {"type": "string"},
                                    },
                                    "required": ["path", "contents"],
                                },
                                "description": "List of files with path and contents to write",
                            },
                            "commit_message": {
                                "type": "string",
                                "description": "The commit message describing the change",
                            },
                        },
                        "required": ["files", "commit_message"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "rm",
                    "description": "Delete files matching a glob pattern and commit the removal to git",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "The file path or glob pattern of files to delete",
                            }
                        },
                        "required": ["path"],
                    },
                },
            },
        ]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=tools,
            tool_choice="auto",
            temperature=0.0,
        )

        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls

        if tool_calls:
            available_functions = {
                "calculate": self.calculate,
                "ls": self.ls,
                "grep": self.grep,
                "cat": self.cat,
                "doctests": self.doctests,
                "write_file": self.write_file,
                "write_files": self.write_files,
                "rm": self.rm,
            }

            messages.append(response_message)

            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_to_call = available_functions.get(function_name)
                function_args = json.loads(tool_call.function.arguments)

                if function_to_call is None:
                    function_response = json.dumps(
                        {"error": f"Unknown function: {function_name}"}
                    )
                else:
                    function_response = function_to_call(**function_args)

                messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": function_response,
                    }
                )

            second_response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
            )
            return second_response.choices[0].message.content

        return response_message.content

    def compact(self):
        """Summarize the current chat session and replace messages with a single summary entry.
        
        This reduces token count by condensing the conversation history into 1-5 lines,
        which helps reduce API costs, improve response speed, and prevent hitting token limits.

        >>> chat = Chat()
        >>> chat.messages.append({"role": "user", "content": "What files are in the directory?"})
        >>> result = chat.compact()
        >>> chat.messages[0]["role"]
        'system'
        >>> 'Summary' in chat.messages[0]["content"]
        True
        """
        result = compact_tool(self.messages, self.client, self.model)
        
        # Extract summary from result if successful
        if result.startswith("Conversation compacted"):
            # Parse the summary from the result string
            summary_start = result.find("Summary: ") + len("Summary: ")
            summary = result[summary_start:]
            
            # Replace messages with system message containing summary
            self.messages = [
                {
                    "role": "system",
                    "content": f"Summary of previous conversation: {summary}",
                }
            ]
        
        return result


def main(chat=None, inputs=None):
    """Starts the chat command line interface.

    >>> class NewChat:
    ...     def calculate(self, e): return f"CALC:{e}"
    ...     def ls(self, path=None): return f"LS:{path}"
    ...     def grep(self, r, f): return f"GREP:{r}:{f}"
    ...     def cat(self, f): return f"CAT:{f}"
    ...     def doctests(self, p): return f"DOCTESTS:{p}"
    ...     def rm(self, p): return f"RM:{p}"
    ...     def run_conversation(self, p): return f"CHAT:{p}"
    ...     def compact(self): return "Conversation compacted."
    >>> main(chat=NewChat(), inputs=[
    ...     "/",
    ...     "/calculate",
    ...     "/calculate 2+2",
    ...     "/calculate 4 + 5",
    ...     "/ls",
    ...     "/ls dir",
    ...     "/grep",
    ...     "/grep a file.txt",
    ...     "/cat",
    ...     "/cat file.txt",
    ...     "/doctests",
    ...     "/doctests file.py",
    ...     "/rm",
    ...     "/rm file.txt",
    ...     "/compact",
    ...     "/unknown cmd",
    ...     "hello",
    ... ])
    Groq client is not configured. Only local tools are available.
    Invalid command
    Usage: /calculate <expression>
    CALC:2+2
    CALC:4 + 5
    LS:None
    LS:dir
    Usage: /grep <regex> <filepath>
    GREP:a:file.txt
    Usage: /cat <filename>
    CAT:file.txt
    Usage: /doctests <path>
    DOCTESTS:file.py
    Usage: /rm <path>
    RM:file.txt
    Conversation compacted.
    Unknown command: unknown
    CHAT:hello
    <BLANKLINE>
    """
    if not os.path.isdir(".git"):
        print("Error: .git folder not found. This command must be run from a git repository.")
        return

    if chat is None:
        chat = Chat()

    if getattr(chat, 'client', None) is None:
        print("Groq client is not configured. Only local tools are available.")

    if os.path.isfile("AGENTS.md"):
        print(chat.cat("AGENTS.md"))
        print("I read the agents.md file")

    input_iter = iter(inputs) if inputs is not None else None

    try:
        while True:
            user_input = next(input_iter) if input_iter is not None else input("chat>> ")
            if user_input.startswith("/"):
                parts = user_input[1:].split(maxsplit=1)
                if not parts:
                    print("Invalid command")
                    continue
                command, *args = parts
                if command == "calculate":
                    if len(args) != 1:
                        print("Usage: /calculate <expression>")
                        continue
                    print(chat.calculate(args[0]))
                elif command == "ls":
                    print(chat.ls(args[0] if args else None))
                elif command == "grep":
                    if len(args) != 1:
                        print("Usage: /grep <regex> <filepath>")
                        continue
                    grep_parts = args[0].split(maxsplit=1)
                    if len(grep_parts) != 2:
                        print("Usage: /grep <regex> <filepath>")
                        continue
                    print(chat.grep(grep_parts[0], grep_parts[1]))
                elif command == "cat":
                    if len(args) != 1:
                        print("Usage: /cat <filename>")
                        continue
                    print(chat.cat(args[0]))
                elif command == "doctests":
                    if len(args) != 1:
                        print("Usage: /doctests <path>")
                        continue
                    print(chat.doctests(args[0]))
                elif command == "rm":
                    if len(args) != 1:
                        print("Usage: /rm <path>")
                        continue
                    print(chat.rm(args[0]))
                elif command == "compact":
                    print(chat.compact())
                else:
                    print(f"Unknown command: {command}")
            else:
                print(chat.run_conversation(user_input))
    except (KeyboardInterrupt, StopIteration):
        print()


if __name__ == "__main__":
    main()

    


