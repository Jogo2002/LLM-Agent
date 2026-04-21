"""Conversation compaction tool for the chat program.

This module summarizes chat conversation history to reduce token usage.
"""


def compact(messages, client, model):
    """Summarize messages and return a summary string.

    This function takes the current conversation messages, generates a summary using
    the LLM, and returns a summary string that can be used to replace the conversation.

    >>> from unittest.mock import Mock
    >>> from chat import Chat
    >>> mock_client = Mock()
    >>> mock_response = Mock()
    >>> mock_message = Mock()
    >>> mock_message.content = 'Summary: User discussed files and calculations.'
    >>> mock_choice = Mock()
    >>> mock_choice.message = mock_message
    >>> mock_response.choices = [mock_choice]
    >>> mock_client.chat.completions.create.return_value = mock_response
    >>> chat = Chat(client=mock_client)
    >>> chat.messages.append({"role": "user", "content": "What files are in the directory?"})
    >>> chat.messages.append({"role": "assistant", "content": "Here are the files..."})
    >>> result = compact(chat.messages, chat.client, chat.model)
    >>> 'Summary' in result
    True
    >>> 'Conversation compacted' in result
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