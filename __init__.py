# ノードのインポート
from .nodes.stability_image_ultra import StabilityImageUltra  # Stable Image Ultra
from .nodes.stability_image_core import StabilityImageCore    # Stable Image Core
from .nodes.stability_image_sd3 import StabilityImageSD3      # Stable Diffusion 3.0 & 3.5
from .nodes.stability_upscale_fast import StabilityUpscaleFast  # Fast Upscaler
from .nodes.stability_upscale_conservative import StabilityUpscaleConservative  # Conservative Upscaler
from .nodes.stability_upscale_creative import StabilityUpscaleCreative  # Creative Upscaler
from .nodes.stability_edit import StabilityEdit  # 画像編集機能
from .nodes.stability_image_to_video import StabilityImageToVideo  # 画像から動画生成
from .nodes.stability_control_sketch import StabilityControlSketch  # スケッチベースの生成制御
from .nodes.stability_control_structure import StabilityControlStructure  # 構造ベースの生成制御
from .nodes.stability_control_style import StabilityControlStyle  # スタイルベースの生成制御
from .nodes.stability_fast_3d import StableFast3D  # Fast 3D生成
from .nodes.stability_point_aware_3d import StablePointAware3D  # Point Aware 3D生成
from .nodes.save_3d_model import Save3DModel  # 3Dモデル保存

# ノードクラスとComfyUI上での表示名のマッピング
NODE_CLASS_MAPPINGS = {
    "StabilityImageUltra": StabilityImageUltra,
    "StabilityImageCore": StabilityImageCore,
    "StabilityImageSD3": StabilityImageSD3,
    "StabilityUpscaleFast": StabilityUpscaleFast,
    "StabilityUpscaleConservative": StabilityUpscaleConservative,
    "StabilityUpscaleCreative": StabilityUpscaleCreative,
    "StabilityEdit": StabilityEdit,
    "StabilityImageToVideo": StabilityImageToVideo,
    "StabilityControlSketch": StabilityControlSketch,
    "StabilityControlStructure": StabilityControlStructure,
    "StabilityControlStyle": StabilityControlStyle,
    "StableFast3D": StableFast3D,
    "StablePointAware3D": StablePointAware3D,
    "Save3DModel": Save3DModel
}

# ComfyUI上でのノードの表示名設定
NODE_DISPLAY_NAME_MAPPINGS = {
    "StabilityImageUltra": "Stability Ultra Image Generation",  # フォトリアリスティックな高品質画像生成
    "StabilityImageCore": "Stability Core Image Generation",    # 高速な標準画像生成
    "StabilityImageSD3": "Stability SD3 Image Generation",     # SD3/3.5ベースの画像生成
    "StabilityUpscaleFast": "Stability Fast Upscaler",        # 高速な画像アップスケール
    "StabilityUpscaleConservative": "Stability Conservative Upscaler",  # 保守的な画像アップスケール
    "StabilityUpscaleCreative": "Stability Creative Upscaler",  # クリエイティブな画像アップスケール
    "StabilityEdit": "Stability Image Editor",                 # 画像編集ツール
    "StabilityImageToVideo": "Stability Image to Video",       # 画像から動画への変換
    "StabilityControlSketch": "Stability Sketch Control",      # スケッチベースの生成制御
    "StabilityControlStructure": "Stability Structure Control", # 構造ベースの生成制御
    "StabilityControlStyle": "Stability Style Control",        # スタイルベースの生成制御
    "StableFast3D": "Stability Fast 3D Generation",           # 高速3Dモデル生成
    "StablePointAware3D": "Stability Point Aware 3D",         # 高品質3Dモデル生成
    "Save3DModel": "Save 3D Model"                            # 3Dモデル保存
}

# ComfyUIに必要な情報のエクスポート
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']