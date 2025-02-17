from server import PromptServer
import struct

class Preview3DModel:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "model_3d": ("MODEL_3D",),
            },
        }

    RETURN_TYPES = ()
    RETURN_NAMES = ()
    FUNCTION = "preview"
    OUTPUT_NODE = False # プレビュー表示のみで、次のノードには何も渡さない
    CATEGORY = "3D/preview" # カテゴリを修正

    def preview(self, model_3d):
        # Save3DModelノードで処理されるため、ここでは何もしない
        # イベントを発火させて、preview_3d_model.jsで受信する
        header = model_3d["mimetype"].encode('utf-8')
        header_size = len(header)
        model_bytes = model_3d["string"]
         # ヘッダーのサイズ + ヘッダー + 実際のデータ
        packed_data = struct.pack('<I', header_size) + header +model_bytes
        PromptServer.instance.send_sync("preview_3d_model", {"model_data": packed_data,
                                                              "filename": "filename", "model_type": "type"})
        return ()