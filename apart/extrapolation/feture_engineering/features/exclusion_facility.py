#共同住宅に似た建物を除外する

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

def exclusion_facility(gdf, schools, hospitals, crs):
    gdf.to_crs(crs, inplace=True)
    schools.to_crs(crs, inplace=True)
    hospitals.to_crs(crs, inplace=True)

    # --- ★ 1. 元のgdfのカラム名を保存 ---
    original_columns = gdf.columns.tolist()

    # --- 3. 各施設に最も近い建物を特定 ---
    joined_schools = gpd.sjoin_nearest(schools, gdf)
    school_building_indices = joined_schools['index_right']

    joined_hospitals = gpd.sjoin_nearest(hospitals, gdf)
    hospital_building_indices = joined_hospitals['index_right']

    # --- 4. 除外対象のインデックスを重複なく統合 ---
    indices_to_exclude = list(set(school_building_indices) | set(hospital_building_indices))

    # --- 5. 特定したインデックスを元の建物データから除外 ---
    gdf = gdf.drop(indices_to_exclude)
    
    # --- ★ 6. カラムを元々あったものだけに絞り込む ---
    # 保存しておいたカラム名のリストでデータフレームを再作成する
    gdf = gdf[original_columns]

    return gdf