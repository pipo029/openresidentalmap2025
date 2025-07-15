# 外挿を行うクラス

import pandas as pd
import numpy as np
import geopandas as gpd
import xgboost as xgb
import os
from apart_num import calculate_apportioned_apartments

class Predict:
    def __init__(self,
                target_area,
                bldg_path,
                features_path,
                model_path,
                jucho_path,
                crs,
                output_dir,
                output_path
                ):
        self.target_area = target_area
        self.bldg_path = bldg_path
        self.features_path = features_path
        self.model_path = model_path
        self.jucho_path = jucho_path
        self.crs = crs
        self.output_dir = output_dir
        self.output_path = output_path
    
    def load_data(self):
        print('データの読み込み開始')
        # データの読み込み
        self.bldg_path = self.bldg_path.format(target_area=self.target_area)
        self.bldg = gpd.read_parquet(self.bldg_path)
        self.features_path = self.features_path.format(target_area=self.target_area)
        self.features = gpd.read_parquet(self.features_path)
        self.jucho = pd.read_excel(self.jucho_path, skiprows=8)
    
    def clean_data(self):
        self.later_join = self.bldg[['geometry', 'KEY_CODE']]
        need_col = ['年少人口', '生産年齢人口', '老年人口', 
                    '出生時から', '1年未満', '1年以上5年未満', '5年以上10年未満',
                    '10年以上20年未満', '20年以上', '居住期間「不詳」', '01_500万円未満', '07_500～1000万円未満',
                    '一戸建', '長屋建', '共同住宅', 
                    'area', 'rectangularity', 'convexity', 'moment_of_inertia', 'num_corners', 
                    'anisotropy', 'longest_axis', 'elongation', 'orientation',
                    'type_堅ろう建物', 'type_堅ろう無壁舎', 'type_普通建物', 'type_普通無壁舎']
        if 'type_堅ろう無壁舎' not in self.bldg.columns:
            self.bldg['type_堅ろう無壁舎'] = 0
        
        self.bldg = self.bldg[need_col]
    
    def load_model(self):
        # 新しいXGBoostモデルインスタンスを作成
        self.model = xgb.Booster() 
        # モデルをJSONファイルからロード
        self.model.load_model(self.model_path)
        print(f"モデルが正常にロードされました: {self.model_path}")
    
    def extrapolation(self):
        dtest = xgb.DMatrix(self.bldg)
        # モデルを使って新しいデータに対して予測を行う
        y_pred = self.model.predict(dtest)
        # 予測結果をデータフレームに追加
        self.bldg['prob'] = y_pred
    
    def geometry_join(self):
        self.bldg = self.bldg.join(self.later_join)
        self.bldg = gpd.GeoDataFrame(self.bldg, geometry='geometry', crs=self.crs)
    
    def calculate_apart_apportion(self):
        self.features = calculate_apportioned_apartments(self.jucho, self.features, self.target_area)

    def add_detached_flag(self):
        self.features['KEY_CODE'] = self.features['KEY_CODE'].astype(str)
        self.bldg['KEY_CODE'] = self.bldg['KEY_CODE'].astype(str)
        self.bldg['KEY_CODE'] = self.bldg['KEY_CODE'].apply(lambda x: x[:-2] if x.endswith('.0') else x)

        #戸建て住宅のリスト
        apart_list = []
        #indexごとに繰り返し
        for index in self.features.index:
            apart_count = self.features.loc[index]['apart_apportion_count']
            if pd.notna(apart_count):
                KEY_CODE = self.features.loc[index]['KEY_CODE']
                
                #KEY_CODEの建物を取得
                micro_area = self.bldg[self.bldg['KEY_CODE'] == KEY_CODE]
                micro_area = micro_area.sort_values(by='prob', ascending=False)
                micro_area = micro_area[:int(apart_count)]
                #小地域で戸建て住宅可能性順に並べて個数分の戸建て住宅のindexを取得
                apart_list.extend(micro_area.index)  # extendでリストに追加

        #self.bldgに推定戸建てのフラグを作成
        self.bldg['presumed_detached'] = 0
        self.bldg.loc[apart_list, 'presumed_detached'] = 1

    
    def save_data(self):
        self.output_dir = self.output_dir.format(target_area=self.target_area)
        os.makedirs(self.output_dir, exist_ok=True)
        self.output_path = self.output_path.format(target_area=self.target_area)
        self.bldg.to_parquet(
                self.output_path,
                index=False,
                compression="brotli",
                )
        
    def run(self):
        self.load_data()
        self.clean_data()
        self.load_model()
        self.extrapolation()
        self.geometry_join()
        self.calculate_apart_apportion()
        self.add_detached_flag()
        self.save_data()
