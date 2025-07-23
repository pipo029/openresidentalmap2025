#建物タイプのダミー変数を追加するモジュール

import pandas as pd

def bldg_type(gdf):
    pd.set_option('future.no_silent_downcasting', True)
    #普通か堅ろう住宅の説明変数を追加
    gdf = pd.get_dummies(gdf, columns=['type'])
    print("gdf columns before replace:", gdf.columns) # 追加
    col = ['type_堅ろう建物', 'type_堅ろう無壁舎', 'type_普通建物', 'type_普通無壁舎']
    existing_cols = [c for c in col if c in gdf.columns]

    # 存在するカラムに対してのみ replace 処理を実行
    if existing_cols: # 存在するカラムが1つでもあれば処理
        gdf[existing_cols] = gdf[existing_cols].replace({True: 1, False: 0})
    else:
        print("Warning: None of the specified columns exist in the DataFrame.")

    return gdf