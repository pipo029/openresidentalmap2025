#住宅が建たない用途地域の建物を除外する関数

import pandas as pd
import geopandas as gpd

def exclusion_usage_area(gdf, usage_area, crs):
    gdf.to_crs(crs, inplace=True)
    usage_area.to_crs(crs, inplace=True)

    # --- ★ 1. 元のgdfのカラム名を保存 ---
    original_columns = gdf.columns.tolist()

    # 共同住宅が建たない用途地域に絞る
    usage_area = usage_area[usage_area['A29_004'] == 12]
    

    # 用途地域に結合される建物のインデックスを取得
    joined_with_usage_area = gpd.sjoin(gdf, usage_area, how='left')
    joined_with_usage_area = joined_with_usage_area.loc[~joined_with_usage_area.index.duplicated(keep='first')]
    usage_area_indices = joined_with_usage_area[joined_with_usage_area['index_right'].notna()].index
    
    
    # 住宅が建たない用途地域のインデックスを取得
    indices_to_exclude = list(set(usage_area_indices))


    # 特定したインデックスを元の建物データから除外 ---
    gdf = gdf.drop(indices_to_exclude)

    # --- ★ 6. カラムを元々あったものだけに絞り込む ---
    # 保存しておいたカラム名のリストでデータフレームを再作成する
    gdf = gdf[original_columns]


    return gdf