# nodes/save_3d_model.py
import os
from typing import Tuple
from server import PromptServer
import io  # 不要なので削除
import base64  # 不要なので削除

class Save3DModel:
    """3DモデルをGLBファイルとして保存し、プレビューするノード"""

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
    OUTPUT_NODE = True

    def save_model(self, model_bytes: bytes, filename: str) -> Tuple:
        """3DモデルをGLBファイルとして保存"""

        print(f"Save3DModel: save_model called. filename: {filename}") # DEBUG 1

        # ファイル名の検証
        if not filename.endswith('.glb'):
            filename += '.glb'
        print(f"Save3DModel: Filename after validation: {filename}") # DEBUG 2

        # 出力ディレクトリの作成
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'output')
        print(f"Save3DModel: Output directory: {output_dir}") # DEBUG 3

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"Save3DModel: Created output directory.") # DEBUG 4

        # ファイルパスの作成
        filepath = os.path.join(output_dir, filename)
        print(f"Save3DModel: Full filepath: {filepath}") # DEBUG 5

        # GLBファイルとして保存
        try:
            with open(filepath, 'wb') as f:
                f.write(model_bytes)
            print(f"Save3DModel: 3D model saved to: {filepath}") # DEBUG 6
        except Exception as e:
            print(f"Save3DModel: Error saving file: {e}") # DEBUG 7


        # バイトデータを直接送信 (latin-1でエンコード)
        try:
            model_data_str = model_bytes.decode("latin-1")
            print(f"Save3DModel: model_bytes length: {len(model_bytes)}") # DEBUG 8
            print(f"Save3DModel: model_data_str length: {len(model_data_str)}")  # DEBUG 9

            PromptServer.instance.send_sync("preview_3d_model", {
                "model_data": model_data_str,
                "filename": filename
            })
            print(f"Save3DModel: Sent preview_3d_model message to client.") # DEBUG 10
        except Exception as e:
            print(f"Save3DModel: Error sending to client: {e}") # DEBUG 11

        return ()