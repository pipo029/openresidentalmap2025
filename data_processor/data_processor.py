#基盤データとなる基盤地図データの前処理
#正解データとなるplateauデータの前処理

import pandas as pd
import geopandas as gpd
import re
import numpy as np
import os
from shapely import force_2d

class DataProcessor:
    def __init__(self, basemap_area, target_basemap_area, target_plateau_area, 
                 widearea_basemap_path, government_polygon_path, 
                 plateau_path, output_dir, output_basemap_path, output_plateau_path):
        #基盤地図
        self.basemap_area = basemap_area
        self.target_basemap_area = target_basemap_area
        self.widearea_basemap_path = widearea_basemap_path
        self.government_polygon_path = government_polygon_path 
        
        #plateauデータ
        self.target_plateau_area = target_plateau_area
        self.plateau_path = plateau_path

        #output_data
        self.output_dir = output_dir
        self.output_basemap_path = output_basemap_path
        self.output_plateau_path = output_plateau_path


    def load_data(self):
        print('データの読み込み開始')
        #基盤地図データの読み込み
        self.widearea_basemap_path = self.widearea_basemap_path.format(basemap_area=self.basemap_area)
        self.widearea_basemap = gpd.read_parquet(self.widearea_basemap_path)
        #行政ポリゴンの読み込み
        self.government_polygon = gpd.read_file(self.government_polygon_path)
        #plateauデータの読み込み
        self.plateau_path = self.plateau_path.format(target_plateau_area=self.target_plateau_area)
        self.plateau = gpd.read_parquet(self.plateau_path)

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

    def extract_numeric_part(self, value):
        if pd.isna(value):
            return None
        numeric_part = re.findall(r'\d+', value)
        return numeric_part[0] if numeric_part else None

    #plateauデータの前処理
    def cleaning_plateau(self):
        print('plateauデータの前処理開始')
        self.plateau = self.plateau[['id', 'class', 'usage', 'geometry']]
        # usageカラムを数値部分のみで置き換え
        self.plateau['usage'] = self.plateau['usage'].apply(self.extract_numeric_part)
        self.plateau['class'] = pd.to_numeric(self.plateau['class'], errors='coerce')  # 変換できない値はNaNにする
        self.plateau['usage'] = pd.to_numeric(self.plateau['usage'], errors='coerce')
        # 無効なジオメトリを高速に修正（ベクトル化）
        invalid_mask = ~self.plateau.is_valid
        if invalid_mask.any():
            self.plateau.loc[invalid_mask, 'geometry'] = self.plateau.loc[invalid_mask, 'geometry'].make_valid()
        # POLYGON Zを2次元にする（Z値を除去）
        self.plateau['geometry'] = self.plateau['geometry'].apply(force_2d)


        self.plateau.replace({None: np.nan}, inplace=True)
        print('plateauデータの前処理終了')

    def output_file(self):
        print('データの保存開始')
        #基盤地図の出力
        self.output_dir_base = self.output_dir.format(target_plateau_area=self.target_plateau_area)
        self.output_dir_base = os.path.join(self.output_dir_base, 'basemap')
        os.makedirs(self.output_dir_base, exist_ok=True)  # ディレクトリを作成（存在してもエラーにならない）
        #出力先のパスを設定
        self.output_basemap_path = self.output_basemap_path.format(target_plateau_area=self.target_plateau_area)
        self.target_basemap.to_parquet(
                                self.output_basemap_path,
                                index=False,
                                compression="brotli",
        )

        #plateauの出力
        self.output_dir_pla = self.output_dir.format(target_plateau_area=self.target_plateau_area)
        self.output_dir_pla = os.path.join(self.output_dir_pla, 'plateau')
        os.makedirs(self.output_dir_pla, exist_ok=True)  # ディレクトリを作成（存在してもエラーにならない）
        #出力先のパスを設定
        self.output_plateau_path = self.output_plateau_path.format(target_plateau_area=self.target_plateau_area)
        self.plateau.to_parquet(
                                self.output_plateau_path,
                                index=False,
                                compression="brotli",
        )
        print('データの保存終了')

    def run(self):
        self.load_data()
        self.extract_target_basemap_bldg()
        self.cleaning_plateau()
        self.output_file()