"""Conversation compaction tool for the chat program.

This module summarizes chat conversation history to reduce token usage.
"""


def compact(messages, client, model):
    """Summarize messages and return a summary string.

    This function takes the current conversation messages, generates a summary using
    the LLM, and returns a summary string that can be used to replace the conversation.

    >>> from chat import Chat
    >>> chat = Chat(temperature=0.0)
    >>> chat.messages.append({"role": "user", "content": "What files are in the directory?"})
    >>> chat.messages.append({"role": "assistant", "content": "Here are the files..."})
    >>> result = compact(chat.messages, chat.client, chat.model)
    >>> 'Conversation compacted' in result
    True
    >>> isinstance(result, str) and len(result) > 0
    True
    """

    summary_prompt = (
        "Please provide a concise 1-5 line summary of this conversation. "
        "Include only the key points and decisions made."
    )

    # Create messages for summary request
    summary_messages = messages + [
        {"role": "user", "content": summary_prompt}
    ]

    response = client.chat.completions.create(
        model=model,
        messages=summary_messages,
    )
    summary = response.choices[0].message.content

    return f"Conversation compacted. Summary: {summary}"