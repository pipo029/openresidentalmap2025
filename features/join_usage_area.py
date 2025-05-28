#用途地域を結合するモジュール

import pandas as pd
import numpy as np
import geopandas as gpd

def join_usage_area(bldg_df, usage_usage_df):
    #データを絞る
    usage_df = usage_df[['A29_004', 'geometry']]
    usage_df.rename(columns={'A29_004':'usage_area'}, inplace=True)

    # 用途地域の種類を減らす．住居地域，商業地域，工業地域の三種類に分類
    usage_df['usage_area_disagg'] = np.where(usage_df['usage_area'].isin([1, 2, 3, 4, 5, 6, 7, 21]), 1, 
                                                np.where(usage_df['usage_area'].isin([8, 9]), 2, 
                                                    np.where(usage_df['usage_area'].isin([10, 11, 12]), 3, np.nan)))

    # ワンホットエンコーディング
    usage_df = pd.get_dummies(usage_df, columns=['usage_area'], prefix='usage_area')

    #用途地域のポリゴンを建物ポリゴンに空間結合
    bldg_df = gpd.sjoin(bldg_df, usage_df, how='left', op='within')
    bldg_df.drop(columns=['index_right'], inplace=True)

    return bldg_df