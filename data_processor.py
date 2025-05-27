#基盤データとなる基盤地図データの前処理
#正解データとなるplateauデータの前処理

import pandas as pd
import geopandas as gpd
import re
import numpy as np

class DataProcessor:
    def __init__(self, basemap_area, target_basemap_area, target_plateau_area, 
                 widearea_geomap_path, government_polygon_path, output_basemap_path, 
                 plateau_path, output_plateau_path):
        #基盤地図
        self.basemap_area = basemap_area
        self.target_basemap_area = target_basemap_area
        self.widearea_geomap_path = widearea_geomap_path
        self.government_polygon_path = government_polygon_path 
        self.output_basemap_path = output_basemap_path
        #plateauデータ
        self.target_plateau_area = target_plateau_area
        self.plateau_path = plateau_path
        self.output_plateau_path = output_plateau_path

    def load_data(self):
        #基盤地図データの読み込み
        self.widearea_geomap_path = self.widearea_geomap_path.format(basemap_area=self.basemap_area)
        self.widearea_geomap = gpd.read_parquet(self.widearea_geomap_path)
        #行政ポリゴンの読み込み
        self.government_polygon = gpd.read_file(self.government_polygon_path)
        #plateauデータの読み込み
        self.plateau_path = self.plateau_path.format(target_plateau_area=self.target_plateau_area)
        self.plateau = gpd.read_file(self.government_polygon_path)

    #基盤地図データの前処理
    def extract_target_basemap_bldg(self):
        #基盤地図を対象地域のみに絞る
        self.target_polygon = self.government_polygon[self.government_polygon['SIKUCHOSON'] == self.target_basemap_area]
        self.target_geomap = gpd.sjoin(self.widearea_geomap, self.target_polygon, predicate="within")

        #要らないカラムの削除，データの出力
        self.target_geomap = self.target_geomap[['type', 'geometry']]
        self.target_geomap.reset_index(drop=True, inplace=True)
        self.target_geomap = gpd.GeoDataFrame(self.target_geomap, geometry='geometry', crs='EPSG:4326')
    
    #plateauデータの前処理
    def cleaning_plateau(self):
        # usageカラムの数値部分のみを取得して置き換える関数
        def extract_numeric_part(value):
            if pd.isna(value):
                return None
            numeric_part = re.findall(r'\d+', value)
            return numeric_part[0] if numeric_part else None
        # usageカラムを数値部分のみで置き換え
        self.plateau['usage'] = self.plateau['usage'].apply(extract_numeric_part)

        self.plateau = self.plateau[['id', 'class', 'usage', 'geometry']]
        self.plateau.replace({None: np.nan}, inplace=True)

    def output_file(self):
        #出力先のパスを設定
        self.output_basemap_path = self.output_basemap_path.format(target_basemap_area=self.target_basemap_area)
        self.target_geomap.to_parquet(
                                self.output_basemap_path,
                                index=False,
                                compression="brotli",
        )
        self.output_plateau_path = self.output_plateau_path.format(target_plateau_area=self.target_plateau_area)
        self.target_geomap.to_parquet(
                                self.output_plateau_path,
                                index=False,
                                compression="brotli",
        )

    def run(self):
        self.load_data()
        self.extract_target_basemap_bldg()
        self.cleaning_plateau()
        self.output_file()