from feature_engineering import FeatureEngineering

if __name__ == "__main__":
    #特徴量作成クラス
    #特徴量のパス
    age_group_path = 'G:/マイドライブ/akiyamalab/オープン住宅地図/code_data/EDA/step3/国勢調査/第3表_年齢階級.csv'
    ownertype_path = 'G:/マイドライブ/akiyamalab/オープン住宅地図/code_data/EDA/step3/国勢調査/第7表_住宅の所有関係別一般世帯数2020小地域集計.csv'
    year_income_path = 'G:/マイドライブ/akiyamalab/オープン住宅地図/code_data/EDA/step3/住宅土地統計調査/第44-4表_世帯の年間収入階級.xlsx'
    length_residence_path = 'G:/マイドライブ/akiyamalab/オープン住宅地図/code_data/EDA/step3/国勢調査/第18表_居住期間小地域集計2020.csv'
    small_area_path = 'G:/マイドライブ/akiyamalab/オープン住宅地図/code_data/EDA/step4/小地域ポリゴン/A002005212020DDSWC15202/r2ka15202.shp'
    how_to_build_path = 'G:/マイドライブ/akiyamalab/オープン住宅地図/code_data/EDA/step3/国勢調査/第8表 _住宅の建て方別一般世帯数－町丁・字等2020.csv'
    usage_area_path = 'G:/マイドライブ/akiyamalab/オープン住宅地図/code_data/EDA/step4/新潟県用途地域/A29-11_15.shp'
    poi_path = '//Akiyamalab_02/Akiyamalab02/科研費B/B_Building_Type_Clasification/data/raw/polygon/poi/15/15202.parquet'
    #建物データ
    target_area = 15202
    basemap_path = 'G:/マイドライブ/akiyamalab/オープン住宅地図/dev_2025/train/data_processor/{target_area}/basemap/{target_area}.parquet'
    plateau_path = 'G:/マイドライブ/akiyamalab/オープン住宅地図/dev_2025/train/data_processor/{target_area}/plateau/{target_area}.parquet'
    # basemap_path = "G:/マイドライブ/akiyamalab/オープン住宅地図/dev/nagaoka/step1/nagaoka_basemap.parquet"
    # plateau_path = "G:/マイドライブ/akiyamalab/オープン住宅地図/dev/nagaoka/step2/nagaoka_plateau.parquet"
    crs = 6676
    target_usage = 411
    # 出力パス
    output_path = 'G:/マイドライブ/akiyamalab/オープン住宅地図/dev_2025/train/feature_engineering/detached/{target_area}.parquet'
    smallarea_output_path = 'G:/マイドライブ/akiyamalab/オープン住宅地図/dev_2025/train/feature_engineering/detached/15202_smallfeature.parquet'

    featureengineering = FeatureEngineering(age_group_path,
                                             ownertype_path,
                                             year_income_path,
                                             length_residence_path,
                                             small_area_path,
                                             how_to_build_path,
                                             usage_area_path,
                                             target_area,
                                             basemap_path,
                                             plateau_path,
                                             poi_path,
                                             crs,
                                             target_usage,
                                             output_path,
                                             smallarea_output_path)
    
    featureengineering.run()