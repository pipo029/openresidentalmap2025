import os
from datetime import datetime
import functools
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

load_dotenv()


def notify(channel="notice"):
    def _notify(func):
        @functools.wraps(func)
        def _wrapper(*args, **kwargs):
            start_time = datetime.now()
            text = f'\nfunction: {func.__name__}\nstart at {start_time:%Y/%m/%d %H:%M:%S}\nelapsed '

            try:
                result = func(*args, **kwargs)

            except BaseException as e:
                end_time = datetime.now()
                text = f':warning: {e.__class__.__name__}: {e}' + text + format_timedelta(end_time - start_time)
                send_slack_message(text=text, channel=channel)
                raise e

            else:
                end_time = datetime.now()
                text = ':white_check_mark: Finished!' + text + format_timedelta(end_time - start_time)
                send_slack_message(text=text, channel=channel)

            return result
        return _wrapper
    return _notify


def send_slack_message(text="Hello from slackapp! :tada:", channel="random"):
    slack_token = os.environ["SLACK_API_TOKEN"]
    client = WebClient(token=slack_token)

    try:
        response = client.chat_postMessage(
            channel=channel,
            text=text,
        )

    except SlackApiError as e:
        # You will get a SlackApiError if "ok" is False
        assert e.response["error"]


def format_timedelta(timedelta):
    total_sec = timedelta.total_seconds()
    fmt = ''
    # hours
    if total_sec > 3600:
        hours = total_sec // 3600
        fmt += f'{hours:.0f}h '
    # minutes
    if total_sec > 60:
        minutes = (total_sec % 3600) // 60
        fmt += f'{minutes:.0f}m '
        # seconds
        seconds = (total_sec % 60) // 1
        fmt += f'{seconds:.0f}s'
    elif total_sec > 1:
        fmt = f'{total_sec:.3f} s'
    else:
        milliseconds = total_sec * 1000
        fmt = f'{milliseconds:.0f} ms'

    return fmt
