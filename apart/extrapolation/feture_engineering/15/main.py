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

    # 建物データ（basemap）パス
    # dev_2025 ディレクトリをルートとして結合
    target_area = '15212'
    dev_root = project_root / 'dev_2025'
    bldg_path = dev_root / 'extrapolation' / 'predict' / 'detached' / '{target_area}' / '{target_area}.parquet'
    crs = 6676
    # 学校と病院のパス
    schools_path = data_root / 'feture_engineering' / 'nlfpt' / '15' / '学校' / 'P29-21_15.shp'
    hospitals_path = data_root / 'feture_engineering' / 'nlfpt' / '15' / '医療機関' / 'P04-20_15.shp'
    usage_area_path = data_root / 'feture_engineering' / 'nlfpt' / '15' / '用途地域' / '01-01_シェープファイル形式' / 'A29-19_{target_area}.shp'

    # 出力パス
    output_path = dev_root / 'extrapolation' / 'feature_engineering' / 'apart' / '{target_area}_apart.parquet'
    output_features_path = dev_root / 'extrapolation' / 'feature_engineering' / '{target_area}_apart_features.parquet'

    featureengineering = FeatureEngineering(
                                             target_area,
                                             bldg_path,
                                             crs,
                                             schools_path,
                                             hospitals_path,
                                             usage_area_path,
                                             output_path,
                                             output_features_path
                                             )
    
    featureengineering.run()