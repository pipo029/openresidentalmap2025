#各建物の周辺にあるpoiデータの結合

import pandas as pd
import geopandas as gpd


def find_nearby_pois(bldg_gdf, poi_gdf, crs, min):
    # EPSG:3857（メートル単位の投影座標系）に変換
    bldg_gdf.to_crs(epsg=crs, inplace=True)  # 建物データの座標系をメートル単位に変換
    poi_gdf.to_crs(epsg=crs, inplace=True)  
    
    # 建物の中心点を計算
    bldg_gdf['center'] = bldg_gdf.centroid

    # バッファ距離を度単位に変換
    distance_meter = min * 80 # 80m/minの変換
    print(f'バッファの半径:{distance_meter}')
    
    # バッファの作成
    bldg_gdf['buffer'] = bldg_gdf['center'].buffer(distance_meter)

    # POIデータとバッファを用いて空間結合（POIがバッファ内にある場合）
    bldg_gdf.set_geometry('buffer', inplace=True)  # バッファをジオメトリとして設定
    nearby_pois = gpd.sjoin(poi_gdf, bldg_gdf, how="inner", predicate="within")

    columns = ['unique_id', 'amenity', 'shop', 'tourism']
    nearby_pois = nearby_pois[columns]

    return nearby_pois

# 情報の追加
def attach_poi_to_buildings(bldg_gdf, poi_gdf, crs):  
    # 周辺建物情報のdfを格納したリストを返す
    bldg_gdf['unique_id'] = bldg_gdf.index
    for i in range(1, 6, 2):
        #建物データに近辺のpoiデータを結合
        filter_poi = find_nearby_pois(bldg_gdf, poi_gdf, crs, i)

        # None以外の要素を'amenity'に置き換え
        filter_poi['amenity'] = filter_poi['amenity'].where(filter_poi['amenity'].isna(), 'amenity')
        filter_poi['shop'] = filter_poi['shop'].where(filter_poi['shop'].isna(), 'shop')
        filter_poi['tourism'] = filter_poi['tourism'].where(filter_poi['tourism'].isna(), 'tourism')

        rename_columns = [str(i) + '_' + colum for colum in ['amenity', 'shop', 'tourism']]
        rename_dict = dict(zip(['amenity', 'shop', 'tourism'], rename_columns))
        filter_poi.rename(columns=rename_dict, inplace=True)

        # unique_idでグループ化・個数の集計
        filter_poi = pd.get_dummies(filter_poi, columns=rename_columns)
        # geometry列を除外して集計
        filter_poi_groupby = filter_poi.groupby('unique_id').sum().reset_index()


        bldg_gdf = pd.merge(bldg_gdf, filter_poi_groupby, on='unique_id', how='left')

        columns = {'1_amenity_amenity':'1_amenity', '1_shop_shop':'1_shop',
       '1_tourism_tourism':'1_tourism', '3_amenity_amenity':'3_amenity', '3_shop_shop':'3_shop',
       '3_tourism_tourism':'3_tourism', '5_amenity_amenity':'5_amenity', '5_shop_shop':'5_shop', '5_tourism_tourism':'5_tourism'}
        
        bldg_gdf.rename(columns=columns, inplace=True)
    
    return bldg_gdf