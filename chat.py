import json
import os
from dotenv import load_dotenv
from tools.calculate import calculate as calculate_tool
from tools.cat import cat as cat_tool
from tools.grep import grep as grep_tool
from tools.ls import ls as ls_tool

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
        """
        self.model = "llama-3.1-8b-instant"
        self.messages = [
            {
                "role": "system",
                "content": "Write the output in 1-2 sentences",
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
        """
        return calculate_tool(expression)

    def ls(self, path=None):
        """List files in the current directory or relative directory.

        >>> chat = Chat()
        >>> 'files' in chat.ls(None)
        True
        >>> 'error' in chat.ls('nonexistent_dir')
        True
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
        """
        return grep_tool(regex, filepath)

    def run_conversation(self, user_prompt):
        """Run a conversation through the configured Groq client.

        >>> from unittest.mock import Mock
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
                    "description": "List files in the current directory or in a specified directory",
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
                    "description": "Read the contents of a file",
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


def main():
    """Start the chat command line interface."""
    if os.getenv("GROQ_API_KEY") is None:
        print("Groq client is not configured. Only local tools are available.")

    chat = Chat()

    try:
        while True:
            user_input = input("chat>> ")
            if user_input.startswith("/"):
                parts = user_input[1:].split()
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
                    if len(args) != 2:
                        print("Usage: /grep <regex> <filepath>")
                        continue
                    print(chat.grep(args[0], args[1]))
                elif command == "cat":
                    if len(args) != 1:
                        print("Usage: /cat <filename>")
                        continue
                    print(chat.cat(args[0]))
                else:
                    print(f"Unknown command: {command}")
            else:
                print(chat.run_conversation(user_input))
    except KeyboardInterrupt:
        print()


if __name__ == "__main__":
    main()

    


