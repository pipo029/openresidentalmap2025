#KEYCODEを追加するコードを作成

import pandas as pd

def add_KEYCODE(df):
    if '男女' in df.columns:
        df = df[df['男女'] == '総数']
    #地域階層レベルが１は市区町村レベル，3は4が存在するときにものなので2，4を取得
    df = df[(df['地域階層レベル'] == 2) | (df['地域階層レベル'] == 4)]
    df.reset_index(drop=True, inplace=True)
    
    #csvに出力した際に落ちてしまう先頭の00を補完
    # 地域階層レベルに応じて町丁字コードをゼロ埋め
    df.loc[df['地域階層レベル'] == 2, '町丁字コード'] = df.loc[df['地域階層レベル'] == 2, '町丁字コード'].apply(lambda x: f"{int(x):04d}")
    df.loc[df['地域階層レベル'] == 4, '町丁字コード'] = df.loc[df['地域階層レベル'] == 4, '町丁字コード'].apply(lambda x: f"{int(x):06d}")
    
    #KEY＿CODEを文字列として結合
    df['市区町村コード'] = df['市区町村コード'].astype(str).str.zfill(5)
    df['KEY_CODE'] = df['市区町村コード'] + df['町丁字コード']
    
    return df