import os
import torch
from .stability_base_node import StabilityBaseNode

class Save3DModel(StabilityBaseNode):
    """StabilityのAPIで生成した3DモデルをGLBファイルとして保存するノード"""
    
    @classmethod
    def INPUT_TYPES(s):
        # 親クラスのINPUT_TYPESを取得
        types = super().INPUT_TYPES()
        # 必要な入力を追加
        if "required" not in types:
            types["required"] = {}
            
        # required入力を追加
        types["required"].update({
            "model_bytes": ("BYTES",), # GLBファイルのバイトデータ
            "filename": ("STRING", {"default": "model.glb"}) # 保存するファイル名
        })
        
        return types
    
    RETURN_TYPES = ()  # 出力なし
    FUNCTION = "save_model"
    CATEGORY = "Stability 3D"
    
    def save_model(self, model_bytes: bytes, filename: str) -> tuple:
        """3DモデルをGLBファイルとして保存"""
        
        # ファイル名の検証
        if not filename.endswith('.glb'):
            filename += '.glb'
            
        # 出力ディレクトリの作成
        output_dir = 'output'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # ファイルパスの作成
        filepath = os.path.join(output_dir, filename)
        
        # GLBファイルとして保存
        with open(filepath, 'wb') as f:
            f.write(model_bytes)
            
        print(f"3D model saved to: {filepath}")
        return () # 出力なし