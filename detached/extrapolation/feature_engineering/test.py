import pandas as pd
import slackapp

@slackapp.notify()
def long_running_task():
    print("重い処理を実行中...")
    import time
    time.sleep(2)
    print("完了！")

long_running_task()