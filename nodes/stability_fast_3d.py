import torch
from typing import Tuple
from .stability_base_node import StabilityBaseNode

class StableFast3D(StabilityBaseNode):
    """単一の2D入力画像から3Dアセットを生成するノード。
    
    このノードは、Stability AIのFast 3D生成機能を利用して、
    2D画像から高品質の3Dモデルを生成します。
    """
    
    @classmethod
    def INPUT_TYPES(s):
        # 親クラスのINPUT_TYPESを取得
        types = super().INPUT_TYPES()
        # 必要な入力を追加
        if "required" not in types:
            types["required"] = {}
        if "optional" not in types:
            types["optional"] = {}
            
        # required入力を追加
        types["required"].update({
            "image": ("IMAGE",),
        })
        
        # optional入力を追加
        types["optional"].update({
            "texture_resolution": (["512", "1024", "2048"], {"default": "1024"}),
            "foreground_ratio": ("FLOAT", {"default": 0.85, "min": 0.1, "max": 1.0, "step": 0.01}),
            "remesh": (["none", "quad", "triangle"], {"default": "none"}),
            "vertex_count": ("INT", {"default": -1, "min": -1, "max": 20000, "step": 1}),
        })
        
        return types
    
    RETURN_TYPES = ("BYTES",)  # GLBファイルをバイト列として返す
    FUNCTION = "generate"
    
    def generate(self,
                image: torch.Tensor,
                texture_resolution: str = "1024",
                foreground_ratio: float = 0.85,
                remesh: str = "none",
                vertex_count: int = -1,
                api_key: str = "") -> Tuple[bytes]:
        """3Dモデルを生成
        
        Parameters
        ----------
        image : torch.Tensor
            入力画像。[H,W,C]または[B,H,W,C]形式のテンソル
        texture_resolution : str
            テクスチャの解像度。"512", "1024", "2048"のいずれか
        foreground_ratio : float
            オブジェクトの周囲のパディング量を制御
        remesh : str
            リメッシュアルゴリズム。"none", "quad", "triangle"のいずれか
        vertex_count : int
            簡略化されたメッシュの頂点数。-1で制限なし
        api_key : str
            APIキー
            
        Returns
        -------
        Tuple[bytes]
            GLB形式の3Dモデルデータ
        """
        client = self.get_client(api_key)
        
        # 画像サイズのバリデーション
        height, width = image.shape[1:3]
        if width < 64 or height < 64:
            raise ValueError(f"画像の辺は64px以上である必要があります。現在のサイズ: {width}x{height}px")
        if width * height < 4096 or width * height > 4194304:
            raise ValueError(f"総ピクセル数は4,096px以上4,194,304px以下である必要があります。現在のピクセル数: {width * height}px")
            
        # リクエストデータの準備
        data = {
            "texture_resolution": texture_resolution,
            "foreground_ratio": foreground_ratio,
        }
        
        if remesh != "none":
            data["remesh"] = remesh
            
        if vertex_count != -1:
            data["vertex_count"] = vertex_count
            
        # ファイルの準備
        files = {
            "image": ("image.png", client.image_to_bytes(image))
        }
        
        # APIリクエストを実行
        response = client._make_request(
            "POST",
            "/v2beta/3d/stable-fast-3d",
            data=data,
            files=files
        )
        
        # GLBデータを返す
        return (response.content,)