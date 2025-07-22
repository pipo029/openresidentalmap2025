import os
from datetime import datetime
import functools
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

env_path = "G:/マイドライブ/akiyamalab/オープン住宅地図/code_2025/libs/slackapp/.env"
load_dotenv(dotenv_path=env_path)


def notify(channel="U044WBNG96U"):
    def _notify(func):
        @functools.wraps(func)
        def _wrapper(*args, **kwargs):
            start_time = datetime.now()
            text = f'/nfunction: {func.__name__}/nstart at {start_time:%Y/%m/%d %H:%M:%S}/nelapsed '

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


def send_slack_message(text="Hello from slackapp! :tada:", channel="U044WBNG96U"):
    slack_token = os.getenv("SLACK_API_TOKEN")
    if not slack_token:
        print("エラー: SLACK_API_TOKENが.envファイルから読み込めていません。")
        return # 処理を中断

    client = WebClient(token=slack_token)

    try:
        response = client.chat_postMessage(
            channel=channel,
            text=text,
        )

    except SlackApiError as e:
        # "ok"がFalseの場合にSlackApiErrorが発生する
        # エラー内容を詳しく表示する
        print(f"Slack APIエラーが発生しました: {e.response['error']}")


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
