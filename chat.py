from groq import Groq
from dotenv import load_dotenv
import os
import re
import json
import glob
from pathlib import PurePath

load_dotenv()

class Chat:
    """
    >>> chat = Chat()
    >>> isinstance(chat, Chat)
    True
    """

    def __init__(self):
        self.model = "llama-3.1-8b-instant"
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        if os.getenv("GROQ_API_KEY") is None:
            raise ValueError("GROQ_API_KEY not found. Put it in your .env file.")

        self.messages = [
            {
                "role": "system",
                "content": "Write the output in 1-2 sentences",
            }
        ]

    def send_message(self, message, temperature=0.8):
        self.messages.append(
            {
                "role": "user",
                "content": message
            }
        )

        chat_completion = self.client.chat.completions.create(
            messages=self.messages,
            model=self.model,
            temperature=temperature
        )
        return chat_completion.choices[0].message.content

    def calculate(self, expression):
        """Evaluate a mathematical expression.

        >>> chat = Chat()
        >>> chat.calculate("2 + 2")
        '{"result": 4}'
        >>> chat.calculate("invalid")
        '{"error": "Invalid expression"}'
        """
        try:
            result = eval(expression)
            return json.dumps({"result": result})
        except Exception:
            return json.dumps({"error": "Invalid expression"})

    def ls(self, path=None):
        # List files in the current directory or in the given directory.
        try:
            if path is not None and path != "":  
                if os.path.isabs(path) or any(part == ".." for part in PurePath(path).parts):
                    # this replaces the is_path_true function to check for absolute paths and directory traversal
                    raise ValueError(
                        "Absolute paths and directory traversal are not allowed."
                    )

            if path is None or path == "":
                files = sorted(glob.glob("*"))
            else:
                files = sorted(glob.glob(f"{path}/*"))

            return json.dumps({"files": files})
        except Exception as e:
            return json.dumps({"error": str(e)})

    def run_conversation(self, user_prompt):
        """Run a conversation with tool calling."""

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant. "
                    "You can use tools to calculate math expressions and list files."
                )
            },
            {
                "role": "user",
                "content": user_prompt,
            }
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
                                "description": "Optional directory path to list files from"
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
                                "description": "The regex pattern to search for"
                            },
                            "filepath": {
                                "type": "string",
                                "description": "The file path or glob pattern to search in"
                            }
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
                                "description": "The name of the file to read"
                            }
                        },
                        "required": ["filename"],
                    },
                },
            }
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
                function_to_call = available_functions[function_name]
                function_args = json.loads(tool_call.function.arguments)

                if function_name == "calculate":
                    function_response = function_to_call(
                        expression=function_args.get("expression")
                    )
                elif function_name == "ls":
                    function_response = function_to_call(
                        path=function_args.get("path")
                    )
                elif function_name == "grep":
                    function_response = function_to_call(
                        regex=function_args.get("regex"),
                        filepath=function_args.get("filepath")
                    )
                elif function_name == "cat":
                    function_response = function_to_call(
                        filename=function_args.get("filename")
                    )
                else:
                    function_response = json.dumps(
                        {"error": f"Unknown function: {function_name}"}
                    )

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
                messages=messages
            )
            return second_response.choices[0].message.content

        return response_message.content
    
    def cat(self, filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            print("Error: File not found.")
        except UnicodeDecodeError:
            print("Error: File is not a valid UTF-8 text file.")
        except Exception as e:
            print(f"Error: {e}")

    
    def grep(self, regex, filepath): 
        files = glob.glob(filepath)
        output = []
        
        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if re.search(regex, line):
                            output.append(line.rstrip('\n'))
            except (FileNotFoundError, UnicodeDecodeError, OSError):
                # Skip files that can't be read
                continue
        
        if output:
            return '\n'.join(output)
        else:
            return ""
    

if __name__ == '__main__':
    import readline

    chat = Chat()

    def test_manual_commands():
        # Test calculate
        user_input = "/calculate 2 + 2"
        if user_input.startswith('/'):
            parts = user_input[1:].split()
            command = parts[0]
            args = parts[1:]
            # if command == 'calculate':
            #     result = chat.calculate(args[0])
            #     assert result == '{"result": 4}', f"Expected {{\"result\": 4}}, got {result}"

        # Test ls
        user_input = "/ls"
        if user_input.startswith('/'):
            parts = user_input[1:].split()
            command = parts[0]
            args = parts[1:]
            if command == 'ls':
                result = chat.ls(None)
                assert '"files"' in result, f"Expected files in result, got {result}"

        # Test grep
        user_input = "/grep import *.py"
        if user_input.startswith('/'):
            parts = user_input[1:].split()
            command = parts[0]
            args = parts[1:]
            if command == 'grep':
                result = chat.grep(args[0], args[1])
                # Just check it's a string
                assert isinstance(result, str)

        # Test cat
        user_input = "/cat requirements.txt"
        if user_input.startswith('/'):
            parts = user_input[1:].split()
            command = parts[0]
            args = parts[1:]
            if command == 'cat':
                result = chat.cat(args[0])
                assert isinstance(result, str)

        print("Manual command tests passed")

    test_manual_commands()

    print(chat.grep("hello", "*.txt"))

    try:
        while True:
            user_input = input("chat>> ")
            if user_input.startswith('/'):
                # manual command
                parts = user_input[1:].split()  # remove / and split
                if not parts:
                    print("Invalid command")
                    continue
                command = parts[0]
                args = parts[1:]
                if command == 'calculate':
                    if len(args) != 1:
                        print("Usage: /calculate <expression>")
                        continue
                    result = chat.calculate(args[0])
                    print(result)
                elif command == 'ls':
                    path = ' '.join(args) if args else None
                    result = chat.ls(path)
                    print(result)
                elif command == 'grep':
                    if len(args) != 2:
                        print("Usage: /grep <regex> <filepath>")
                        continue
                    result = chat.grep(args[0], args[1])
                    if result:
                        print(result)
                elif command == 'cat':
                    if len(args) != 1:
                        print("Usage: /cat <filename>")
                        continue
                    result = chat.cat(args[0])
                    print(result)
                else:
                    print(f"Unknown command: {command}")
            else:
                response = chat.run_conversation(user_input)
                print(response)
    except KeyboardInterrupt:
        print()

    


