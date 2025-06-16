#基盤データとなる基盤地図データの前処理
#正解データとなるplateauデータの前処理

import pandas as pd
import geopandas as gpd
import re
import numpy as np
import os
from shapely import force_2d
from shapely.geometry import Polygon, MultiPolygon, GeometryCollection
from shapely.ops import unary_union

class DataProcessor:
    def __init__(self, basemap_area, target_basemap_area, target_plateau_area, 
                 widearea_basemap_path, government_polygon_path, 
                 plateau_path, output_dir, output_basemap_path, output_plateau_path):
        #基盤地図
        self.basemap_area = basemap_area
        self.target_basemap_area = target_basemap_area
        self.widearea_basemap_path = widearea_basemap_path
        self.government_polygon_path = government_polygon_path 
        
        #plateauデータ
        self.target_plateau_area = target_plateau_area
        self.plateau_path = plateau_path

        #output_data
        self.output_dir = output_dir
        self.output_basemap_path = output_basemap_path
        self.output_plateau_path = output_plateau_path


    def load_data(self):
        print('データの読み込み開始')
        #基盤地図データの読み込み
        self.widearea_basemap_path = self.widearea_basemap_path.format(basemap_area=self.basemap_area)
        self.widearea_basemap = gpd.read_parquet(self.widearea_basemap_path)
        #行政ポリゴンの読み込み
        self.government_polygon = gpd.read_file(self.government_polygon_path)
        #plateauデータの読み込み
        self.plateau_path = self.plateau_path.format(target_plateau_area=self.target_plateau_area)
        self.plateau = gpd.read_parquet(self.plateau_path)

        print('データの読み込み終了')

    #基盤地図データの前処理
    def extract_target_basemap_bldg(self):
        print('基盤地図データの前処理開始')
        #基盤地図を対象地域のみに絞る
        self.target_polygon = self.government_polygon[self.government_polygon['SIKUCHOSON'] == self.target_basemap_area]
        self.widearea_basemap.to_crs('EPSG:4326', inplace=True)
        self.target_polygon.to_crs('EPSG:4326', inplace=True)
        self.target_basemap = gpd.sjoin(self.widearea_basemap, self.target_polygon, predicate="within")

        #要らないカラムの削除，データの出力
        self.target_basemap = self.target_basemap[['type', 'geometry']]
        self.target_basemap.reset_index(drop=True, inplace=True)
        self.target_basemap = gpd.GeoDataFrame(self.target_basemap, geometry='geometry', crs='EPSG:4326')
        # 無効なジオメトリを高速に修正（ベクトル化）
        invalid_mask = ~self.target_basemap.is_valid
        if invalid_mask.any():
            self.target_basemap.loc[invalid_mask, 'geometry'] = self.target_basemap.loc[invalid_mask, 'geometry'].make_valid()
        print('基盤地図データの前処理終了')
    
    #plateauデータの前処理
    def cleaning_plateau(self):
        print('plateauデータの前処理開始')
        self.plateau = self.plateau[['id', 'class', 'usage', 'geometry']]
        
        # 最初に無効なジオメトリを修正 (非常に重要！)
        invalid_mask = ~self.plateau.is_valid
        if invalid_mask.any():
            print(f"無効なジオメトリが {invalid_mask.sum()} 件見つかりました。修正を試みます。")
            self.plateau.loc[invalid_mask, 'geometry'] = self.plateau.loc[invalid_mask, 'geometry'].make_valid()
            still_invalid_mask = ~self.plateau.is_valid
            if still_invalid_mask.any():
                print(f"注意: {still_invalid_mask.sum()} 件のジオメトリが make_valid() 後も無効なままです。")
                # 必要であれば、ここでこれらの無効な行を削除
                # self.plateau = self.plateau[~still_invalid_mask]

        # GeometryCollectionやMultiPolygonを単一のジオメトリに結合する処理 (unary_unionを使用)
        def combine_to_single_geometry_with_unary_union(geometry):
            if geometry is None:
                return None
            
            # GeometryCollectionの場合
            if isinstance(geometry, GeometryCollection):
                polygons_to_union = []
                for geom_part in geometry.geoms:
                    if isinstance(geom_part, Polygon):
                        polygons_to_union.append(geom_part)
                    elif isinstance(geom_part, MultiPolygon):
                        # MultiPolygonの場合は個々のポリゴンに分解して追加
                        polygons_to_union.extend(list(geom_part.geoms))
                
                if polygons_to_union:
                    # 抽出したポリゴンをunary_unionで結合
                    # unary_unionはMultiPolygonまたはPolygonを返す可能性がある
                    return unary_union(polygons_to_union)
                else:
                    return None # ポリゴンが含まれていない場合はNone
            
            # MultiPolygonの場合 (直接unary_unionを適用)
            elif isinstance(geometry, MultiPolygon):
                # MultiPolygon内の個々のポリゴンに対してunary_unionを適用
                # これにより、MultiPolygon内の重複/隣接する部分が結合され、
                # 単一のPolygonになるか、非連結のままMultiPolygonとして残る
                return unary_union(list(geometry.geoms))
            
            # Polygonの場合 (そのまま返す)
            elif isinstance(geometry, Polygon):
                return geometry
            else:
                return None # その他のジオメトリタイプは無視

        # 'geometry' 列に結合処理を適用
        self.plateau['geometry'] = self.plateau['geometry'].apply(combine_to_single_geometry_with_unary_union)

        # Noneになった行（変換できなかった、またはポリゴンが含まれていなかった行）を削除
        self.plateau = self.plateau.dropna(subset=['geometry'])
        
        # POLYGON Zを2次元にする（Z値を除去）
        self.plateau['geometry'] = self.plateau['geometry'].apply(force_2d)

        # 最後にジオメトリタイプがPolygonまたはMultiPolygonであることを確認（重要）
        # unary_unionの結果が空のGeometryCollectionになる可能性もゼロではないため
        self.plateau = self.plateau[
            self.plateau['geometry'].apply(
                lambda g: isinstance(g, (Polygon, MultiPolygon)) and not g.is_empty
            )
        ]

        self.plateau.replace({None: np.nan}, inplace=True)
        print('plateauデータの前処理終了')

    def output_file(self):
        print('データの保存開始')
        #基盤地図の出力
        self.output_dir_base = self.output_dir.format(target_plateau_area=self.target_plateau_area)
        self.output_dir_base = os.path.join(self.output_dir_base, 'basemap')
        os.makedirs(self.output_dir_base, exist_ok=True)  # ディレクトリを作成（存在してもエラーにならない）
        #出力先のパスを設定
        self.output_basemap_path = self.output_basemap_path.format(target_plateau_area=self.target_plateau_area)
        self.target_basemap.to_parquet(
                                self.output_basemap_path,
                                index=False,
                                compression="brotli",
        )

        #plateauの出力
        self.output_dir_pla = self.output_dir.format(target_plateau_area=self.target_plateau_area)
        self.output_dir_pla = os.path.join(self.output_dir_pla, 'plateau')
        os.makedirs(self.output_dir_pla, exist_ok=True)  # ディレクトリを作成（存在してもエラーにならない）
        #出力先のパスを設定
        self.output_plateau_path = self.output_plateau_path.format(target_plateau_area=self.target_plateau_area)
        self.plateau.to_parquet(
                                self.output_plateau_path,
                                index=False,
                                compression="brotli",
        )
        print('データの保存終了')

    def run(self):
        self.load_data()
        self.extract_target_basemap_bldg()
        self.cleaning_plateau()
        self.output_file()