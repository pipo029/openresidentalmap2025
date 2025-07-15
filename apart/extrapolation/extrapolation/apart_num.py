import pandas as pd
import numpy as np

def calculate_apportioned_apartments(jucho, kokusei, target_city_code):
    """
    住宅土地統計調査と国勢調査のデータを用いて、小地域単位で共同住宅数を按分計算する。

    Args:
        jucho (pd.DataFrame): 住宅土地統計調査データ (第１５４－３表ベース)
        kokusei (pd.DataFrame): 国勢調査データ (第８表ベース)
        target_pref_code (str): 対象とする都道府県コード（2桁）

    Returns:
        pd.DataFrame: 小地域単位で按分された共同住宅数
    """

    # --- 1. データの前処理 ---

    # 住宅土地統計調査 (住調) の前処理
    # 必要なカラム: 'KEYCODE'(市区町村コード5桁を想定), '共同住宅数' (棟数または戸数)
    # ※設計では「むね数」だが、国勢調査の「世帯数」で按分するため、単位を揃える必要がある。
    # ここでは 'jucho_COUNT' が按分対象の総数（戸数相当）と仮定する。
    # 対象都道府県のデータのみに絞る
    target_pref_code = target_city_code[:2]  # 都道府県コードは最初の2桁
    jucho = jucho[jucho['地域区分'].str.startswith(target_pref_code)].copy()
    jucho['CITY_CODE'] = jucho['地域区分'].str[:5]
    # 建物の構造カラムが「0_総数」のみに絞る
    jucho = jucho[jucho['建物の構造'] == '0_総数'].copy()

    # 「1_長屋建」と「2_共同住宅」の総数を「number_apart」として作成
    # 数値型に変換（エラーはNaNに変換し、0で埋める）
    jucho['1_長屋建'] = pd.to_numeric(jucho['1_長屋建'], errors='coerce').fillna(0)
    jucho['2_共同住宅'] = pd.to_numeric(jucho['2_共同住宅'], errors='coerce').fillna(0)
    jucho['1_長屋建'] = jucho['1_長屋建'].replace('-', 0).astype(int)
    jucho['2_共同住宅'] = jucho['2_共同住宅'].replace('-', 0).astype(int)

    # 国勢調査 (国調) の前処理
    kokusei['apart_num'] = kokusei['長屋建'] + kokusei['共同住宅']

    # 市区町村コード（5桁）の準備
    # 国調の KEYCODE は小地域コード（例: 11桁）を想定
    kokusei['CITY_CODE'] = kokusei['KEY_CODE'].str[:5]


    # --- 2. 住調データがある地域とない地域の特定 ---

    jucho_city_codes = jucho['CITY_CODE'].unique()
    kokusei_city_codes = kokusei['CITY_CODE'].unique()

    # 住調にデータが存在する市区町村
    cities_with_jucho = set(jucho_city_codes)
    # 住調にデータが存在しないが、国調には存在する市区町村
    cities_without_jucho = set(kokusei_city_codes) - cities_with_jucho

    results = []

    # --- 3. 条件分岐1: 対象地域（住調データ）がある場合の按分 ---

    if target_city_code not in cities_without_jucho:
        # 対象地域の国調データを抽出
        kokusei_with_jucho = kokusei[kokusei['KEY_CODE'].str.startswith(target_city_code)].copy()


        # 国調ベースの市区町村における共同住宅合計数を算出
        apart_households_total = kokusei[kokusei['CITY_CODE'] == target_city_code]['apart_num'].sum()

        # 按分比率の計算: (小地域の共同住宅数) / (市区町村の共同住宅総数)
        # ゼロ除算を防ぐ
        kokusei_with_jucho['apart_ratio'] = kokusei_with_jucho['apart_num'] / apart_households_total
        kokusei_with_jucho['apart_ratio'] = kokusei_with_jucho['apart_ratio'].fillna(0)

        # 住調の市区町村別データ（按分したい実際の合計値）を結合
        jucho = jucho[jucho['地域区分'].str.startswith(target_city_code)]
        apart_buildings_total = (jucho['1_長屋建'] + jucho['2_共同住宅']).iloc[0]

        # 按分計算: 比率 * 住調の市区町村合計
        kokusei_with_jucho['apart_apportion_count'] = kokusei_with_jucho['apart_ratio'] * apart_buildings_total

        return kokusei_with_jucho

    # --- 4. 条件分岐2: 対象地域（住調データ）がない場合の按分 ---

    else:
        print(f"Processing cities without jucho data: {len(cities_without_jucho)}")

        # 4-1. 住調データがない地域の共同住宅総数（住調ベース）を推計する
        
        # 住調の都道府県合計 (※住調データに都道府県合計の行 'PREF_TOTAL_CODE' があると仮定)
        jucho['apart_bldg_num'] = jucho['1_長屋建'] + jucho['2_共同住宅']
        # 都道府県の共同住宅の合計棟数（１行目）から住調にデータがある市区町村の共同住宅の棟数（２行目以降）を引くことでデータがない市区町村の共同住宅の棟数を算出．
        apart_bldg_pref_total = jucho['apart_bldg_num'].iloc[0]
        apart_bldg_total_with_jucho = jucho['apart_bldg_num'].iloc[1:].sum()
        apart_bldg_total_without_jucho = apart_bldg_pref_total - apart_bldg_total_with_jucho


        # 4-2. 住調データがない地域の国調データを用いて按分する

        # 住調データがない市区町村の国調データ（小地域）を抽出
        kokusei_without_jucho = kokusei[kokusei['CITY_CODE'].isin(cities_without_jucho)].copy()

        # 国調ベースで、この「住調データがない地域全体」の共同住宅総数を算出
        apart_households_total = kokusei_without_jucho['apart_num'].sum()

        # 按分比率の計算: (小地域の共同住宅数) / (住調データがない地域全体の共同住宅総数)
        kokusei_without_jucho = kokusei_without_jucho[kokusei_without_jucho['CITY_CODE'] == target_city_code].copy()
        if apart_households_total > 0:
            kokusei_without_jucho['apart_ratio'] = kokusei_without_jucho['apart_num'] / apart_households_total
        else:
            kokusei_without_jucho['apart_ratio'] = 0

        # 按分計算: 比率 * 推計された住調データがない地域の合計
        kokusei_without_jucho['apart_apportion_count'] = kokusei_without_jucho['apart_ratio'] * apart_bldg_total_without_jucho

    return kokusei_without_jucho