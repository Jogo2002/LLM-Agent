from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

class Chat: 
    '''
    >>> chat = Chat()
    >>> chat.send_message('my name is bob')
    '''
    client = Groq()
    def __init__(self): 
        self.messages = [
            {
                "role": "system",
                "content": "Write the output in 1-2 sentences",
            }
        ]
    def send_message(self, message):
        self.messages.append(
            {
                'role': 'user',
                'content': message
            })
        chat_completion = self.client.chat.completions.create(
            messages=self.messages,
            model="llama-3.1-8b-instant",
        ) 
        return chat_completion.choices[0].message.content


if __name__ == '__main__': 
    import readline
    chat = Chat()
    try:
        while True:  
            user_input = input("chat>> ")
            response = chat.send_message(user_input)
            print(response)
    except KeyboardInterrupt: 
        print() 

        
# client = Groq(
#     api_key=os.environ.get("GROQ_API_KEY"),  # This is the default and can be omitted
# )

# chat_completion = client.chat.completions.create(
#     messages=[
#         {
#             "role": "system",
#             "content": "Write the output in 1-2 sentences",
#         },
#         {
#             "role": "user",
#             "content": "explain the importance of low latency LLMS",
#         },
#     ],
#     model="llama-3.1-8b-instant",
# )
# print(chat_completion.choices[0].message.content)