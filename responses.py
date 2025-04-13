import discord
import responses

# Chat bot features
def get_response(message: str) -> str:
    '''
    Example usage:
    if p_message == 'hello':
        return f'Hello {p_message.author}!'
    '''

    p_message = message.lower()

    if p_message == "!help":
        return "Commands: !help"
    
    return None
