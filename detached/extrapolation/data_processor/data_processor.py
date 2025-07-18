#基盤データとなる基盤地図データの前処理
#正解データとなるplateauデータの前処理

import pandas as pd
import geopandas as gpd
import re
import numpy as np
import os
from shapely import force_2d
from shapely.geometry import Polygon, MultiPolygon, GeometryCollection
from shapely.ops import unary_union

class DataProcessor:
    def __init__(self, basemap_area, target_basemap_area, 
                 widearea_basemap_path, government_polygon_path,
                 target_area, output_dir, output_basemap_path):
        #基盤地図
        self.basemap_area = basemap_area
        self.target_basemap_area = target_basemap_area
        self.widearea_basemap_path = widearea_basemap_path
        self.government_polygon_path = government_polygon_path 

        #output_data
        self.target_area = target_area
        self.output_dir = output_dir
        self.output_basemap_path = output_basemap_path

    def load_data(self):
        print('データの読み込み開始')
        #基盤地図データの読み込み
        self.widearea_basemap_path = self.widearea_basemap_path.format(basemap_area=self.basemap_area)
        self.widearea_basemap = gpd.read_parquet(self.widearea_basemap_path)
        #行政ポリゴンの読み込み
        self.government_polygon = gpd.read_file(self.government_polygon_path)
        print('データの読み込み終了')

    #基盤地図データの前処理
    def extract_target_basemap_bldg(self):
        print('基盤地図データの前処理開始')
        #基盤地図を対象地域のみに絞る
        self.target_polygon = self.government_polygon[self.government_polygon['SIKUCHOSON'] == self.target_basemap_area]
        self.widearea_basemap.to_crs('EPSG:4326', inplace=True)
        self.target_polygon.to_crs('EPSG:4326', inplace=True)
        self.target_basemap = gpd.sjoin(self.widearea_basemap, self.target_polygon, predicate="within")

        #要らないカラムの削除，データの出力
        self.target_basemap = self.target_basemap[['type', 'geometry']]
        self.target_basemap.reset_index(drop=True, inplace=True)
        self.target_basemap = gpd.GeoDataFrame(self.target_basemap, geometry='geometry', crs='EPSG:4326')
        # 無効なジオメトリを高速に修正（ベクトル化）
        invalid_mask = ~self.target_basemap.is_valid
        if invalid_mask.any():
            self.target_basemap.loc[invalid_mask, 'geometry'] = self.target_basemap.loc[invalid_mask, 'geometry'].make_valid()
        print('基盤地図データの前処理終了')
    
    # bldg_idの追加
    def add_bldg_id(self):
        # 1. 1から始まる連番を振る (gdf.index + 1)
        sequence = self.target_basemap.index + 1
        # 2. 連番を7桁の文字列にし、先頭を0で埋める (zfill)
        sequence_str_7digit = pd.Series(sequence).astype(str).str.zfill(7)
        # 3. 市区町村コードと7桁の連番を結合してIDを作成
        self.target_basemap['bldg_id'] = self.target_area + sequence_str_7digit

    def output_file(self):
        print('データの保存開始')
        #基盤地図の出力
        self.output_dir_base = self.output_dir.format(target_area=self.target_area)
        self.output_dir_base = os.path.join(self.output_dir_base, 'basemap')
        os.makedirs(self.output_dir_base, exist_ok=True)  # ディレクトリを作成（存在してもエラーにならない）
        #出力先のパスを設定
        self.output_basemap_path = self.output_basemap_path.format(target_area=self.target_area)
        self.target_basemap.to_parquet(
                                self.output_basemap_path,
                                index=False,
                                compression="brotli",
        )
        print('データの保存終了')

    def run(self):
        self.load_data()
        self.extract_target_basemap_bldg()
        self.add_bldg_id()
        self.output_file()