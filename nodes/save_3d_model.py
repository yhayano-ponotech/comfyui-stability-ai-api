import os
from typing import Tuple

class Save3DModel:
    """3DモデルをGLBファイルとして保存するノード"""
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "model_bytes": ("BYTES",), # GLBファイルのバイトデータ
                "filename": ("STRING", {"default": "model.glb"}) # 保存するファイル名
            }
        }
    
    RETURN_TYPES = ()  # 出力なし
    RETURN_NAMES = ()  # 出力名なし
    FUNCTION = "save_model"
    CATEGORY = "Stability AI"
    
    def save_model(self, model_bytes: bytes, filename: str) -> Tuple:
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
        return ()  # 空のタプルを返す