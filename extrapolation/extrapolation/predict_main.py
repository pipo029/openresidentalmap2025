# 実行ファイル
from predict import Predict

if __name__ == "__main__":
    #外挿クラス
    target_area = '06402'
    bldg_path = "G:/マイドライブ/akiyamalab/オープン住宅地図/dev_2025/extrapolation/feature_engineering/{target_area}.parquet"
    features_path = "G:/マイドライブ/akiyamalab/オープン住宅地図/dev_2025/extrapolation/feature_engineering/{target_area}_features.parquet"
    model_path = "G:/マイドライブ/akiyamalab/オープン住宅地図/dev_2025/train/train_model/15202_detached.json"
    crs = 6678
    #output_data
    output_dir = 'G:/マイドライブ/akiyamalab/オープン住宅地図/dev_2025/extrapolation/predict/{target_area}'
    output_path = 'G:/マイドライブ/akiyamalab/オープン住宅地図/dev_2025/extrapolation/predict/{target_area}/{target_area}.parquet'

    predict = Predict(target_area,
                      bldg_path,
                      features_path,
                      model_path,
                      crs,
                      output_dir,
                      output_path
                      )
    predict.run()
