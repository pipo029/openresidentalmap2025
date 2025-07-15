# 実行ファイル
from train_model import Train_model

if __name__ == "__main__":
    #教師データのパス
    teacher_data_path = "G:/マイドライブ/akiyamalab/オープン住宅地図/dev_2025/train/feature_engineering/15202.parquet"
    target_usage = '411'
    model_output_path = "G:/マイドライブ/akiyamalab/オープン住宅地図/dev_2025/train/train_model/15202_detached.json"


    train_model = Train_model(teacher_data_path,
                              target_usage,
                              model_output_path
                             )
    
    train_model.run()