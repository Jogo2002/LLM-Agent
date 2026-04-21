import json
import os
from dotenv import load_dotenv
from tools.calculate import calculate as calculate_tool
from tools.cat import cat as cat_tool
from tools.grep import grep as grep_tool
from tools.ls import ls as ls_tool
from tools.compact import compact as compact_tool

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

        >>> from unittest.mock import Mock
        >>> mock_client = Mock()
        >>> mock_completion = Mock()
        >>> mock_message = Mock()
        >>> mock_message.content = 'Hello back!'
        >>> mock_choice = Mock()
        >>> mock_choice.message = mock_message
        >>> mock_completion.choices = [mock_choice]
        >>> mock_client.chat.completions.create.return_value = mock_completion
        >>> chat = Chat(client=mock_client)
        >>> chat.send_message('hello', temperature=0.0)
        'Hello back!'
        >>> import os
        >>> os.environ["GROQ_API_KEY"] = ""
        >>> chat = Chat(client=None)
        >>> chat.send_message('hello')
        'No Groq client configured.'
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

        >>> from pathlib import Path
        >>> test_path = Path('chat_cat_test.txt')
        >>> test_path.write_text('hello', encoding='utf-8')
        5
        >>> chat = Chat()
        >>> chat.cat('chat_cat_test.txt')
        'hello'
        >>> test_path.unlink()
        >>> chat.cat('chat_cat_test.txt')
        "Error: [Errno 2] No such file or directory: 'chat_cat_test.txt'"
        """
        return cat_tool(filename)

    def grep(self, regex, filepath):
        """Search files matching a glob pattern for a regex.

        >>> from pathlib import Path
        >>> Path('chat_grep_1.txt').write_text('apple\\nbanana\\n', encoding='utf-8')
        13
        >>> Path('chat_grep_2.txt').write_text('apple pie\\ncherry\\n', encoding='utf-8')
        17
        >>> chat = Chat()
        >>> result = chat.grep('apple', 'chat_grep_*.txt')
        >>> 'apple' in result
        True
        >>> Path('chat_grep_1.txt').unlink()
        >>> Path('chat_grep_2.txt').unlink()
        >>> chat.grep('notfound', 'chat_grep_*.txt')
        ''
        """
        return grep_tool(regex, filepath)

    def run_conversation(self, user_prompt):
        """Run a conversation through the configured Groq client.
        Doctests for this method use mocking to simulate Groq client responses, without the need for an actual API key.

        >>> from unittest.mock import Mock 
        >>> mock_client = Mock()
        >>> mock_client = Mock()
        >>> mock_response = Mock()
        >>> mock_message = Mock()
        >>> mock_message.content = 'I can help with that.'
        >>> mock_message.tool_calls = None
        >>> mock_choice = Mock()
        >>> mock_choice.message = mock_message
        >>> mock_response.choices = [mock_choice]
        >>> mock_client.chat.completions.create.return_value = mock_response
        >>> chat = Chat(client=mock_client)
        >>> chat.run_conversation('hello')
        'I can help with that.'
        >>> # Test tool calling path
        >>> import json
        >>> mock_tool_call = Mock()
        >>> mock_tool_call.id = 'call_123'
        >>> mock_tool_call.function.name = 'calculate'
        >>> mock_tool_call.function.arguments = '{"expression": "2+2"}'
        >>> mock_message_with_tools = Mock()
        >>> mock_message_with_tools.content = ''
        >>> mock_message_with_tools.tool_calls = [mock_tool_call]
        >>> mock_response_with_tools = Mock()
        >>> mock_response_with_tools.choices = [Mock()]
        >>> mock_response_with_tools.choices[0].message = mock_message_with_tools
        >>> mock_second_response = Mock()
        >>> mock_second_message = Mock()
        >>> mock_second_message.content = 'The result is 4'
        >>> mock_second_choice = Mock()
        >>> mock_second_choice.message = mock_second_message
        >>> mock_second_response.choices = [mock_second_choice]
        >>> mock_client.chat.completions.create.side_effect = [mock_response_with_tools, mock_second_response]
        >>> chat.run_conversation('calculate 2+2')
        'The result is 4'
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

        >>> from unittest.mock import Mock
        >>> mock_client = Mock()
        >>> mock_response = Mock()
        >>> mock_message = Mock()
        >>> mock_message.content = 'Summary: User asked about files and tools.'
        >>> mock_choice = Mock()
        >>> mock_choice.message = mock_message
        >>> mock_response.choices = [mock_choice]
        >>> mock_client.chat.completions.create.return_value = mock_response
        >>> chat = Chat(client=mock_client)
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


def main():
    """Start the chat command line interface.

    >>> import builtins
    >>> import io
    >>> import contextlib
    >>> import os
    >>> import sys

    >>> original_input = builtins.input
    >>> original_getenv = os.getenv
    >>> original_chat_class = Chat

    >>> class FakeChat:
    ...     def calculate(self, expression):
    ...         return f"CALC:{expression}"
    ...     def ls(self, path=None):
    ...         return f"LS:{path}"
    ...     def grep(self, regex, filepath):
    ...         return f"GREP:{regex}:{filepath}"
    ...     def cat(self, filename):
    ...         return f"CAT:{filename}"
    ...     def run_conversation(self, user_prompt):
    ...         return f"CHAT:{user_prompt}"
    ...     def compact(self):
    ...         return "Conversation compacted."

    >>> builtins.input = lambda prompt: next(inputs)
    >>> os.getenv = lambda key: None
    >>> sys.modules[__name__].Chat = FakeChat

    >>> inputs = iter([
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
    ...     "/compact",
    ...     "/unknown cmd",
    ...     "hello",
    ... ])

    >>> output = io.StringIO()
    >>> with contextlib.redirect_stdout(output):
    ...     try:
    ...         main()
    ...     except StopIteration:
    ...         print()

    >>> print(output.getvalue(), end="")
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
    Conversation compacted.
    Unknown command: unknown
    CHAT:hello
    <BLANKLINE>

    >>> builtins.input = original_input
    >>> os.getenv = original_getenv
    >>> sys.modules[__name__].Chat = original_chat_class
    """
    if os.getenv("GROQ_API_KEY") is None:
        print("Groq client is not configured. Only local tools are available.")

    chat = Chat()

    try:
        while True:
            user_input = input("chat>> ")
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
                elif command == "compact":
                    print(chat.compact())
                else:
                    print(f"Unknown command: {command}")
            else:
                print(chat.run_conversation(user_input))
    except KeyboardInterrupt:
        print()


if __name__ == "__main__":
    main()

    


