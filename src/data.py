from datetime import datetime

from api_spec import Message, Intent, Sentiment

EXAMPLES = {
    "chat_stream_1": """enias:
Hi Team!

enias:
Thanks for getting back to us on the styling issue we had last week. Font colours are so important for productivity.

enias:
I noticed ab.bot being very verbose lately

enias:
Is there a way to decrease the verbosity level?

enias:
I want ab.bot to ignore thank you messages and stop asking our customers to assign messages to threads.

enias:
Our clients are not technical so working with threads is difficult.

enias:
Thanks again, looking forward to your response!

enias:
Oh, before I forget. Is there a settings to change the font size?
    """
}

PROCESSED_CHAT_STREAM = [Message(
    **{'message_id': '0', 'timestamp': datetime(2022, 6, 15, 16, 18, 44, 155), 'user_id': 'enias',
       'text': 'Hi Team!', 'sentiment'
       : Sentiment.POSITIVE, 'intent': Intent.SALUTATION, 'root_message_id': '0'}),
    Message(**{
        'message_id': '1',
        'timestamp': datetime(
            2022,
            6,
            15,
            16,
            18,
            44,
            155),
        'user_id': 'enias',
        'text': 'Thanks for getting back to us on the styling issue we had last week. Font colours are so important for productivity.',
        'sentiment'
        : Sentiment.POSITIVE, 'intent': Intent.PRAISE, 'root_message_id': '1'}), Message(**{
        'message_id': '2',
        'timestamp': datetime(
            2022,
            6,
            15,
            16,
            18,
            44,
            155),
        'user_id': 'enias',
        'text': 'I noticed ab.bot being very verbose lately',
        'sentiment'
        : Sentiment.NEGATIVE, 'intent': Intent.COMPLAINT, 'root_message_id': '2'}), Message(
        **{
            'message_id': '3',
            'timestamp': datetime(
                2022,
                6,
                15,
                16,
                18,
                44,
                155),
            'user_id': 'enias',
            'text': 'Is there a way to decrease the verbosity level?',
            'sentiment'
            : Sentiment.NEUTRAL, 'intent': Intent.QUESTION, 'root_message_id': '2'}),
    Message(**{
        'message_id': '4',
        'timestamp': datetime(
            2022,
            6,
            15,
            16,
            18,
            44,
            155),
        'user_id': 'enias',
        'text': 'I want ab.bot to ignore thank you messages and stop asking our customers to assign messages to threads.',
        'sentiment'
        : Sentiment.NEGATIVE, 'intent': Intent.REQUEST, 'root_message_id': '2'}),
    Message(**{
        'message_id': '5',
        'timestamp': datetime(
            2022,
            6,
            15,
            16,
            18,
            44,
            155),
        'user_id': 'enias',
        'text': 'Our clients are not technical so working with threads is difficult.',
        'sentiment'
        : Sentiment.NEGATIVE, 'intent': Intent.QUESTION,
        'root_message_id': '2'}), Message(**{
        'message_id': '6',
        'timestamp': datetime(
            2022,
            6,
            15,
            16,
            18,
            44,
            155),
        'user_id': 'enias',
        'text': 'Thanks again, looking forward to your response!',
        'sentiment'
        : Sentiment.POSITIVE, 'intent': Intent.PRAISE, 'root_message_id': '6'}),
    Message(**{
        'message_id': '7',
        'timestamp': datetime(
            2022,
            6,
            15,
            16,
            18,
            44,
            155),
        'user_id': 'enias',
        'text': 'Oh, before I forget. Is there a settings to change the font size?',
        'sentiment'
        : Sentiment.NEUTRAL, 'intent': Intent.QUESTION,
        'root_message_id': '6'})]
