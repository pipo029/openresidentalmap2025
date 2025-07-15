# 実行ファイル
from predict import Predict

if __name__ == "__main__":
    #外挿クラス
    target_area = '15212'
    bldg_path = "G:/マイドライブ/akiyamalab/オープン住宅地図/dev_2025/extrapolation/feature_engineering/apart/{target_area}_apart.parquet"
    features_path = "G:/マイドライブ/akiyamalab/オープン住宅地図/dev_2025/extrapolation/feature_engineering/apart/{target_area}_apart_features.parquet"
    model_path = "G:/マイドライブ/akiyamalab/オープン住宅地図/dev_2025/train/train_model/15202_apart.json"
    crs = 6676
    #output_data
    output_dir = 'G:/マイドライブ/akiyamalab/オープン住宅地図/dev_2025/extrapolation/predict/{target_area}'
    output_path = 'G:/マイドライブ/akiyamalab/オープン住宅地図/dev_2025/extrapolation/predict/{target_area}/{target_area}_apart.parquet'

    predict = Predict(target_area,
                      bldg_path,
                      features_path,
                      model_path,
                      crs,
                      output_dir,
                      output_path
                      )
    predict.run()
