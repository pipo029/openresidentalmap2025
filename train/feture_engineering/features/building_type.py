#建て方別世帯数を算出するモジュール

import pandas as pd

def building_type(df):
    #地域階層レベルが１は市区町村レベル，3は4が存在するときにものなので2，4を取得
    df = df[(df['地域階層レベル'] == 2) | (df['地域階層レベル'] == 4)]
    df.reset_index(drop=True, inplace=True)
    
    #csvに出力した際に落ちてしまう先頭の00を補完
    # 地域階層レベルに応じて町丁字コードをゼロ埋め
    df.loc[df['地域階層レベル'] == 2, '町丁字コード'] = df.loc[df['地域階層レベル'] == 2, '町丁字コード'].apply(lambda x: f"{int(x):04d}")
    df.loc[df['地域階層レベル'] == 4, '町丁字コード'] = df.loc[df['地域階層レベル'] == 4, '町丁字コード'].apply(lambda x: f"{int(x):06d}")
    
    #KEY＿CODEを文字列として結合
    df['市区町村コード'] = df['市区町村コード'].astype(str)
    df['KEY_CODE'] = df['市区町村コード'] + df['町丁字コード']
    
    #秘匿地域を削除
    df = df[df['総数'] != 'X']
    #'-'は0で置換
    df = df.replace('-', '0')
    
    #カラムの厳選
    columns = ['KEY_CODE', '一戸建', '長屋建', '共同住宅']
    df = df[columns]
    
    # 該当のカラムの方の変換
    cols_to_convert = ['一戸建', '長屋建', '共同住宅']
    df[cols_to_convert] = df[cols_to_convert].astype(int)
    
    return df