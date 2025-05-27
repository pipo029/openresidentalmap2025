# 実行ファイル
from data_processor import DataProcessor

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