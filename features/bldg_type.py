#建物タイプのダミー変数を追加するモジュール

import pandas as pd

def bldg_type(gdf):
    #普通か堅ろう住宅の説明変数を追加
    gdf = pd.get_dummies(gdf, columns=['type'])
    col = ['type_堅ろう建物', 'type_堅ろう無壁舎', 'type_普通建物', 'type_普通無壁舎']
    #get_dummiesはTrueとFalseを返すので1と0に置き換える
    gdf[col] = gdf[col].replace({True: 1, False: 0})

    return gdf