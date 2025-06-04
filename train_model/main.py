# 実行ファイル
from train_model import Train_model

if __name__ == "__main__":
    #教師データのパス
    teacher_data = "G:/マイドライブ/akiyamalab/オープン住宅地図/dev_2025/feature_engineering/15202.parquet"


    train_model = Train_model(teacher_data
                            )
    
    train_model.run()