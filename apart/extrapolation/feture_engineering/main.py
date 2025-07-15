from feature_engineering import FeatureEngineering

if __name__ == "__main__":
    usage_area_path = 'G:/マイドライブ/akiyamalab/オープン住宅地図/code_data/EDA/step4/新潟県用途地域/A29-11_15.shp'
    #建物データ
    target_area = 15212
    bldg_path = 'G:/マイドライブ/akiyamalab/オープン住宅地図/dev_2025/extrapolation/predict/detached/{target_area}/{target_area}.parquet'

    crs = 6676
    target_usage = 412
    # 出力パス
    output_path = 'G:/マイドライブ/akiyamalab/オープン住宅地図/dev_2025/extrapolation/feature_engineering/apart/{target_area}_apart.parquet'
    output_features_path = 'G:/マイドライブ/akiyamalab/オープン住宅地図/dev_2025/extrapolation/feature_engineering/apart/{target_area}_apart_features.parquet'

    featureengineering = FeatureEngineering(
                                             usage_area_path,
                                             target_area,
                                             bldg_path,                                             
                                             crs,
                                             target_usage,
                                             output_path,
                                             output_features_path)
    
    featureengineering.run()