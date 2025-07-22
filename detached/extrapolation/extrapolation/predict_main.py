# 実行ファイル
from predict import Predict

if __name__ == "__main__":
    #外挿クラス
    target_area = '15100'
    bldg_path = "G:/マイドライブ/akiyamalab/オープン住宅地図/dev_2025/extrapolation/feature_engineering/detached/{target_area}/{target_area}_detached.parquet"
    features_path = "G:/マイドライブ/akiyamalab/オープン住宅地図/dev_2025/extrapolation/feature_engineering/detached/{target_area}/{target_area}_detached_features.parquet"
    model_path = "G:/マイドライブ/akiyamalab/オープン住宅地図/dev_2025/train/train_model/15202.json"
    crs = 6676
    #output_data
    output_dir = 'G:/マイドライブ/akiyamalab/オープン住宅地図/dev_2025/extrapolation/predict/detached/{target_area}'
    output_path = 'G:/マイドライブ/akiyamalab/オープン住宅地図/dev_2025/extrapolation/predict/detached/{target_area}/{target_area}.parquet'

    predict = Predict(target_area,
                      bldg_path,
                      features_path,
                      model_path,
                      crs,
                      output_dir,
                      output_path
                      )
    predict.run()
