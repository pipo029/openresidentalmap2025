#特徴量の作成

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from features import (
    add_KEYCODE,
    age_group_ratio,
    per_length_residence,
    household_income_ratios,
    building_type,
    join_usage_area,
    bldg_attrs,
    bldg_type,

)



class FeatureEngineering:
    def __init__(self, age_group_path, ownertype_path,
                 year_income_path, length_residence_path, small_area_path,
                 city_code_path, how_to_build_path, usage_area_path, 
                 geomap, plateau, crs,
                 target_area, output_path):
        # 特徴量のパス
        self.age_group_path = age_group_path
        self.ownertype_path = ownertype_path
        self.year_income_path = year_income_path
        self.length_residence_path = length_residence_path
        self.small_area_path = small_area_path
        self.city_code_path = city_code_path
        self.how_to_build_path = how_to_build_path
        self.usage_area_path = usage_area_path
        # 建物データ
        self.geomap = geomap
        self.plateau = plateau
        self.crs = crs
        # 出力パス
        self.target_area = target_area
        self.output_path = output_path
    
    def load_data(self):
        # 特徴量データの読み込み
        self.age_group = pd.read_csv(self.age_group_path)
        self.ownertype = pd.read_csv(self.ownertype_path)
        self.year_income = pd.read_excel(self.year_income_path)
        self.length_residence = pd.read_csv(self.length_residence_path)
        self.small_area = gpd.read_file(self.small_area_path)
        self.city_code = pd.read_excel(self.city_code_path)
        self.how_to_build = pd.read_csv(self.how_to_build_path)
        self.usage_area = gpd.read_file(self.usage_area_path, encoding='shift_jis')
        self.poi_path = 

    
    def add_keycode(self):
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
        self.micro_income = household_income_ratios(self.year_income, self.ownertype)
    
    def building_type(self):
        # 建て方別世帯数を計算
        self.how_to_build = building_type(self.how_to_build)
    
    def join_small_area(self):
        # 小地域ポリゴンと結合
        self.small_area = self.small_area[['KEY_CODE', 'PREF_NAME', 'CITY_NAME', 'S_NAME', 'geometry']] #小地域ポリゴンのdfのうち必要なカラムに絞る
        dfs = [self.small_area, self.age_group, self.length_residence, self.micro_income, self.how_to_build]
        for i, df in enumerate(dfs):
            if i == 0:
                self.features = df
            else:
                self.features = pd.merge(self.features, df, on='KEY_CODE', how='left')
    

    # 建物データの処理
    
    def plateau_join_to_geomap(self):
        # plateauデータと基盤地図の結合
        # 各ポリゴンの重心を求める
        self.plateau['centroid'] = self.plateau['geometry'].centroid     
        # 空のジオメトリに対処する
        self.plateau['geometry'] = self.plateau['centroid'].apply(lambda x: Point(x.x, x.y) if not x.is_empty else Point())   
        # 重心カラムを削除する
        self.plateau = self.plateau.drop(columns=['centroid'])

        # 基盤地図とplateauデータの結合
        self.plateau.rename(columns={'id':'buildingID'}, inplace=True)
        self.plateau = self.plateau[['class', 'usage', 'buildingID', 'geometry']]
        #基盤地図にplateauデータを空間結合
        self.bldg = gpd.sjoin(self.geomap, self.plateau, how='left', op='contains', )
        self.bldg.drop(columns=['index_right'], inplace=True)
        # インデックスの重複を削除
        self.bldg = self.bldg[~self.bldg.index.duplicated(keep='first')]
    
    def bldg_attrs(self):
        # 建物属性の追加(面積，周囲長，矩形度)
        self.bldg = self.bldg_attrs(self.bldg, self.crs)
    
    def bldg_type(self):
        # 建物タイプのダミー変数を追加
        self.bldg = bldg_type(self.bldg)

    def join_usage_area(self):
        # 用途地域の結合
        self.usage_area = self.usage_area[['id', 'class', 'usage', 'geometry']]
        self.usage_area = gpd.GeoDataFrame(self.usage_area, geometry='geometry', crs='EPSG:4326')
        self.bldg = join_usage_area(self.bldg, self.usage_area)
    
    def clean_data(self):
        self.bldg = self.bldg.iloc[:, 8:]
        columns = ['00_総数', '09_1000以上']
        self.bldg.drop(columns=columns, axis=1, inplace=True)


    def target_variable(self):
        # 目的変数の追加
        self.bldg['target'] = self.bldg['usage'] == 411
        self.bldg['target'] = self.bldg['target'].astype(int)
    
    def save_features(self):
        # 特徴量の保存
        self.output_path = self.output_path.format(target_area=self.target_area)
        self.features.to_parquet(
                self.output_path,
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
        
        # 建物データの処理
        self.plateau_join_to_geomap()
        self.bldg_attrs()
        self.bldg_type()
        self.join_usage_area()
        self.clean_data()
        self.target_variable()

        # 特徴量の保存
        self.save_features()