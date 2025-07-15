#居住期間別人口割合を算出するモジュール

import pandas as pd

#小地域の年齢階級別人口割合を算出
def per_length_residence(df):
    #秘匿地域を削除
    df = df[df['総数'] != 'X']
    #'-'は0で置換
    df = df.replace('-', '0')
    
    
    #年齢カラムの数値を文字列から数値列に変換
    # 12列目から32列目に該当する部分を取り出して変換を試みる
    cols_to_convert = ['総数', '出生時から', '1年未満', '1年以上5年未満',
       '5年以上10年未満', '10年以上20年未満', '20年以上', '居住期間「不詳」']
    df[cols_to_convert] = df[cols_to_convert].astype(int)
    
    
    # 総数カラムで各カラムの値の割合を計算して置き換え
    for col in cols_to_convert:
        if col != '総数':
            df[col] = df[col] / df['総数']
    #0を割ると欠損値になるので0で置換
    df = df.fillna(0)
    
    #カラムを厳選
    df = df[['KEY_CODE', '出生時から', '1年未満', '1年以上5年未満',
       '5年以上10年未満', '10年以上20年未満', '20年以上', '居住期間「不詳」']]
    
    return df