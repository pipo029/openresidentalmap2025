#用途地域を結合するモジュール

import pandas as pd
import numpy as np
import geopandas as gpd

def join_usage_area(bldg_gdf, usage_gdf, crs):
    #データを絞る
    usage_gdf = usage_gdf[['A29_004', 'geometry']]
    usage_gdf.rename(columns={'A29_004':'usage_area'}, inplace=True)

    # # 用途地域の種類を減らす．住居地域，商業地域，工業地域の三種類に分類
    # usage_gdf['usage_area_disagg'] = np.where(usage_gdf['usage_area'].isin([1, 2, 3, 4, 5, 6, 7, 21]), 1, 
    #                                             np.where(usage_gdf['usage_area'].isin([8, 9]), 2, 
    #                                                 np.where(usage_gdf['usage_area'].isin([10, 11, 12]), 3, np.nan)))

    #用途地域のポリゴンを建物ポリゴンに空間結合
    bldg_gdf.to_crs('EPSG:4326', inplace=True)
    usage_gdf.to_crs('EPSG:4326', inplace=True)
    bldg_gdf = gpd.sjoin(bldg_gdf, usage_gdf, how='left', predicate='within')
    bldg_gdf.drop(columns=['index_right'], inplace=True)
    bldg_gdf.to_crs(f'EPSG:{crs}', inplace=True)

    #用途地域の説明変数を追加
    bldg_gdf['usage_area'].fillna(0)
    bldg_gdf = pd.get_dummies(bldg_gdf, columns=['usage_area'])
    bldg_gdf_col_list = bldg_gdf.columns.to_list()
    #地域で不足している用途地域カラムを追加
    usage_col = ['usage_area_1.0', 'usage_area_2.0', 'usage_area_3.0', 'usage_area_4.0', 'usage_area_5.0',
                'usage_area_6.0', 'usage_area_7.0', 'usage_area_8.0', 'usage_area_9.0', 'usage_area_10.0',
                'usage_area_11.0', 'usage_area_12.0', 'usage_area_21.0','usage_area_99.0']
    #地域で不足している用途地域カラム
    for col in usage_col:
        if col in bldg_gdf_col_list:
            continue
        else:
            bldg_gdf[col] = False
    
    pd.set_option('future.no_silent_downcasting', True)
    bldg_gdf[usage_col] = bldg_gdf[usage_col].replace({True: 1, False: 0})

    return bldg_gdf