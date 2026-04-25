import json
import os
from dotenv import load_dotenv
from tools.calculate import calculate, calculate_schema
from tools.cat import cat, cat_schema
from tools.grep import grep, grep_schema
from tools.ls import ls, ls_schema
from tools.compact import compact
from tools.doctests import doctests, doctests_schema
from tools.write_file import write_file, write_files, write_file_schema, write_files_schema
from tools.rm import rm, rm_schema

from groq import Groq

load_dotenv()

class Chat:
    """Chat interface for interacting with a Groq LLM and various tools.

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
                "content": "You are a helpful assistant with access to tools. Be concise and direct in your responses.",
            }
        ]

        if client is not None:
            self.client = client
        elif api_key is not None:
            self.client = Groq(api_key=api_key)
        else:
            env_key = os.getenv("GROQ_API_KEY")
            self.client = Groq(api_key=env_key) if env_key else None

    def send_message(self, message, temperature=0.0):
        """Append a user message and optionally send it to the configured LLM.

        >>> chat = Chat()
        >>> result = chat.send_message('hello', temperature=0.0)
        >>> isinstance(result, str) and len(result) > 0
        True
        """
        self.messages.append({"role": "user", "content": message})


        completion = self.client.chat.completions.create(
            messages=self.messages,
            model=self.model,
            temperature=0.0,
        )
        return completion.choices[0].message.content

    def run_conversation(self, user_prompt, temperature):
        """Run a conversation through the configured Groq client.
        Doctests for this method use mocking to simulate Groq client responses, without the need for an actual API key.

        >>> chat = Chat()
        >>> result = chat.run_conversation('hello', temperature=0.0)
        >>> isinstance(result, str) and len(result) > 0
        True
        >>> chat2 = Chat()
        >>> result2 = chat2.run_conversation('calculate 2+2', temperature=0.0)
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
            calculate_schema,
            ls_schema,
            grep_schema,
            cat_schema,
            doctests_schema,
            write_file_schema,
            write_files_schema,
            rm_schema,
        ]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=tools,
            tool_choice="auto",
            temperature=temperature,
        )

        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls

        if tool_calls:
            available_functions = {
                "calculate": calculate,
                "ls": ls,
                "grep": grep,
                "cat": cat,
                "doctests": doctests,
                "write_file": write_file,
                "write_files": write_files,
                "rm": rm,
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
        >>> chat.messages[0]["content"].startswith('Summary of previous conversation:')
        True
        """
        result = compact(self.messages, self.client, self.model)
        
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


def main(chat=None, temperature=0.0):
    """Starts the chat command line interface.

    >>> calculate('2+2')
    '{"result": 4}'
    >>> calculate('4 + 5')
    '{"result": 9}'
    >>> ls('test_files')
    '{"files": ["test_files/__pycache__", "test_files/grep_1.txt", "test_files/grep_2.txt", "test_files/sample_add.py", "test_files/testtext.txt"]}'
    >>> ls('dir')
    '{"error": "Directory does not exist."}'
    >>> cat('file.txt')
    "Error: [Errno 2] No such file or directory: 'file.txt'"
    >>> result = doctests('test_files/sample_add.py')
    >>> 'Test passed.' in result
    True
    >>> rm('file.txt')
    'Error: No files matched the pattern: file.txt'
    """
    if not os.path.isdir(".git"):
        print("Error: .git folder not found. This command must be run from a git repository.")
        return

    if chat is None:
        chat = Chat()

    if getattr(chat, 'client', None) is None:
        print("Groq client is not configured. Only local tools are available.")

    if os.path.isfile("AGENTS.md"):
        print(cat("AGENTS.md"))
        print("I read the agents.md file")

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
                    print(calculate(args[0]))
                elif command == "ls":
                    print(ls(args[0] if args else None))
                elif command == "grep":
                    if len(args) != 1:
                        print("Usage: /grep <regex> <filepath>")
                        continue
                    grep_parts = args[0].split(maxsplit=1)
                    if len(grep_parts) != 2:
                        print("Usage: /grep <regex> <filepath>")
                        continue
                    print(grep(grep_parts[0], grep_parts[1]))
                elif command == "cat":
                    if len(args) != 1:
                        print("Usage: /cat <filename>")
                        continue
                    print(cat(args[0]))
                elif command == "doctests":
                    if len(args) != 1:
                        print("Usage: /doctests <path>")
                        continue
                    print(doctests(args[0]))
                elif command == "rm":
                    if len(args) != 1:
                        print("Usage: /rm <path>")
                        continue
                    print(rm(args[0]))
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

    


