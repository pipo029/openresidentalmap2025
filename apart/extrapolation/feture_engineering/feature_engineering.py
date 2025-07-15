#特徴量の作成

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from features.add_KEYCODE import add_KEYCODE
from features.age_group_ratio import age_group_ratio
from features.per_length_residence import per_length_residence
from features.household_income_ratios import household_income_ratios
from features.building_type import building_type
from features.join_usage_area import join_usage_area
from features.bldg_attrs import bldg_attrs
from features.bldg_type import bldg_type
from features.poi import find_nearby_pois
from features.poi import attach_poi_to_buildings
from features.exclusion_facility import exclusion_facility
from features.exclusion_usage_area import exclusion_usage_area


class FeatureEngineering:
    def __init__(self, 
                 target_area,
                 bldg_path, 
                 crs,
                 schools_path,
                 hospitals_path,
                 usage_area_path, 
                 output_path,
                 output_features_path ):

        # 建物データ
        self.target_area = target_area
        self.bldg_path = bldg_path
        self.crs = crs
        self.schools_path = schools_path
        self.hospitals_path = hospitals_path
        self.usage_area_path = usage_area_path
        # 出力パス
        self.output_path = output_path
        self.output_features_path = output_features_path 
    
    def load_data(self):
        print('データの読み込み開始')
        #建物データの読み込み
        self.bldg_path = str(self.bldg_path).format(target_area=self.target_area)
        self.bldg = gpd.read_parquet(self.bldg_path)
        self.schools = gpd.read_file(self.schools_path)
        self.hospitals = gpd.read_file(self.hospitals_path)
        self.usage_area_path = str(self.usage_area_path).format(target_area=self.target_area)
        self.usage_area = gpd.read_file(self.usage_area_path, encoding='shift_jis')

        print('データの読み込み終了')

    # 建物データの処理
    
    def bldg_attrs(self):
        # 建物属性の追加(面積，周囲長，矩形度)
        self.bldg = self.bldg.copy()
        self.bldg = bldg_attrs(self.bldg, self.crs)
        #bldg座標系6676


    def exclusion_detached(self):
        # 戸建てと分類された建物を除外する
        self.bldg = self.bldg[self.bldg['presumed_detached'] != 1]
    
    def exclusion_facility(self):
        # 特定の施設を除外する
        self.bldg = exclusion_facility(self.bldg, self.schools, self.hospitals, self.crs)

    def exclusion_usage_area(self):
        # 特定の用途地域の建物を除外する
        self.bldg = exclusion_usage_area(self.bldg, self.usage_area, self.crs)

    
    def clean_data(self):
        columns = ['prob']
        self.bldg.drop(columns=columns, axis=1, inplace=True)

    
    def save_features(self):
        # 特徴量の保存
        self.output_path = str(self.output_path).format(target_area=self.target_area)
        self.bldg.to_parquet(
                self.output_path,
                index=False,
                compression="brotli",
                )
        self.output_features_path = str(self.output_features_path).format(target_area=self.target_area)
        # self.features.to_parquet(
        #         self.output_features_path,
        #         index=False,
        #         compression="brotli",
        #         )

    def run(self):
        # データの読み込み
        self.load_data()

        # 建物データの処理
        self.bldg_attrs()
        self.exclusion_detached()
        self.exclusion_facility() 
        self.exclusion_usage_area()
        self.clean_data()

        # 特徴量の保存
        self.save_features()