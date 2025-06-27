#収入階級別人口割合

import pandas as pd

def household_income_ratios(year_income_df, ownertype_df, target_area):
    # --- 市区町村コードの作成 (City Code Creation) ---
    city_codes = year_income_df['地域区分－全国・都道府県・市区町村'].str[:5].to_list()
    city_name = year_income_df['地域区分－全国・都道府県・市区町村'].str[6:].to_list()

    city = pd.DataFrame()
    city['city_code'] = city_codes
    city['city_name'] = city_name
    city = city[city['city_code'] == f'{target_area}'] #target_areaのきーこどが歩かないかで条件分岐　ない場合は県の総数から各市町村の値を引き代表値を特徴量として扱う

    # 住宅土地統計調査にデータがある場合
    if city.empty:
        pref_code = target_area[:2]
        year_income_df['普通世帯数(世帯)'].replace('-', 0, inplace=True)
        year_income_df['普通世帯数(世帯)'] = year_income_df['普通世帯数(世帯)'].astype(int)
        all_pref_df = year_income_df[year_income_df['地域区分－全国・都道府県・市区町村'].str.startswith(f'{pref_code}')]
        all_pref_df = all_pref_df[all_pref_df['世帯の種類'] == '1_主世帯']
        city_codes = year_income_df['地域区分－全国・都道府県・市区町村'].str[:5].to_list()
        city_codes = list(set(city_codes))
        target_city_codes = [code for code in city_codes if code.startswith(f'{pref_code}')]

        # 都道府県のみのデータを抽出
        pref_code = target_area[:2] + '000'
        pref_income = all_pref_df[all_pref_df['地域区分－全国・都道府県・市区町村'].str.startswith(f'{pref_code}')]

        for target_city_code in target_city_codes:
            if target_city_code == pref_code:
                continue
            else:
                city_income = all_pref_df[all_pref_df['地域区分－全国・都道府県・市区町村'].str.startswith(f'{target_city_code}')]
                pref_income['主要都市_普通世帯数(世帯)'] = city_income['普通世帯数(世帯)'].to_list()
                pref_income['普通世帯数(世帯)'] = pref_income['普通世帯数(世帯)'] - pref_income['主要都市_普通世帯数(世帯)']
                tmp_city_income = pref_income.copy()

        tmp_df = pd.DataFrame()
        classifire_df = pd.DataFrame()
        # --- 市区町村単位の収入割合を保存するための空のデータフレームを作成 (Initialize DataFrames for City Income Ratios) ---
        city_income = pd.DataFrame()
        major_city_income = pd.DataFrame()

        income_classes = [
            '00_総数', '01_100万円未満', '02_100～200万円未満', '04_200～300万円未満',
            '05_300～400万円未満', '06_400～500万円未満', '07_500～700万円未満',
            '08_700～1000万円未満', '09_1000～1500万円未満', '10_1500万円以上'
        ]

        major_classes = [
            '00_総数', '01_500万円未満', '07_500～1000万円未満', '09_1000以上',
        ]

        tmp_df['世帯の年間収入階級'] = income_classes
        tmp_df['city_code'] = pref_code

        classifire_df['世帯の年間収入階級'] = major_classes
        classifire_df['city_code'] = pref_code

        home_ownerships = [
            '総数', '持ち家', '借家', '公営の借家', '都市再生機構', '民営借家', '給与住宅'
        ]
        # 大事なのはここから

        # 住宅の所有関係別で処理を行う
        for home_ownership in home_ownerships:
            # 所有関係別で世帯数を取得（そのままの順番でtmp_dfに結合することで所有関係別収入階級別で世帯数を取得できる）
            filtered_data = tmp_city_income[tmp_city_income['住宅の所有の関係'].str.contains(home_ownership)]['普通世帯数(世帯)'].reset_index(drop=True)
            tmp_df[home_ownership] = filtered_data

            # 世帯年収階級の総数を取得
            total_value = tmp_df[home_ownership].iloc[1:10].sum()

            # 総数が0でない場合、それぞれの建物の所有形態ごとに割合を算出
            if total_value != 0:
                tmp_df[f'{home_ownership}_ratio'] = tmp_df[home_ownership] / total_value
            else:
                tmp_df[f'{home_ownership}_ratio'] = 0
            
            # もともとの収入階級別のカテゴリ分けだと多いのでカテゴリを3つに少なくする．
            # 3つの階級のそれぞれの世帯数の合計を算出
            total = tmp_df[home_ownership].iloc[1:10].sum()
            under_500 = tmp_df[home_ownership].iloc[1:6].sum() if len(tmp_df[home_ownership]) >= 5 else 0
            from_500_to_1000 = tmp_df[home_ownership].iloc[6:8].sum() if len(tmp_df[home_ownership]) >= 8 else 0
            up_to_1000 = tmp_df[home_ownership].iloc[8:10].sum() if len(tmp_df[home_ownership]) >= 10 else 0

            major_list = [total, under_500, from_500_to_1000, up_to_1000]
            classifire_df[home_ownership] = major_list

            if total != 0:
                classifire_df[f'{home_ownership}_ratio'] = classifire_df[home_ownership] / total
            else:
                classifire_df[f'{home_ownership}_ratio'] = 0



        # 国勢調査のカラムに合わせるために'公営・都市再生機構・公社の借家'カラムを新しく作成し，上記の処理を別で実行
        # Combine '公営の借家' and '都市再生機構'
        # カテゴリ分けが多い方の処理
        tmp_df['公営・都市再生機構・公社の借家'] = tmp_df['公営の借家'] + tmp_df['都市再生機構']
        home_ownerships_extended = home_ownerships + ['公営・都市再生機構・公社の借家'] # For ratio column generation
        total_public_urban = tmp_df['公営・都市再生機構・公社の借家'].iloc[1:10].sum() if not tmp_df['公営・都市再生機構・公社の借家'].empty else 0
        if total_public_urban != 0:
            tmp_df['公営・都市再生機構・公社の借家_ratio'] = tmp_df['公営・都市再生機構・公社の借家'] / total_public_urban
        else:
            tmp_df['公営・都市再生機構・公社の借家_ratio'] = 0

        classifire_df['公営・都市再生機構・公社の借家'] = classifire_df['公営の借家'] + classifire_df['都市再生機構']
        total_class_public_urban = classifire_df['公営・都市再生機構・公社の借家'].iloc[1:4].sum() if not classifire_df['公営・都市再生機構・公社の借家'].empty else 0
        if total_class_public_urban != 0:
            classifire_df['公営・都市再生機構・公社の借家_ratio'] = classifire_df['公営・都市再生機構・公社の借家'] / total_class_public_urban
        else:
            classifire_df['公営・都市再生機構・公社の借家_ratio'] = 0



        # 新しくカラムのリストを作成
        home_ownerships_ratio = [f'{ho}_ratio' for ho in home_ownerships_extended if f'{ho}_ratio' in tmp_df.columns]
        actual_home_ownerships = [ho for ho in home_ownerships_extended if ho in tmp_df.columns] # Ensure existence

        # 必要なカラムのリストを作成
        columns_order = ['city_code', '世帯の年間収入階級'] + actual_home_ownerships + home_ownerships_ratio
        
        # columns_orderの中でtmp_dfに含まれるカラムのみで並べ替えを行う
        tmp_df = tmp_df.loc[:, [col for col in columns_order if col in tmp_df.columns]]
        classifire_df = classifire_df.loc[:, [col for col in columns_order if col in classifire_df.columns]]

        # 市区町村単位で繰り返す場合、作成した世帯割合をcity_incomeに保存していく
        city_income = pd.concat([city_income, tmp_df], ignore_index=True)
        major_city_income = pd.concat([major_city_income, classifire_df], ignore_index=True)

        # 必要なカラムのみに絞る
        major_city_income['民営の借家_ratio'] = major_city_income['民営借家_ratio']
        need_columns = ['city_code', '世帯の年間収入階級', '持ち家_ratio', '民営の借家_ratio', '給与住宅_ratio', '公営・都市再生機構・公社の借家_ratio']
        major_city_income = major_city_income[need_columns]
        
        
        
        # 第7表_住宅の所有関係別一般世帯数の前処理
        # 秘匿地域を削除
        ownertype_df = ownertype_df[ownertype_df['市区町村コード'] == f'{target_area}']
        ownertype_processed = ownertype_df[ownertype_df['総数'] != 'X'].copy()
        ownertype_processed.replace('-', '0', inplace=True)
        ownertype_columns = ['市区町村コード', '持ち家', '民営の借家', '給与住宅', '公営・都市再生機構・公社の借家', 'KEY_CODE']
        ownertype_processed = ownertype_processed[ownertype_columns].copy()
        # カラムの厳選・型の変更
        change_columns = ['持ち家', '民営の借家', '給与住宅', '公営・都市再生機構・公社の借家']
        ownertype_processed[change_columns] = ownertype_processed[change_columns].astype(int)



        # 小地域の収入階級ごとの世帯割合の集計
        micro_income = pd.DataFrame()

        for index, micro_ownertype in ownertype_processed.iterrows():
            code = micro_ownertype['市区町村コード']
            print(f'市区町村コード：{code}の処理を実行中')
            tmp_major_city_income = major_city_income.copy()

            if tmp_major_city_income.empty:
                continue
            
            # カラムを定義するためのリストを作成
            ownership_ratios_cols = ['持ち家_ratio', '民営の借家_ratio', '給与住宅_ratio', '公営・都市再生機構・公社の借家_ratio']
            ownership_values_cols = ['持ち家', '民営の借家', '給与住宅', '公営・都市再生機構・公社の借家']

            # 建物所有形態別・収入階級別で算出した割合と小地域の所有形態別世帯数を用いて，小地域単位で所有形態別・収入階級別世帯数を算出する
            tmp_micro_income_values = tmp_major_city_income[ownership_ratios_cols].values * micro_ownertype[ownership_values_cols].values
            tmp_micro_income_calculated = pd.DataFrame(tmp_micro_income_values, columns=ownership_values_cols)

            # 小地域単位でを算出した所有形態別・収入階級別世帯数をtmp_major_city_incomeの形式になるように結合
            tmp_major_city_income = tmp_major_city_income.reset_index(drop=True)
            tmp_micro_income = tmp_major_city_income[['city_code', '世帯の年間収入階級']].join(tmp_micro_income_calculated)
            tmp_micro_income['KEY_CODE'] = micro_ownertype['KEY_CODE']

            tmp_micro_income['世帯数'] = tmp_micro_income['持ち家'] + tmp_micro_income['民営の借家'] + tmp_micro_income['給与住宅'] + tmp_micro_income['公営・都市再生機構・公社の借家']
            total_house = tmp_micro_income[tmp_micro_income['世帯の年間収入階級'] == '00_総数']['世帯数'].values[0] if not tmp_micro_income[tmp_micro_income['世帯の年間収入階級'] == '00_総数'].empty else 0

            if total_house != 0:
                tmp_micro_income['世帯数割合'] = tmp_micro_income['世帯数'] / total_house
            else:
                tmp_micro_income['世帯数割合'] = 0

            micro_income = pd.concat([micro_income, tmp_micro_income], ignore_index=True)

        micro_income = micro_income[['KEY_CODE', '世帯の年間収入階級', '世帯数', '世帯数割合']]

        income_aggregation = {
            "KEY_CODE": [],
            '00_総数': [],
            '01_500万円未満': [],
            '07_500～1000万円未満': [],
            '09_1000以上': []
        }

        for key_code in micro_income['KEY_CODE'].unique():
            subset = micro_income[micro_income['KEY_CODE'] == key_code]
            total_population = {category: 0 for category in income_aggregation if category != "KEY_CODE"}

            for index, row in subset.iterrows():
                total_population[row['世帯の年間収入階級']] += row['世帯数割合']

            income_aggregation["KEY_CODE"].append(key_code)
            for category in total_population:
                income_aggregation[category].append(total_population[category])

    # 住宅土地統計調査にデータがない場合
    else:
        city = city.drop_duplicates(subset=['city_code'], keep='first')
        pd.set_option('future.no_silent_downcasting', True)
        city['city_name'] = city['city_name'].str.replace('　', '_')
        city = city.reset_index(drop=True)

        # --- 市区町村単位の収入割合を保存するための空のデータフレームを作成 (Initialize DataFrames for City Income Ratios) ---
        city_income = pd.DataFrame()
        major_city_income = pd.DataFrame()

        # --- 年間収入階級別、住宅の所有の関係別の割合を算出 (Calculate Ratios by Income Class and Housing Ownership) ---
        for city_code in city['city_code']:
            print(f'{city_code}の処理を実行中')

            year_income_processed = year_income_df.copy()
            year_income_processed.replace('-', 0, inplace=True)
            year_income_processed['普通世帯数(世帯)'] = year_income_processed['普通世帯数(世帯)'].astype(int)
            year_income_processed = year_income_processed[year_income_processed['世帯の種類'] == '1_主世帯']
            tmp_city_income = year_income_processed[year_income_processed['地域区分－全国・都道府県・市区町村'].str.startswith(f'{city_code}')]

            tmp_df = pd.DataFrame()
            classifire_df = pd.DataFrame()

            income_classes = [
                '00_総数', '01_100万円未満', '02_100～200万円未満', '04_200～300万円未満',
                '05_300～400万円未満', '06_400～500万円未満', '07_500～700万円未満',
                '08_700～1000万円未満', '09_1000～1500万円未満', '10_1500万円以上'
            ]

            major_classes = [
                '00_総数', '01_500万円未満', '07_500～1000万円未満', '09_1000以上',
            ]

            tmp_df['世帯の年間収入階級'] = income_classes
            tmp_df['city_code'] = city_code

            classifire_df['世帯の年間収入階級'] = major_classes
            classifire_df['city_code'] = city_code

            home_ownerships = [
                '総数', '持ち家', '借家', '公営の借家', '都市再生機構', '民営借家', '給与住宅'
            ]

            for home_ownership in home_ownerships:
                filtered_data = tmp_city_income[tmp_city_income['住宅の所有の関係'].str.contains(home_ownership)]['普通世帯数(世帯)'].reset_index(drop=True)
                tmp_df[home_ownership] = filtered_data

                total_values = tmp_df[tmp_df['世帯の年間収入階級'] == '00_総数']
                total_value = total_values[home_ownership].iloc[1:10].sum() if not total_values.empty else 0

                if total_value != 0:
                    tmp_df[f'{home_ownership}_ratio'] = tmp_df[home_ownership] / total_value
                else:
                    tmp_df[f'{home_ownership}_ratio'] = 0

                total = tmp_df[home_ownership].iloc[1:10].sum() if not tmp_df[home_ownership].empty else 0
                under_500 = tmp_df[home_ownership].iloc[1:6].sum() if len(tmp_df[home_ownership]) >= 5 else 0
                from_500_to_1000 = tmp_df[home_ownership].iloc[6:8].sum() if len(tmp_df[home_ownership]) >= 8 else 0
                up_to_1000 = tmp_df[home_ownership].iloc[8:10].sum() if len(tmp_df[home_ownership]) >= 10 else 0

                major_list = [total, under_500, from_500_to_1000, up_to_1000]
                classifire_df[home_ownership] = major_list

                if total != 0:
                    classifire_df[f'{home_ownership}_ratio'] = classifire_df[home_ownership] / total
                else:
                    classifire_df[f'{home_ownership}_ratio'] = 0

            # Combine '公営の借家' and '都市再生機構'
            tmp_df['公営・都市再生機構・公社の借家'] = tmp_df['公営の借家'] + tmp_df['都市再生機構']
            home_ownerships_extended = home_ownerships + ['公営・都市再生機構・公社の借家'] # For ratio column generation

            total_public_urban = tmp_df['公営・都市再生機構・公社の借家'].iloc[1:10].sum() if not tmp_df['公営・都市再生機構・公社の借家'].empty else 0
            if total_public_urban != 0:
                tmp_df['公営・都市再生機構・公社の借家_ratio'] = tmp_df['公営・都市再生機構・公社の借家'] / total_public_urban
            else:
                tmp_df['公営・都市再生機構・公社の借家_ratio'] = 0

            classifire_df['公営・都市再生機構・公社の借家'] = classifire_df['公営の借家'] + classifire_df['都市再生機構']
            total_class_public_urban = classifire_df['公営・都市再生機構・公社の借家'].iloc[1:4].sum() if not classifire_df['公営・都市再生機構・公社の借家'].empty else 0
            if total_class_public_urban != 0:
                classifire_df['公営・都市再生機構・公社の借家_ratio'] = classifire_df['公営・都市再生機構・公社の借家'] / total_class_public_urban
            else:
                classifire_df['公営・都市再生機構・公社の借家_ratio'] = 0

            home_ownerships_ratio = [f'{ho}_ratio' for ho in home_ownerships_extended if f'{ho}_ratio' in tmp_df.columns]
            actual_home_ownerships = [ho for ho in home_ownerships_extended if ho in tmp_df.columns] # Ensure existence

            columns_order = ['city_code', '世帯の年間収入階級'] + actual_home_ownerships + home_ownerships_ratio
            
            # Filter columns to only include those that actually exist in the DataFrame
            tmp_df = tmp_df.loc[:, [col for col in columns_order if col in tmp_df.columns]]
            classifire_df = classifire_df.loc[:, [col for col in columns_order if col in classifire_df.columns]]

            city_income = pd.concat([city_income, tmp_df], ignore_index=True)
            major_city_income = pd.concat([major_city_income, classifire_df], ignore_index=True)

        # --- 必要なカラムのみに絞る (Select Necessary Columns) ---
        major_city_income['民営の借家_ratio'] = major_city_income['民営借家_ratio']
        need_columns = ['city_code', '世帯の年間収入階級', '持ち家_ratio', '民営の借家_ratio', '給与住宅_ratio', '公営・都市再生機構・公社の借家_ratio']
        major_city_income = major_city_income[need_columns]

        # --- 秘匿地域を削除 (Remove Confidential Regions) ---
        ownertype_processed = ownertype_df[ownertype_df['総数'] != 'X'].copy()
        ownertype_processed.replace('-', '0', inplace=True)
        ownertype_columns = ['市区町村コード', '持ち家', '民営の借家', '給与住宅', '公営・都市再生機構・公社の借家', 'KEY_CODE']
        ownertype_processed = ownertype_processed[ownertype_columns].copy()

        change_columns = ['持ち家', '民営の借家', '給与住宅', '公営・都市再生機構・公社の借家']
        ownertype_processed[change_columns] = ownertype_processed[change_columns].astype(int)

        # --- 小地域の収入階級ごとの世帯割合の集計 (Aggregate Household Ratios by Income Class for Small Areas) ---
        micro_income = pd.DataFrame()

        for index, micro_ownertype in ownertype_processed.iterrows():
            code = micro_ownertype['市区町村コード']
            print(f'市区町村コード：{code}の処理を実行中')
            tmp_major_city_income = major_city_income[major_city_income['city_code'] == code]

            if tmp_major_city_income.empty:
                continue

            ownership_ratios_cols = ['持ち家_ratio', '民営の借家_ratio', '給与住宅_ratio', '公営・都市再生機構・公社の借家_ratio']
            ownership_values_cols = ['持ち家', '民営の借家', '給与住宅', '公営・都市再生機構・公社の借家']

            tmp_micro_income_values = tmp_major_city_income[ownership_ratios_cols].values * micro_ownertype[ownership_values_cols].values
            tmp_micro_income_calculated = pd.DataFrame(tmp_micro_income_values, columns=ownership_values_cols)

            tmp_major_city_income = tmp_major_city_income.reset_index(drop=True)
            tmp_micro_income = tmp_major_city_income[['city_code', '世帯の年間収入階級']].join(tmp_micro_income_calculated)
            tmp_micro_income['KEY_CODE'] = micro_ownertype['KEY_CODE']

            tmp_micro_income['世帯数'] = tmp_micro_income['持ち家'] + tmp_micro_income['民営の借家'] + tmp_micro_income['給与住宅'] + tmp_micro_income['公営・都市再生機構・公社の借家']
            total_house = tmp_micro_income[tmp_micro_income['世帯の年間収入階級'] != '00_総数']['世帯数'].sum() if not tmp_micro_income[tmp_micro_income['世帯の年間収入階級'] != '00_総数'].empty else 0

            if total_house != 0:
                tmp_micro_income['世帯数割合'] = tmp_micro_income['世帯数'] / total_house
            else:
                tmp_micro_income['世帯数割合'] = 0

            micro_income = pd.concat([micro_income, tmp_micro_income], ignore_index=True)

        micro_income = micro_income[['KEY_CODE', '世帯の年間収入階級', '世帯数', '世帯数割合']]

        income_aggregation = {
            "KEY_CODE": [],
            '00_総数': [],
            '01_500万円未満': [],
            '07_500～1000万円未満': [],
            '09_1000以上': []
        }

        for key_code in micro_income['KEY_CODE'].unique():
            subset = micro_income[micro_income['KEY_CODE'] == key_code]
            total_population = {category: 0 for category in income_aggregation if category != "KEY_CODE"}

            for index, row in subset.iterrows():
                total_population[row['世帯の年間収入階級']] += row['世帯数割合']

            income_aggregation["KEY_CODE"].append(key_code)
            for category in total_population:
                income_aggregation[category].append(total_population[category])

    return pd.DataFrame(income_aggregation)