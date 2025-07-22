# 実行ファイル
from data_processor import DataProcessor

if __name__ == "__main__":
    #データの前処理クラス
    #input_data
    #基盤地図
    area = 'hokuriku'
    target_area = '新潟市'
    widearea_basemap_path = '//Akiyamalab_02/Akiyamalab02/DRM/prj_データセット開発/data/raw/基盤地図_建物/bld_poligon/FG-GML-{basemap_area}-ALL-02-Z001.parquet'
    government_polygon_path = 'G:/マイドライブ/akiyamalab/オープン住宅地図/code_data/EDA/step1/行政区域レイヤ.geojson'
    #plateau
    target_plateau_area = 15100
    plateau_path = '//Akiyamalab_02/Akiyamalab02/PLATEAU/Data_parquet/{target_plateau_area}/{target_plateau_area}.parquet'

    #output_data
    output_dir = 'G:/マイドライブ/akiyamalab/オープン住宅地図/dev_2025/train/data_processor/{target_plateau_area}'
    output_basemap_path = 'G:/マイドライブ/akiyamalab/オープン住宅地図/dev_2025/train/data_processor/{target_plateau_area}/basemap/{target_plateau_area}.parquet'
    output_plateau_path = 'G:/マイドライブ/akiyamalab/オープン住宅地図/dev_2025/train/data_processor/{target_plateau_area}/plateau/{target_plateau_area}.parquet'


    dataProcessor = DataProcessor(area,
                                  target_area,
                                  target_plateau_area,
                                  widearea_basemap_path,
                                  government_polygon_path,
                                  plateau_path,
                                  output_dir,
                                  output_basemap_path,
                                  output_plateau_path)
    dataProcessor.run()


    
    