# 実行ファイル
from data_processor import DataProcessor
from feature_engineering import FeatureEngineering

if __name__ == "__main__":
    #データの前処理クラス
    #基盤地図
    area = 'hokuriku'
    target_area = '長岡市'
    widearea_geomap_path = '//Akiyamalab_02/Akiyamalab02/DRM/prj_データセット開発/data/raw/基盤地図_建物/bld_poligon/FG-GML-{basemap_area}-ALL-02-Z001.parquet'
    government_polygon_path = 'G:/マイドライブ/akiyamalab/オープン住宅地図/code_data/EDA/step1/行政区域レイヤ.geojson'
    output_basemap_path = 'G:/マイドライブ/akiyamalab/オープン住宅地図/dev_2025/data_processor/{target_plateau_area}_basemap.parquet'
    #plateau
    target_plateau_area = 15202
    plateau_path = '//Akiyamalab_02/Akiyamalab02/PLATEAU/Data_gpkg/{target_plateau_area}/{target_plateau_area}.gpkg'
    output_plateau_path = 'G:/マイドライブ/akiyamalab/オープン住宅地図/dev_2025/data_processor/{target_plateau_area}_plateau.parquet'

    dataProcessor = DataProcessor(area,
                                  target_area,
                                  target_plateau_area,
                                  widearea_geomap_path,
                                  government_polygon_path,
                                  output_basemap_path,
                                  plateau_path,
                                  output_plateau_path)
    dataProcessor.run()


    #特徴量作成クラス
    #特徴量のパス
    age_group_path = 'G:/マイドライブ/akiyamalab/オープン住宅地図/code_data/EDA/step3/国勢調査/第3表_年齢階級.csv'
    ownertype_path = 'G:/マイドライブ/akiyamalab/オープン住宅地図/code_data/EDA/step3/国勢調査/第7表_住宅の所有関係別一般世帯数2020小地域集計.csv'
    year_income_path = 'G:/マイドライブ/akiyamalab/オープン住宅地図/code_data/EDA/step3/住宅土地統計調査/第44-4表_世帯の年間収入階級.xlsx'
    length_residence_path = 'G:/マイドライブ/akiyamalab/オープン住宅地図/code_data/EDA/step3/国勢調査/第18表_居住期間小地域集計2020.csv'
    small_area_path = 'G:/マイドライブ/akiyamalab/オープン住宅地図/code_data/EDA/step4/小地域ポリゴン/A002005212020DDSWC15202/r2ka15202.shp'
    city_code_path = 'G:/マイドライブ/akiyamalab/オープン住宅地図/code_data/EDA/step3/市区町村コード.xlsx'
    how_to_build_path = 'G:/マイドライブ/akiyamalab/オープン住宅地図/code_data/EDA/step3/国勢調査/第8表 _住宅の建て方別一般世帯数－町丁・字等2020.csv'
    usage_area_path = 'G:/マイドライブ/akiyamalab/オープン住宅地図/code_data/EDA/step4/新潟県用途地域/A29-11_15.shp'
    #建物データ
    geomap = dataProcessor.target_geomap
    plateau = dataProcessor.plateau

    featureEngineering = FeatureEngineering(age_group_path,
                                             ownertype_path,
                                             year_income_path,
                                             length_residence_path,
                                             small_area_path,
                                             city_code_path,
                                             how_to_build_path,
                                             usage_area_path,
                                             geomap,
                                             plateau)