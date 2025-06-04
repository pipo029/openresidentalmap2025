#モデルの学習

import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import Point
from shapely.wkt import loads
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib import font_manager
import xgboost as xgb
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.model_selection import KFold, train_test_split
import shap
import optuna
from sklearn.metrics import confusion_matrix

class Train_model:
    def __init__(self,
                 teacher_data_path,
                 ):
        self.teacher_data_path = teacher_data_path
    
    def load_data(self):
        self.teacher_data = gpd.read_parquet(self.teacher_data_path)
    
    def claean_data(self):
        

    def objective(self, trial, X, y, X_test, y_test):
        # Optunaの目的関数
        # ハイパーパラメータの範囲をOptunaで探索
        params = {
            'objective': 'binary:logistic',  # 二値分類タスク
            'eval_metric': 'logloss',  # 評価指標
            'max_depth': trial.suggest_int('max_depth', 3, 10),  # 決定木の深さ
            'eta': trial.suggest_loguniform('eta', 0.01, 0.5),  # 学習率
            'subsample': trial.suggest_uniform('subsample', 0.5, 1.0),  # サンプリングの割合
            'colsample_bytree': trial.suggest_uniform('colsample_bytree', 0.5, 1.0),  # 特徴量のサンプリングの割合
            'seed': 42,  # 乱数シード
        }

        # 交差検証
        kf = KFold(n_splits=3, shuffle=True, random_state=42)
        f1_list = []
        for fold, (train_index, val_index) in enumerate(kf.split(X)):
            X_train, X_val = X.iloc[train_index], X.iloc[val_index]
            y_train, y_val = y.iloc[train_index], y.iloc[val_index]

            # DMatrix形式に変換
            dtrain = xgb.DMatrix(X_train, label=y_train)
            dval = xgb.DMatrix(X_val, label=y_val)

            # モデルを学習
            evals = [(dtrain, 'train'), (dval, 'eval')]
            model = xgb.train(params, dtrain, num_boost_round=100, evals=evals,
                            early_stopping_rounds=10, verbose_eval=False)

            # 検証データでの予測
            preds_proba = model.predict(dval)
            preds = (preds_proba >= 0.5).astype(int)

            # 検証データでの精度を計算
            f1 = f1_score(y_val, preds)
            f1_list.append(f1)
            print(f"F1スコア（各Fold）: {f1_list}")
            print(f"平均F1スコア: {np.mean(f1_list):.4f}")
            print(f"F1スコアの標準偏差: {np.std(f1_list):.4f}")

        return np.mean(f1_list)

    # モデルを最適化する関数
    def optimize_xgb_with_optuna(self, X, y, X_test, y_test):
        # Optunaのstudyを作成
        study = optuna.create_study(direction='maximize')
        study.optimize(lambda trial: self.objective(trial, X, y, X_test, y_test), n_trials=50)
        best_params = study.best_trial.params
        
        # 最適なハイパーパラメータを表示
        print('Best trial: ', study.best_trial.params)
        # 最適なハイパーパラメータで最終モデルをトレーニング
        best_params = study.best_trial.params

        # 各foldで作成したモデルを保存するリスト
        models = []

        # 各foldの予測精度を格納するリスト
        accuracy_list = []
        precision_list = []
        recall_list = []
        f1_list = []

        # feature importancesを格納するDataFrame
        feature_importances_df = pd.DataFrame()

        # 交差検証
        kf = KFold(n_splits=3, shuffle=True, random_state=42)
        for fold, (train_index, val_index) in enumerate(kf.split(X)):
            X_train, X_val = X.iloc[train_index], X.iloc[val_index]
            y_train, y_val = y.iloc[train_index], y.iloc[val_index]

            # DMatrix形式に変換
            dtrain = xgb.DMatrix(X_train, label=y_train)
            dval = xgb.DMatrix(X_val, label=y_val)
            dtest = xgb.DMatrix(X_test, label=y_test)  # テストデータ用DMatrix

            # モデルを学習
            evals = [(dtrain, 'train'), (dval, 'eval')]
            model = xgb.train(best_params, dtrain, num_boost_round=100, evals=evals,
                            early_stopping_rounds=10, verbose_eval=False)

            # feature importancesを取得
            feature_importances = pd.DataFrame()
            feature_importances["feature"] = X.columns
            # XGBoostの特徴量重要度を取得し、存在しない特徴量の重要度を0に設定
            importance_dict = model.get_score(importance_type='weight')
            feature_importances["importance"] = feature_importances["feature"].map(importance_dict).fillna(0)
            feature_importances["fold"] = fold
            feature_importances_df = pd.concat([feature_importances_df, feature_importances], axis=0)
            # テストデータでの予測確率を取得
            preds_proba = model.predict(dtest)
            # 予測結果を取得（しきい値0.5）
            preds = (preds_proba >= 0.5).astype(int)
            print("=" * 50)
            print(f"Start of Fold {fold + 1}")

            # テストデータでの評価
            accuracy = accuracy_score(y_test, preds)
            precision = precision_score(y_test, preds)
            recall = recall_score(y_test, preds)
            f1 = f1_score(y_test, preds)

            # 混同行列を取得して先に表示（数値）
            cm = confusion_matrix(y_test, preds)
            cm_float = cm.astype(float)
            print(f"Fold {fold + 1} - Confusion Matrix (Precise Values):\n{cm_float}")
            # 表示
            print("\n===== 最適化されたハイパーパラメータ =====")
            for key, val in best_params.items():
                print(f"  {key}: {val}")
            # スコアも表示
            print(f"Fold {fold + 1} - Test Set Results:")
            print(f"Accuracy: {accuracy:.3f}")
            print(f"Precision: {precision:.3f}")
            print(f"Recall: {recall:.3f}")
            print(f"F1 Score: {f1:.3f}")
            print("-" * 40)
            # プロットは最後に
            sns.heatmap(cm_float, annot=True, fmt=".10g", cmap='Blues')
            plt.title(f"Confusion Matrix - Fold {fold + 1}")
            plt.show()
            print(f"End of Fold {fold + 1}")
            print("=" * 50)
            # モデルを保存
            models.append(model)

        # 各foldの平均feature importances
        mean_feature_importances = feature_importances_df.groupby("feature")["importance"].mean().reset_index()
        mean_feature_importances = mean_feature_importances.sort_values(by="importance", ascending=False)
        # 重要度が高い上位20を図示
        plt.figure(figsize=(16, 10))
        mean_feature_importances_20 = mean_feature_importances.head(20)
        plt.barh(mean_feature_importances_20["feature"], mean_feature_importances_20["importance"])
        plt.xlabel("重要度", fontsize=20)
        plt.ylabel("特徴量", fontsize=20)
        plt.gca().invert_yaxis()
        plt.xticks(fontsize=20)
        plt.yticks(fontsize=20)
        plt.grid(True, linestyle='--', zorder=0)
        plt.show()
        # TreeExplainerでSHAP値計算（すでにやっている場合は再実行不要）
        explainer = shap.TreeExplainer(models[1])
        shap_values = explainer.shap_values(X_test)
        # SHAP値をDataFrameに変換
        shap_df = pd.DataFrame(shap_values, columns=X_test.columns)
        # 上位10特徴量の名前（平均絶対値が大きい順）
        top_10_features = shap_df.abs().mean().sort_values(ascending=False).head(10).index.tolist()
        # summary_plot（上位10個に限定）
        shap.summary_plot(shap_df[top_10_features].values, X_test[top_10_features], plot_type='dot')



    def run(self):
