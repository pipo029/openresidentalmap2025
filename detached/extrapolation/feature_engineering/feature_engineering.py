#特徴量の作成

import pandas as pd
import geopandas as gpd
import os
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
from features.exclusion_usage_area import exclusion_usage_area
import slackapp


class FeatureEngineering:
    def __init__(self, 
                 age_group_path, 
                 ownertype_path,
                 year_income_path, 
                 length_residence_path,
                 target_small_area,
                 small_area_path,
                 how_to_build_path,  
                 target_area,
                 geomap_path,
                 poi_target,
                 poi_path, 
                 usage_area_path,
                 crs,
                 output_dir_path,
                 output_path,
                 output_features_path
                 ):
        # 特徴量のパス
        self.age_group_path = age_group_path
        self.ownertype_path = ownertype_path
        self.year_income_path = year_income_path
        self.length_residence_path = length_residence_path
        self.target_small_area = target_small_area
        self.small_area_path = small_area_path
        self.how_to_build_path = how_to_build_path
        # self.usage_area_path = usage_area_path
        # 建物データ
        self.target_area = target_area
        self.geomap_path = geomap_path
        self.poi_target = poi_target
        self.poi_path = poi_path
        self.usage_area_path = usage_area_path
        self.crs = crs

        # 出力パス
        self.output_dir_path = output_dir_path
        self.output_path = output_path
        self.output_features_path = output_features_path
    
    def load_data(self):
        print('データの読み込み開始')
        # 特徴量データの読み込み
        self.age_group = pd.read_csv(self.age_group_path, encoding='cp932')
        self.ownertype = pd.read_csv(self.ownertype_path, encoding='cp932')
        self.year_income = pd.read_excel(self.year_income_path)
        self.length_residence = pd.read_csv(self.length_residence_path, encoding='cp932')
        self.small_area = gpd.read_file(self.small_area_path)
        self.how_to_build = pd.read_csv(self.how_to_build_path, encoding='cp932', dtype={'市区町村コード': str, '町丁字コード': str})
        # self.usage_area = gpd.read_file(self.usage_area_path, encoding='shift_jis')
        self.poi_path = str(self.poi_path).format(poi_target=self.poi_target)
        self.poi = gpd.read_parquet(self.poi_path)

        #建物データの読み込み
        self.geomap_path = str(self.geomap_path).format(target_area=self.target_area)
        self.geomap = gpd.read_parquet(self.geomap_path)
        print('データの読み込み終了')
    
    def add_keycode(self):
        print('統計値特徴量の作成開始')
        self.age_group = add_KEYCODE(self.age_group)
        self.length_residence = add_KEYCODE(self.length_residence)
        self.ownertype = add_KEYCODE(self.ownertype)

    def age_group_ratio(self):
        # 年齢層の割合を計算
        self.age_group = age_group_ratio(self.age_group)
    
    def per_length_residence(self):
        # 居住期間の割合を計算
        self.length_residence = per_length_residence(self.length_residence)

    def household_income_ratios(self):
        # 収入階級別人口割合を計算
        # household_target = '長井市'
        self.micro_income = household_income_ratios(self.year_income, self.ownertype, self.target_area)
    
    def building_type(self):
        # 建て方別世帯数を計算
        self.how_to_build = building_type(self.how_to_build)
    
    def join_small_area(self):
        # 小地域ポリゴンと結合
        self.small_area = self.small_area[['KEY_CODE', 'PREF_NAME', 'CITY_NAME', 'S_NAME', 'geometry']] #小地域ポリゴンのdfのうち必要なカラムに絞る
        self.small_area = self.small_area[self.small_area['CITY_NAME'] == self.target_small_area]
        self.geomap.to_crs('EPSG:4326', inplace=True)
        self.small_area.to_crs('EPSG:4326', inplace=True)
        self.geomap = gpd.sjoin(self.geomap, self.small_area, how='left', predicate='intersects')
        self.geomap = self.geomap[~self.geomap.index.duplicated(keep='first')]
        self.geomap.drop(columns=['index_right'], inplace=True)

        dfs = [self.age_group, self.length_residence, self.micro_income, self.how_to_build]
        for i, df in enumerate(dfs):
            self.geomap= pd.merge(self.geomap, df, on='KEY_CODE', how='left')
        print('統計値特徴量の作成終了')
    
    def small_area_feature(self):
        #小地域ポリゴンのdfのうち必要なカラムに絞る
        dfs = [self.small_area, self.age_group, self.length_residence, self.micro_income, self.how_to_build]
        for i, df in enumerate(dfs):
            if i == 0:
                self.features = df
            else:
                self.features = pd.merge(self.features, df, on='KEY_CODE', how='left')
    

    # 建物データの処理
    
    def bldg_attrs(self):
        # 建物属性の追加(面積，周囲長，矩形度)
        self.geomap = bldg_attrs(self.geomap, self.crs)
        #bldg座標系6676
    
    def bldg_type(self):
        # 建物タイプのダミー変数を追加
        self.geomap = bldg_type(self.geomap)

    def attach_poi(self):
        self.geomap = attach_poi_to_buildings(self.geomap, self.poi, self.crs)
        print('建物特徴量の作成終了')
        #bldg座標系6676

    def exclusion_usage_area(self):
        try:
            self.usage_area_path = str(self.usage_area_path).format(target_area=self.target_area)
            self.usage_area = gpd.read_file(self.usage_area_path, encoding='shift_jis') #ないファイルがある可能性があるのでデータのロードはここで
            # 特定の用途地域の建物を除外する
            self.geomap = exclusion_usage_area(self.geomap, self.usage_area, self.crs)
        except Exception as e:
            print(f"Error reading usage area file: {e}")
            return
        # 特定の用途地域の建物を除外する
        self.geomap = exclusion_usage_area(self.geomap, self.usage_area, self.crs)

    @slackapp.notify
    def save_features(self):
        # 特徴量の保存
        self.output_dir_path = str(self.output_dir_path).format(target_area=self.target_area)
        os.makedirs(self.output_dir_path, exist_ok=True)
        self.output_path = str(self.output_path).format(target_area=self.target_area)
        self.geomap.to_parquet(
                self.output_path,
                index=False,
                compression="brotli",
                )
        self.output_features_path = str(self.output_features_path).format(target_area=self.target_area)
        self.features.to_parquet(
                self.output_features_path,
                index=False,
                compression="brotli",
                )


    def run(self):
        # 特徴量エンジニアリングの実行
        self.load_data()
        self.add_keycode()
        self.age_group_ratio()
        self.per_length_residence()
        self.household_income_ratios()
        self.building_type()
        self.join_small_area()
        self.small_area_feature()
        
        # 建物データの処理
        self.bldg_attrs()
        self.bldg_type()
        # self.join_usage_area()
        # self.clean_data()
        self.attach_poi()
        self.exclusion_usage_area()
        # self.smallfeature_join_bldg()

        # 特徴量の保存
        self.save_features()