# 実行ファイル
from apart_train_model import Apart_train_model

if __name__ == "__main__":
    #教師データのパス
    teacher_data = "G:/マイドライブ/akiyamalab/オープン住宅地図/dev_2025/feature_engineering/15202.parquet"
    target_usage = 412
    model_output_path = "G:/マイドライブ/akiyamalab/オープン住宅地図/dev_2025/train_model/15202_.json"


    train_model = Apart_train_model(teacher_data,
                              target_usage,
                              model_output_path
                             )
    
    train_model.run()