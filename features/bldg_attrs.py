#建物属性（面積・周囲長・矩形度）を算出するモジュール

import geopandas as gpd
import numpy as np


def bldg_attrs(gdf, crs):
    # 面積の計算
    gdf.to_crs(crs, inplace=True)
    gdf['area'] = gdf.area
    gdf = gdf[gdf['area'] >= 25] # 面積が25平方メートル以上のポリゴンのみを残す

    #建物の外周を算出
    # 各ポリゴンの外周の長さを計算し、新しい列に追加
    gdf['perimeter'] = gdf['geometry'].length

    # 矩形度の計算
    gdf['rectangle'] = gdf['perimeter'] / np.sqrt(gdf['area'])

    return gdf