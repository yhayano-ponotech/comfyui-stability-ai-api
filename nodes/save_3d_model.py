# nodes/save_3d_model.py
import os
from typing import Tuple

class Save3DModel:
    """3DモデルをGLBファイルとして保存するノード"""

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "model_3d": ("MODEL_3D",), # GLBファイルのバイトデータ
                "filename": ("STRING", {"default": "model"}),
                "model_type": (["GLB", "OBJ", "PLY"], {"default": "GLB"}),
            },
             "hidden": {"prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO"}, #workflowの情報を保持
        }

    RETURN_TYPES = ()
    RETURN_NAMES = ()
    FUNCTION = "save_model"
    OUTPUT_NODE = True
    CATEGORY = "Stability AI"

    def save_model(self, model_3d, filename: str, model_type: str, prompt=None, extra_pnginfo=None) -> Tuple:
        """3DモデルをGLBファイルとして保存"""

        model_bytes = model_3d["string"] # バイトデータを取得

        # 出力ディレクトリの作成
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "output")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # ファイルパスの作成
        filepath = os.path.join(output_dir, filename + "." + model_type.lower())

        # GLBファイルとして保存
        with open(filepath, 'wb') as f:
            f.write(model_bytes)

        print(f"[comfyui-stability-ai-api] Saved: {filepath}")

        return ()