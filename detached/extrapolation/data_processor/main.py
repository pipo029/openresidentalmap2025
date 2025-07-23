# 実行ファイル
from data_processor import DataProcessor

if __name__ == "__main__":
    #データの前処理クラス
    #input_data
    #基盤地図
    basemap_area = 'hokuriku'
    target_basemap_area = '上越市'
    widearea_basemap_path = '//Akiyamalab_02/Akiyamalab02/DRM/prj_データセット開発/data/raw/基盤地図_建物/bld_poligon/FG-GML-{basemap_area}-ALL-02-Z001.parquet'
    government_polygon_path = 'G:/マイドライブ/akiyamalab/オープン住宅地図/code_data/EDA/step1/行政区域レイヤ.geojson'

    #output_data
    target_area = '15222'
    output_dir = 'G:/マイドライブ/akiyamalab/オープン住宅地図/dev_2025/extrapolation/data_processor/{target_area}'
    output_basemap_path = 'G:/マイドライブ/akiyamalab/オープン住宅地図/dev_2025/extrapolation/data_processor/{target_area}/basemap/{target_area}.parquet'


    dataProcessor = DataProcessor(basemap_area,
                                  target_basemap_area,
                                  widearea_basemap_path,
                                  government_polygon_path,
                                  target_area,
                                  output_dir,
                                  output_basemap_path
                                  )
    dataProcessor.run()


    
    