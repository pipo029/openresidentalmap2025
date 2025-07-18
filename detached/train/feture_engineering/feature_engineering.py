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


class FeatureEngineering:
    def __init__(self, 
                 age_group_path, 
                 ownertype_path,
                 year_income_path, 
                 length_residence_path, 
                 small_area_path,
                 how_to_build_path, 
                 usage_area_path, 
                 target_area,
                 geomap_path, 
                 plateau_path, 
                 poi_path, 
                 crs,
                 target_usage,
                 output_path,
                 smallarea_output_path ):
        # 特徴量のパス
        self.age_group_path = age_group_path
        self.ownertype_path = ownertype_path
        self.year_income_path = year_income_path
        self.length_residence_path = length_residence_path
        self.small_area_path = small_area_path
        self.how_to_build_path = how_to_build_path
        self.usage_area_path = usage_area_path
        # 建物データ
        self.target_area = target_area
        self.geomap_path = geomap_path
        self.plateau_path = plateau_path
        self.poi_path = poi_path
        self.crs = crs
        self.target_usage = target_usage
        # 出力パス
        self.output_path = output_path
        self.smallarea_output_path = smallarea_output_path 
    
    def load_data(self):
        print('データの読み込み開始')
        # 特徴量データの読み込み
        self.age_group = pd.read_csv(self.age_group_path, encoding='cp932')
        self.ownertype = pd.read_csv(self.ownertype_path, encoding='cp932')
        self.year_income = pd.read_excel(self.year_income_path)
        self.length_residence = pd.read_csv(self.length_residence_path, encoding='cp932')
        self.small_area = gpd.read_file(self.small_area_path)
        self.how_to_build = pd.read_csv(self.how_to_build_path, encoding='cp932')
        self.usage_area = gpd.read_file(self.usage_area_path, encoding='shift_jis')
        self.poi = gpd.read_parquet(self.poi_path)

        #建物データの読み込み
        self.geomap_path = self.geomap_path.format(target_area=self.target_area)
        self.geomap = gpd.read_parquet(self.geomap_path)
        self.plateau_path = self.plateau_path.format(target_area=self.target_area)
        self.plateau = gpd.read_parquet(self.plateau_path)
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
        self.micro_income = household_income_ratios(self.year_income, self.ownertype, self.target_area)
    
    def building_type(self):
        # 建て方別世帯数を計算
        self.how_to_build = building_type(self.how_to_build)
    
    def join_small_area(self):
        # 小地域ポリゴンと結合
        self.small_area = self.small_area[['KEY_CODE', 'PREF_NAME', 'CITY_NAME', 'S_NAME', 'geometry']] #小地域ポリゴンのdfのうち必要なカラムに絞る
        self.geomap.to_crs('EPSG:4326', inplace=True)
        self.small_area.to_crs('EPSG:4326', inplace=True)
        self.geomap = gpd.sjoin(self.geomap, self.small_area, how='left', predicate='intersects')
        self.geomap = self.geomap[~self.geomap.index.duplicated(keep='first')]
        self.geomap.drop(columns=['index_right'], inplace=True)

        dfs = [self.age_group, self.length_residence, self.micro_income, self.how_to_build]
        for i, df in enumerate(dfs):
            self.geomap= pd.merge(self.geomap, df, on='KEY_CODE', how='left')
        print('統計値特徴量の作成終了')
    

    # 建物データの処理
    
    def plateau_join_to_geomap(self):
        print('建物特徴量の作成開始')
        # plateauデータと基盤地図の結合
        # 各ポリゴンの重心を求める
        # self.plateau.to_crs('EPSG:6676', inplace=True)
        # self.plateau['centroid'] = self.plateau['geometry'].centroid     
        # # 空のジオメトリに対処する
        # self.plateau['geometry'] = self.plateau['centroid'].apply(lambda x: Point(x.x, x.y) if not x.is_empty else Point())   
        # # 重心カラムを削除する
        # self.plateau = self.plateau.drop(columns=['centroid'])
        
        self.plateau.to_crs('EPSG:4326', inplace=True)

        # 基盤地図とplateauデータの結合
        self.plateau.rename(columns={'id':'buildingID'}, inplace=True)
        self.plateau = self.plateau[['buildingID', 'class', 'usage', 'geometry']]
        #基盤地図にplateauデータを空間結合
        self.geomap.to_crs('EPSG:4326', inplace=True)
        self.bldg = gpd.sjoin(self.geomap, self.plateau, how='left', predicate='intersects')
        self.bldg.drop(columns=['index_right'], inplace=True)
        # インデックスの重複を削除
        self.bldg = self.bldg[~self.bldg.index.duplicated(keep='first')]
        print(f'空間結合後の建物データのデータ数{len(self.bldg)}')
    
    def bldg_attrs(self):
        # 建物属性の追加(面積，周囲長，矩形度)
        self.bldg = bldg_attrs(self.bldg, self.crs)
        #bldg座標系6676
    
    def bldg_type(self):
        # 建物タイプのダミー変数を追加
        self.bldg = bldg_type(self.bldg)

    def join_usage_area(self):
        # 用途地域の結合
        self.usage_area = gpd.GeoDataFrame(self.usage_area, geometry='geometry', crs='EPSG:4326')
        self.bldg = join_usage_area(self.bldg, self.usage_area, self.crs)
        #bldg座標系6676

    def attach_poi(self):
        self.bldg = attach_poi_to_buildings(self.bldg, self.poi, self.crs)
        print('建物特徴量の作成終了')
        #bldg座標系6676

    # def smallfeature_join_bldg(self):
    #     self.bldg.to_crs('EPSG:4326', inplace=True)
    #     self.features.to_crs('EPSG:4326', inplace=True)
    #     self.bldg = gpd.sjoin(self.bldg, self.features, how='left', predicate='within')
    #     self.bldg.drop(columns=['index_right'], inplace=True)
    
    # def clean_data(self):
        # self.bldg = self.bldg.iloc[:, 8:]
        # columns = ['00_総数', '09_1000以上']
        # self.bldg.drop(columns=columns, axis=1, inplace=True)

    
    def save_features(self):
        # 特徴量の保存
        self.output_path = self.output_path.format(target_area=self.target_area)
        self.bldg.to_parquet(
                self.output_path,
                index=False,
                compression="brotli",
                )

        # self.features.to_parquet(
        #         self.smallarea_output_path,
        #         index=False,
        #         compression="brotli",
        #         )

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
        # self.join_usage_area()
        # self.clean_data()
        self.attach_poi()
        # self.smallfeature_join_bldg()

        # 特徴量の保存
        self.save_features()