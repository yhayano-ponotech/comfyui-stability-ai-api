# nodes/preview_3d_model.py
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
    OUTPUT_NODE = False #プレビュー表示のみで、次のノードには何も渡さない
    CATEGORY = "3D/preview" # カテゴリを修正

    def preview(self, model_3d):
        # Save3DModelノードで処理されるため、ここでは何もしない
        return ()