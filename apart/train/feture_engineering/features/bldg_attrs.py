#建物属性（面積・周囲長・矩形度）を算出するモジュール

import pandas as pd
import geopandas as gpd
import numpy as np
from shapely import GeometryCollection, LineString, MultiPoint, Point, Polygon
from shapely import minimum_bounding_circle
import math
import shapely.affinity # shapely.affinity.scale を使用するため
from shapely.ops import triangulate # triangulate をインポート


# scaling_polygon 関数 (提供されたものそのまま)
def scaling_polygon(polygon):
    if isinstance(polygon, Polygon) and polygon.area != 0:
        scale_factor = math.sqrt(1.0 / polygon.area) # 面積1にスケーリングするための因子
        scaled_polygon = shapely.affinity.scale(
            polygon, xfact=scale_factor, yfact=scale_factor, origin=(0, 0)) # afine変換でスケーリング
        return scaled_polygon
    else:
        raise ValueError("invalid polygon @[scaling_polygon]")



# calculate_rectangularity 関数 (提供されたものそのまま)
def calculate_rectangularity(geometry):
    # '''
    # 矩形度を計算する関数
    # '''
    if isinstance(geometry, Polygon):
        area = geometry.area
        # 最小外接矩形を計算 
        min_rect = geometry.minimum_rotated_rectangle
        min_rect_area = min_rect.area

        if min_rect_area != 0:
            return area / min_rect_area
        else:
            # 面積がゼロの矩形は計算できないか、非常に細長いジオメトリの可能性があります。
            # この場合、エラーを発生させるか、特定の値を返すかを検討してください。
            # 例: 極端に細長い場合は0として扱う、またはNaNとする
            # raise ValueError("Invalid polygon @[calculate_rectangularity]: input must be a non-zero area polygon")
            # 非常に小さい面積のmin_rect_areaの場合、矩形度が非常に大きくなるため注意が必要です。
            # ここでは0を返すようにしていますが、NaNや特定のデフォルト値を検討することもできます。
            return 0.0 # または np.nan, あるいは何らかの例外処理
    else:
        raise ValueError("Invalid polygon @[calculate_rectangularity]: input must be a Polygon")


# ポリゴンの凸度を計算する関数
def calculate_convexity(polygon):
    if not isinstance(polygon, Polygon) or polygon.is_empty:
        return np.nan
    # 対象図形の周囲長を取得
    perimeter = polygon.length  
    # 周囲長が0の場合は計算不能
    if perimeter == 0:
        return np.nan
    # 対象図形の凸包を計算し、その周囲長を取得
    convex_hull_perimeter = polygon.convex_hull.length
    # 凸度を計算
    convexity = convex_hull_perimeter / perimeter
    
    return convexity


# ポリゴンの重心周りの慣性モーメントを計算する関数
def calculate_moment_of_inertia(polygon):
    # """
    # ポリゴンの重心周りの慣性モーメント（断面二次極モーメント）を計算する。
    # I = Σ(a_i * d_i^2)
    # """
    if not isinstance(polygon, Polygon) or polygon.is_empty or polygon.area == 0:
        return np.nan

    centroid = polygon.centroid
    triangles = triangulate(polygon)
    moment_of_inertia = 0.0

    for tri in triangles:
        if tri.is_empty:
            continue
        a_i = tri.area
        d_i = centroid.distance(tri.centroid)
        moment_of_inertia += a_i * (d_i ** 2)

    return moment_of_inertia


#  3つの点がなす角度を計算する関数
def calculate_angle(p1, p2, p3):
    """3つの点がなす角度を p2 を中心として計算する (0-360度)"""
    v1 = (p1[0] - p2[0], p1[1] - p2[1])
    v2 = (p3[0] - p2[0], p3[1] - p2[1])
    angle1 = math.atan2(v1[1], v1[0])
    angle2 = math.atan2(v2[1], v2[0])
    angle_rad = angle2 - angle1
    angle_deg = math.degrees(angle_rad)
    if angle_deg < 0:
        angle_deg += 360
    return angle_deg


#  ポリゴンの「角」の数を数える関数
def count_corners(geometry):
    """定義に従ってポリゴンの「角」の数を数える"""
    if not isinstance(geometry, Polygon) or geometry.is_empty:
        return 0
    
    coords = list(geometry.exterior.coords)[:-1]
    if len(coords) < 3:
        return 0
        
    corner_count = 0
    num_coords = len(coords)
    
    for i in range(num_coords):
        p1 = coords[i - 1]
        p2 = coords[i]
        p3 = coords[(i + 1) % num_coords]
        angle = calculate_angle(p1, p2, p3)
        if angle <= 170.0 or angle >= 190.0:
            corner_count += 1
            
    return corner_count


#  最小外接円に基づく特徴量を計算する関数
def calculate_circle_based_features(geometry):
    """
    最小外接円を計算し、「異方性指数」と「最長軸長」を辞書で返す。
    （正しい `minimum_bounding_circle` 関数の使い方に修正済み）
    """
    if not isinstance(geometry, (Polygon, Point)) or geometry.is_empty:
        return {'anisotropy': np.nan, 'longest_axis': np.nan}
    if isinstance(geometry, Point): # 点の場合は特別扱い
        return {'anisotropy': np.nan, 'longest_axis': 0.0}
    if geometry.area == 0:
        return {'anisotropy': np.nan, 'longest_axis': np.nan}

    # --- 修正点2: メソッド形式ではなく、関数として呼び出す ---
    # 誤: min_circle = geometry.minimum_bounding_circle
    # 正:
    min_circle = minimum_bounding_circle(geometry)
    
    # 最小外接円が点になる場合（入力が点の場合など）の処理
    if not isinstance(min_circle, Polygon):
        return {'anisotropy': np.nan, 'longest_axis': 0.0}

    area_f = geometry.area
    area_c = min_circle.area
    bounds = min_circle.bounds
    diameter_lambda = bounds[2] - bounds[0]

    if area_c == 0:
        anisotropy = np.nan
    else:
        anisotropy = area_f / area_c
    
    longest_axis = diameter_lambda
    
    return {'anisotropy': anisotropy, 'longest_axis': longest_axis}

# ポリゴンの伸長度（アスペクト比）を計算する関数
def calculate_elongation(geometry):
    """
    ポリゴンの伸長度（アスペクト比）を計算する。
    伸長度 = (最小外接矩形の短い辺) / (長い辺)
    """
    if not isinstance(geometry, Polygon) or geometry.is_empty:
        return np.nan
        
    # 1. 最小外接矩形を計算 (回転を許す)
    #    .minimum_rotated_rectangle は長方形のPolygonオブジェクトを返す
    min_rect = geometry.minimum_rotated_rectangle
    
    # 2. 矩形の頂点座標を取得
    coords = list(min_rect.exterior.coords)
    
    # 3. 辺の長さを計算 (連続する2つの頂点間の距離)
    #    Pointオブジェクトを使って2点間の距離を正確に計算
    side1 = Point(coords[0]).distance(Point(coords[1]))
    side2 = Point(coords[1]).distance(Point(coords[2]))

    # 4. 伸長度を計算
    if side1 == 0 or side2 == 0:
        return np.nan # 辺の長さが0の場合は計算不能
    
    elongation = min(side1, side2) / max(side1, side2)
    
    return elongation


# 方位角の計算
def calculate_azimuth(p1, p2):
    """
    点p1から点p2への方位角（真北を0度とする時計回りの角度）を計算する。
    """
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    
    # atan2(dx, dy) は、Y軸(北)を基準とした角度を計算する
    azimuth_rad = math.atan2(dx, dy)
    azimuth_deg = math.degrees(azimuth_rad)
    
    # 角度を0-360の範囲に正規化
    if azimuth_deg < 0:
        azimuth_deg += 360
        
    return azimuth_deg

def calculate_orientation(geometry):
    """
    ポリゴンの方位（0-45度）を計算する。
    """
    if not isinstance(geometry, Polygon) or geometry.is_empty:
        return np.nan
        
    # 1. 最小外接矩形を計算
    min_rect = geometry.minimum_rotated_rectangle
    
    # 2. 矩形の頂点座標を取得
    coords = list(min_rect.exterior.coords)
    
    # 3. 辺の長さを計算
    side1_len = Point(coords[0]).distance(Point(coords[1]))
    side2_len = Point(coords[1]).distance(Point(coords[2]))

    # 4. 長い方の辺の2点を特定
    if side1_len >= side2_len:
        p_start, p_end = coords[0], coords[1]
    else:
        p_start, p_end = coords[1], coords[2]
        
    # 5. 長い方の辺の方位角を計算
    azimuth = calculate_azimuth(p_start, p_end)
    
    # 6. 方位角を0-45度の範囲に変換
    orientation = abs(((azimuth + 45) % 90) - 45)
    
    return orientation




# ------------- ここから建物属性を計算する関数 -------------#




# 建物属性を計算する関数
def bldg_attrs(gdf, crs):
    # 面積の計算
    gdf.to_crs(crs, inplace=True)
    gdf['area'] = gdf.area
    gdf = gdf[gdf['area'] >= 25] # 面積が25平方メートル以上のポリゴンのみを残す

    #建物の外周を算出
    # 各ポリゴンの外周の長さを計算し、新しい列に追加
    gdf['perimeter'] = gdf['geometry'].length

    # 矩形度の計算
    for index, row in gdf.iterrows():
        geom = row['geometry']
        try:
            if isinstance(geom, Polygon) and geom.area > 0:
                gdf.at[index, 'rectangularity'] = calculate_rectangularity(geom)
            else:
                # Polygonではない、または面積がゼロのジオメトリの場合
                gdf.at[index, 'rectangularity'] = None # または np.nan
        except ValueError as e:
            print(f"Error calculating rectangularity for row {index}: {e}. Setting to None.")
            gdf.at[index, 'rectangularity'] = None # 計算エラーの場合もNone

        #  凸度の計算
        try:
            gdf.at[index, 'convexity'] = calculate_convexity(geom)
        except Exception as e:
            print(f"Error calculating convexity for row {index}: {e}.")

        # 慣性モーメントの計算
        try:
            gdf.at[index, 'moment_of_inertia'] = calculate_moment_of_inertia(geom)
        except Exception as e:
            # 予期せぬエラーをキャッチ
            print(f"Error calculating moment of inertia for row {index}: {e}. Setting to NaN.")
        
        # 角の数を数える
        try:
            gdf.at[index, 'num_corners'] = count_corners(geom)
        except Exception as e:
            print(f"Error calculating num_corners for row {index}: {e}.")

        # 円に基づく特徴量の計算(異方性指数と最長軸長)
        try:
            # 2つの特徴量を一度に計算
            circle_features = calculate_circle_based_features(geom)
            # 辞書の結果をそれぞれの列に格納
            gdf.at[index, 'anisotropy'] = circle_features['anisotropy'] # 異方性指数
            gdf.at[index, 'longest_axis'] = circle_features['longest_axis'] # 最長軸長
        except Exception as e:
            print(f"Error calculating circle-based features for row {index}: {e}.")
            # エラーの場合はNaNのままにする
            gdf.at[index, 'anisotropy'] = np.nan
            gdf.at[index, 'longest_axis'] = np.nan
        
        # 伸長度(アスペクト比）の計算
        try:
            gdf.at[index, 'elongation'] = calculate_elongation(geom)
        except Exception as e:
            print(f"Error calculating elongation for row {index}: {e}.")
            gdf.at[index, 'elongation'] = np.nan
        
        # 建物の向きの計算
        try:
            gdf.at[index, 'orientation'] = calculate_orientation(geom)
        except Exception as e:
            print(f"Error calculating orientation for row {index}: {e}.")
            gdf.at[index, 'orientation'] = np.nan

    return gdf