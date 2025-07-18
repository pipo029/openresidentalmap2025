from pathlib import Path
import os
import sys

# feature_engineering.py があるディレクトリをsys.pathに追加
# os.path.dirname(__file__) は現在のファイルのディレクトリ (15/)
# .. は一つ上のディレクトリ (feature_engineering/)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# これで feature_engineering モジュールを直接インポートできるようになる

from feature_engineering import FeatureEngineering


if __name__ == "__main__":
    #特徴量作成クラス
    #特徴量のパス
    # --- プロジェクトのルートディレクトリを特定する（ここが一番重要かつスマートな部分） ---
    # 1. 現在のスクリプトファイルの絶対パスを取得
    current_file_path = Path(__file__).resolve()

    # 2. プロジェクトのルートディレクトリを特定
    # 例: スクリプトが 'オープン住宅地図/code_2025/extrapolation/predict/main.py' にある場合
    # .parent は親ディレクトリを取得します。
    # 3回 .parent を適用することで、'オープン住宅地図' ディレクトリに到達します。
    project_root = current_file_path.parent.parent.parent.parent.parent.parent

    # --- ここから、すべてのパスを project_root からの相対パスとして定義する ---
    # データパスの基底
    data_root = project_root / 'code_data'

    # 特徴量作成クラスのパス
    age_group_path = data_root / 'feture_engineering' / 'census' / '15' / '第3表_年齢階級.csv'
    ownertype_path = data_root / 'feture_engineering' / 'census' / '15' / '第7表_住宅の所有関係別一般世帯数2020小地域集計.csv'
    year_income_path = data_root / 'feture_engineering' / 'housing_and_land_survey' / '15' / '第44-4表_世帯の年間収入階級.xlsx'
    length_residence_path = data_root / 'feture_engineering' / 'census' / '15' / '第18表_居住期間小地域集計2020.csv'
    target_small_area = '村上市'
    small_area_path = data_root / 'feture_engineering' / 'census' / '15' / 'A002005212020DDSWC15' / 'r2ka15.shp'
    how_to_build_path = data_root / 'feture_engineering' / 'census' / '15' / '第8表 _住宅の建て方別一般世帯数－町丁・字等2020.csv'
    poi_target = '15212'
    poi_path = '//Akiyamalab_02/Akiyamalab02/科研費B/B_Building_Type_Clasification/data/raw/polygon/poi/15/{poi_target}.parquet'
    usage_area_path = 'G:/マイドライブ/akiyamalab/オープン住宅地図/code_data/feture_engineering/nlfpt/15/用途地域/01-01_シェープファイル形式/A29-19_{target_area}.shp'
    # 建物データ（basemap）パス
    # dev_2025 ディレクトリをルートとして結合
    target_area = '15212'
    dev_root = project_root / 'dev_2025'
    geomap_path = dev_root / 'extrapolation' / 'data_processor' / '{target_area}' / 'basemap' / '{target_area}.parquet'
    crs = 6676

    # 出力パス
    output_dir_path = dev_root / 'extrapolation' / 'feature_engineering' / 'detached' / '{target_area}'
    output_path = dev_root / 'extrapolation' / 'feature_engineering' / 'detached' / '{target_area}' / '{target_area}.parquet'
    output_features_path = dev_root / 'extrapolation' / 'feature_engineering' / 'detached' /  '{target_area}' / '{target_area}_features.parquet'

    featureengineering = FeatureEngineering(age_group_path,
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
                                             )
    
    featureengineering.run()