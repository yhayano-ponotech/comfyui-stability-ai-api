import torch
from typing import List, Tuple, Dict, Any, Optional
from .api_client import StabilityAPIClient
import json

class StabilityBaseNode:
    """StabilityAI APIノードの基底クラス"""
    CATEGORY = "Stability AI"

    def __init__(self):
        self.client = StabilityAPIClient()

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "prompt": ("STRING", {"multiline": True}),
            },
            "optional": {
                "negative_prompt": ("STRING", {"multiline": True, "default": ""}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 4294967295}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "generate"
    
    def generate(self,
                prompt: str,
                aspect_ratio: str,
                negative_prompt: str = "",
                seed: int = 0,
                style_preset: str = "none") -> Tuple[torch.Tensor]:
        """画像を生成"""

        # リクエストデータの準備
        data = {
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "seed": seed,
            "output_format": "png"
        }
        
        if negative_prompt:
            data["negative_prompt"] = negative_prompt
            
        if style_preset != "none":
            data["style_preset"] = style_preset

        # APIリクエストを実行
        headers = {"Accept": "image/*"}
        response = self.client._make_request(
            "POST", 
            "/v2beta/stable-image/generate/core", 
            data=data,
            headers=headers
        )
        
        # レスポンスを画像テンソルに変換
        image_tensor = self.client.bytes_to_tensor(response.content)
        return (image_tensor,)

class StabilityImageToVideo(StabilityBaseNode):
    """Stability Image to Videoノード"""
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
            },
            "optional": {
                "seed": ("INT", {"default": 0, "min": 0, "max": 4294967295}),
                "cfg_scale": ("FLOAT", {"default": 1.8, "min": 0.0, "max": 10.0, "step": 0.1}),
                "motion_bucket_id": ("INT", {"default": 127, "min": 1, "max": 255}),
            }
        }

    RETURN_TYPES = ("BYTES",)
    FUNCTION = "generate"
    
    def generate(self,
                image: torch.Tensor,
                seed: int = 0,
                cfg_scale: float = 1.8,
                motion_bucket_id: int = 127) -> Tuple[bytes]:
        """画像からビデオを生成"""
        
        # リクエストデータの準備
        data = {
            "seed": seed,
            "cfg_scale": cfg_scale,
            "motion_bucket_id": motion_bucket_id
        }

        files = {
            "image": ("image.png", self.client.image_to_bytes(image))
        }

        # 生成を開始
        response = self.client._make_request(
            "POST",
            "/v2beta/image-to-video",
            data=data,
            files=files
        )
        
        generation_id = response.json()["id"]
        
        # 生成完了まで待機
        while True:
            response = self.client._make_request(
                "GET",
                f"/v2beta/image-to-video/result/{generation_id}",
                headers={"Accept": "video/*"}
            )
            
            if response.status_code == 200:
                # 生成完了
                return (response.content,)

class StabilityUpscaleFast(StabilityBaseNode):
    """Stability Fast Upscalerノード"""
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
            },
            "optional": {
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "upscale"
    
    def upscale(self,
                image: torch.Tensor) -> Tuple[torch.Tensor]:
        """画像をアップスケール"""
        
        # リクエストデータの準備
        files = {"image": ("image.png", self.client.image_to_bytes(image))}

        # APIリクエストを実行
        headers = {"Accept": "image/*"}
        response = self.client._make_request(
            "POST", 
            "/v2beta/stable-image/upscale/fast", 
            files=files,
            headers=headers
        )
        
        # レスポンスを画像テンソルに変換
        image_tensor = self.client.bytes_to_tensor(response.content)
        return (image_tensor,)

class StabilityUpscaleConservative(StabilityBaseNode):
    """Stability Conservative Upscalerノード"""
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "prompt": ("STRING", {"multiline": True}),
            },
            "optional": {
                "negative_prompt": ("STRING", {"multiline": True, "default": ""}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 4294967295}),
                "creativity": ("FLOAT", {"default": 0.35, "min": 0.2, "max": 0.5, "step": 0.01}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "upscale"
    
    def upscale(self,
                image: torch.Tensor,
                prompt: str,
                negative_prompt: str = "",
                seed: int = 0,
                creativity: float = 0.35) -> Tuple[torch.Tensor]:
        """画像をアップスケール"""
        
        # リクエストデータの準備
        data = {
            "prompt": prompt,
            "seed": seed,
            "creativity": creativity,
            "output_format": "png"
        }
        
        if negative_prompt:
            data["negative_prompt"] = negative_prompt

        files = {"image": ("image.png", self.client.image_to_bytes(image))}

        # APIリクエストを実行
        headers = {"Accept": "image/*"}
        response = self.client._make_request(
            "POST", 
            "/v2beta/stable-image/upscale/conservative", 
            data=data,
            files=files,
            headers=headers
        )
        
        # レスポンスを画像テンソルに変換
        image_tensor = self.client.bytes_to_tensor(response.content)
        return (image_tensor,)

class StabilityUpscaleCreative(StabilityBaseNode):
    """Stability Creative Upscalerノード"""
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "prompt": ("STRING", {"multiline": True}),
            },
            "optional": {
                "negative_prompt": ("STRING", {"multiline": True, "default": ""}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 4294967295}),
                "creativity": ("FLOAT", {"default": 0.3, "min": 0.1, "max": 0.5, "step": 0.01}),
                "style_preset": (["none", "3d-model", "analog-film", "anime", "cinematic", "comic-book", "digital-art", 
                                "enhance", "fantasy-art", "isometric", "line-art", "low-poly", "modeling-compound", 
                                "neon-punk", "origami", "photographic", "pixel-art", "tile-texture"],),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "upscale"
    
    def upscale(self,
                image: torch.Tensor,
                prompt: str,
                negative_prompt: str = "",
                seed: int = 0,
                creativity: float = 0.3,
                style_preset: str = "none") -> Tuple[torch.Tensor]:
        """画像をアップスケール"""
        
        # リクエストデータの準備
        data = {
            "prompt": prompt,
            "seed": seed,
            "creativity": creativity,
            "output_format": "png"
        }
        
        if negative_prompt:
            data["negative_prompt"] = negative_prompt
            
        if style_preset != "none":
            data["style_preset"] = style_preset

        files = {"image": ("image.png", self.client.image_to_bytes(image))}

        # APIリクエストを実行
        headers = {"Accept": "image/*"}
        response = self.client._make_request(
            "POST", 
            "/v2beta/stable-image/upscale/creative", 
            data=data,
            files=files,
            headers=headers
        )
        
        # レスポンスを画像テンソルに変換
        image_tensor = self.client.bytes_to_tensor(response.content)
        return (image_tensor,)

class StabilityEdit(StabilityBaseNode):
    """Stability Image Editorノード"""
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "edit_type": (["erase", "inpaint", "outpaint", "search-and-replace", "search-and-recolor", "remove-background"],),
                "prompt": ("STRING", {"multiline": True}),
            },
            "optional": {
                "negative_prompt": ("STRING", {"multiline": True, "default": ""}),
                "mask": ("MASK",),
                "grow_mask": ("INT", {"default": 5, "min": 0, "max": 100}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 4294967295}),
                "style_preset": (["none", "3d-model", "analog-film", "anime", "cinematic", "comic-book", "digital-art", 
                                "enhance", "fantasy-art", "isometric", "line-art", "low-poly", "modeling-compound", 
                                "neon-punk", "origami", "photographic", "pixel-art", "tile-texture"],),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "edit"
    
    def edit(self,
            image: torch.Tensor,
            edit_type: str,
            prompt: str,
            negative_prompt: str = "",
            mask: Optional[torch.Tensor] = None,
            grow_mask: int = 5,
            seed: int = 0,
            style_preset: str = "none") -> Tuple[torch.Tensor]:
        """画像を編集"""
        
        # リクエストデータの準備
        data = {
            "prompt": prompt,
            "seed": seed,
            "output_format": "png"
        }
        
        if negative_prompt:
            data["negative_prompt"] = negative_prompt
            
        if style_preset != "none":
            data["style_preset"] = style_preset
            
        if grow_mask != 5:
            data["grow_mask"] = grow_mask

        files = {
            "image": ("image.png", self.client.image_to_bytes(image))
        }
        
        if mask is not None:
            files["mask"] = ("mask.png", self.client.image_to_bytes(mask))

        # APIリクエストを実行
        headers = {"Accept": "image/*"}
        response = self.client._make_request(
            "POST", 
            f"/v2beta/stable-image/edit/{edit_type}", 
            data=data,
            files=files,
            headers=headers
        )
        
        # レスポンスを画像テンソルに変換
        image_tensor = self.client.bytes_to_tensor(response.content)
        return (image_tensor,)

class StabilityImageUltra(StabilityBaseNode):
    """Stability Ultra Image Generationノード"""
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "prompt": ("STRING", {"multiline": True}),
                "aspect_ratio": (["1:1", "16:9", "21:9", "2:3", "3:2", "4:5", "5:4", "9:16", "9:21"], {"default": "1:1"}),
            },
            "optional": {
                "negative_prompt": ("STRING", {"multiline": True, "default": ""}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 4294967295}),
                "style_preset": (["none", "3d-model", "analog-film", "anime", "cinematic", "comic-book", "digital-art", 
                                "enhance", "fantasy-art", "isometric", "line-art", "low-poly", "modeling-compound", 
                                "neon-punk", "origami", "photographic", "pixel-art", "tile-texture"], {"default": "none"}),
                "output_format": (["png", "jpeg", "webp"], {"default": "png"}),
                "image": ("IMAGE",),  # 入力画像（オプション）
                "strength": ("FLOAT", {"default": 0.7, "min": 0.0, "max": 1.0, "step": 0.01}),  # 画像の影響度
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "generate"
    
    def generate(self, 
                prompt: str,
                aspect_ratio: str,
                negative_prompt: str = "",
                seed: int = 0,
                style_preset: str = "none",
                output_format: str = "png",
                image: Optional[torch.Tensor] = None,
                strength: float = 0.7) -> Tuple[torch.Tensor]:
        """画像を生成
        
        Parameters
        ----------
        image : Optional[torch.Tensor]
            入力画像。以下の制限があります：
            - 幅: 64px以上16,384px以下
            - 高さ: 64px以上16,384px以下
            - 総ピクセル数: 4,096px以上
        strength : float
            画像の影響度（0.0〜1.0）。imageパラメータが指定されている場合は必須。
            0.0: 入力画像とまったく同じ
            1.0: 入力画像の影響なし
        
        Returns
        --------
        Tuple[torch.Tensor]
            生成された画像テンソル。形式は [B,H,W,C]
            B: バッチサイズ (1)
            H: 高さ
            W: 幅
            C: チャンネル数 (3: RGB)
            値の範囲は0-1のfloat32型
        """
        
        # 入力画像のバリデーション
        if image is not None:
            # 画像サイズの取得
            height, width = image.shape[1:3]
            
            # サイズ制限のチェック
            if width < 64 or width > 16384:
                raise ValueError(f"画像の幅は64px以上16,384px以下である必要があります。現在の幅: {width}px")
            if height < 64 or height > 16384:
                raise ValueError(f"画像の高さは64px以上16,384px以下である必要があります。現在の高さ: {height}px")
            if width * height < 4096:
                raise ValueError(f"総ピクセル数は4,096px以上である必要があります。現在のピクセル数: {width * height}px")
            
            # strengthパラメータのチェック
            if strength is None:
                raise ValueError("strengthパラメータは画像が指定されている場合は必須です")
        
        # リクエストデータの準備
        data = {
            "prompt": prompt,
            "seed": seed,
            "output_format": output_format
        }
        
        if negative_prompt:
            data["negative_prompt"] = negative_prompt
            
        if style_preset != "none":
            data["style_preset"] = style_preset

        # 入力画像がある場合（image-to-image）
        files = {}
        if image is not None:
            data["strength"] = strength
            files["image"] = ("image.png", self.client.image_to_bytes(image))
        else:
            # text-to-imageの場合はアスペクト比を指定
            data["aspect_ratio"] = aspect_ratio

        # APIリクエストを実行（画像データを直接受け取る）
        headers = {
            "Accept": "image/*"  # 画像データを直接受け取る
        }
        
        # multipart/form-dataとしてデータを送信
        for key, value in data.items():
            files[key] = (None, str(value))
            
        # デバッグ情報を出力
        print("Request data:", files)
        print("Request headers:", headers)
            
        response = self.client._make_request(
            "POST", 
            "/v2beta/stable-image/generate/ultra", 
            files=files,
            headers=headers
        )
        
        # レスポンスのContent-Typeを確認
        print("Response Content-Type:", response.headers.get('content-type'))
        print("Response status code:", response.status_code)
        
        # Content-Typeに基づいて処理を分岐
        content_type = response.headers.get('content-type', '')
        if 'application/json' in content_type:
            # JSONレスポンスの場合
            response_data = response.json()
            print("JSON Response:", response_data)
            if 'artifacts' in response_data and response_data['artifacts']:
                image_data = response_data['artifacts'][0].get('base64')
                if image_data:
                    import base64
                    image_bytes = base64.b64decode(image_data)
                else:
                    raise Exception("No base64 image data in response")
            else:
                raise Exception("No artifacts in response")
        elif 'image/' in content_type:
            # 画像データの場合
            image_bytes = response.content
        else:
            raise Exception(f"Unexpected content type: {content_type}")
        
        # バイト列を画像テンソルに変換
        image_tensor = self.client.bytes_to_tensor(image_bytes)
        return (image_tensor,)

class StabilityImageCore(StabilityBaseNode):
    """Stability Core Image Generationノード"""
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "prompt": ("STRING", {"default": "", "multiline": True}),
                "aspect_ratio": (["1:1", "16:9", "21:9", "2:3", "3:2", "4:5", "5:4", "9:16", "9:21"], {"default": "1:1"}),
                "negative_prompt": ("STRING", {"default": "", "multiline": True}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "style_preset": (["none", "3d-model", "analog-film", "anime", "cinematic", "comic-book", "digital-art", 
                                "enhance", "fantasy-art", "isometric", "line-art", "low-poly", "modeling-compound", 
                                "neon-punk", "origami", "photographic", "pixel-art", "tile-texture"], {"default": "none"}),
                "output_format": (["png", "jpeg", "webp"], {"default": "png"}),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "generate"
    
    def generate(self, 
                prompt: str,
                aspect_ratio: str,
                negative_prompt: str = "",
                seed: int = 0,
                style_preset: str = "none",
                output_format: str = "png") -> Tuple[torch.Tensor]:
        """画像を生成
        
        Returns
        --------
        Tuple[torch.Tensor]
            生成された画像テンソル。形式は [B,H,W,C]
            B: バッチサイズ (1)
            H: 高さ
            W: 幅
            C: チャンネル数 (3: RGB)
            値の範囲は0-1のfloat32型
        """
        
        # リクエストデータの準備
        data = {
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "seed": seed,
            "output_format": output_format
        }
        
        if negative_prompt:
            data["negative_prompt"] = negative_prompt
            
        if style_preset != "none":
            data["style_preset"] = style_preset

        # APIリクエストを実行（画像データを直接受け取る）
        headers = {
            "Accept": "image/*"  # 画像データを直接受け取る
        }
        
        # multipart/form-dataとしてデータを送信
        files = {}
        for key, value in data.items():
            files[key] = (None, str(value))
            
        # デバッグ情報を出力
        print("Request data:", files)
        print("Request headers:", headers)
            
        response = self.client._make_request(
            "POST", 
            "/v2beta/stable-image/generate/core", 
            files=files,
            headers=headers
        )
        
        # レスポンスのContent-Typeを確認
        print("Response Content-Type:", response.headers.get('content-type'))
        print("Response status code:", response.status_code)
        
        # Content-Typeに基づいて処理を分岐
        content_type = response.headers.get('content-type', '')
        if 'application/json' in content_type:
            # JSONレスポンスの場合
            response_data = response.json()
            print("JSON Response:", response_data)
            if 'artifacts' in response_data and response_data['artifacts']:
                image_data = response_data['artifacts'][0].get('base64')
                if image_data:
                    import base64
                    image_bytes = base64.b64decode(image_data)
                else:
                    raise Exception("No base64 image data in response")
            else:
                raise Exception("No artifacts in response")
        elif 'image/' in content_type:
            # 画像データの場合
            image_bytes = response.content
        else:
            raise Exception(f"Unexpected content type: {content_type}")
        
        # バイト列を画像テンソルに変換
        image_tensor = self.client.bytes_to_tensor(image_bytes)
        return (image_tensor,)

class StabilityImageSD3(StabilityBaseNode):
    """Stability SD3 Image Generationノード"""
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "prompt": ("STRING", {"multiline": True}),
                "model": (["sd3.5-large", "sd3.5-large-turbo", "sd3.5-medium", "sd3-large", "sd3-large-turbo", "sd3-medium"],),
                "mode": (["text-to-image", "image-to-image"],),
            },
            "optional": {
                "negative_prompt": ("STRING", {"multiline": True, "default": ""}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 4294967295}),
                "cfg_scale": ("FLOAT", {"default": 7.0, "min": 1.0, "max": 10.0}),
                "image": ("IMAGE",),
                "strength": ("FLOAT", {"default": 0.7, "min": 0.0, "max": 1.0}),
                "aspect_ratio": (["1:1", "3:2", "4:3", "16:9", "2:3", "3:4", "9:16"], {"default": "1:1"}),
                "style_preset": (["none", "enhance", "anime", "photographic", "digital-art", "comic-book", "pixel-art", "cinematic", "3d-model", "origami"], {"default": "none"}),
                "output_format": (["png", "webp"], {"default": "png"}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "generate"
    
    def generate(self,
                prompt: str,
                model: str,
                mode: str,
                negative_prompt: str = "",
                seed: int = 0,
                cfg_scale: float = 7.0,
                image: Optional[torch.Tensor] = None,
                strength: float = 0.7,
                aspect_ratio: str = "1:1",
                style_preset: str = "none",
                output_format: str = "png") -> Tuple[torch.Tensor]:
        """画像を生成
        
        Parameters
        ----------
        prompt : str
            生成する画像の説明テキスト
        model : str
            使用するモデル
            - sd3.5-large: 6.5 credits/生成
            - sd3.5-large-turbo: 4 credits/生成
            - sd3.5-medium: 3.5 credits/生成
            - sd3-large: 6.5 credits/生成
            - sd3-large-turbo: 4 credits/生成
            - sd3-medium: 3.5 credits/生成
        mode : str
            生成モード
            - text-to-image: プロンプトのみから生成
            - image-to-image: 入力画像を基に生成
        negative_prompt : str, optional
            生成時に避けたい要素を指定するテキスト
        seed : int, optional
            乱数シード値、デフォルト: 0
        cfg_scale : float, optional
            プロンプトの厳密さ (1.0-10.0)、デフォルト: 7.0
        image : Optional[torch.Tensor], optional
            入力画像 (image-to-imageモード時に必須)
        strength : float, optional
            入力画像の影響度 (0.0-1.0)、デフォルト: 0.7
        aspect_ratio : str, optional
            出力画像のアスペクト比、デフォルト: "1:1"
        style_preset : str, optional
            スタイルプリセット、デフォルト: "none"
        output_format : str, optional
            出力画像フォーマット、デフォルト: "png"

        Returns
        -------
        Tuple[torch.Tensor]
            生成された画像テンソル
        """
        # リクエストデータの準備
        data = {
            "prompt": prompt,
            "model": model,
            "mode": mode,
            "seed": seed,
            "cfg_scale": cfg_scale,
            "output_format": output_format
        }
        
        # パラメータのバリデーション
        if mode == "image-to-image":
            if image is None:
                raise ValueError("image-to-imageモードでは入力画像が必須です")
            if strength is None:
                raise ValueError("image-to-imageモードではstrengthパラメータが必須です")
        else:
            # text-to-imageの場合はアスペクト比を指定
            data["aspect_ratio"] = aspect_ratio

        if negative_prompt:
            data["negative_prompt"] = negative_prompt

        if style_preset != "none":
            data["style_preset"] = style_preset

        if mode == "image-to-image":
            data["strength"] = strength

        # APIリクエストを実行
        headers = {"Accept": "image/*"}
        if mode == "image-to-image":
            files = {
                "image": ("image.png", self.client.image_to_bytes(image))
            }
            response = self.client._make_request(
                "POST",
                "/v2beta/stable-image/generate/sd3",
                data=data,
                files=files,
                headers=headers
            )
        
        # レスポンスのContent-Typeを確認
        print("Response Content-Type:", response.headers.get('content-type'))
        print("Response status code:", response.status_code)
        
        # Content-Typeに基づいて処理を分岐
        content_type = response.headers.get('content-type', '')
        if 'application/json' in content_type:
            # JSONレスポンスの場合
            response_data = response.json()
            print("JSON Response:", response_data)
            if 'artifacts' in response_data and response_data['artifacts']:
                image_data = response_data['artifacts'][0].get('base64')
                if image_data:
                    import base64
                    image_bytes = base64.b64decode(image_data)
                else:
                    raise Exception("No base64 image data in response")
            else:
                raise Exception("No artifacts in response")
        elif 'image/' in content_type:
            # 画像データの場合
            image_bytes = response.content
        else:
            raise Exception(f"Unexpected content type: {content_type}")

        # バイト列を画像テンソルに変換
        image_tensor = self.client.bytes_to_tensor(image_bytes)
        return (image_tensor,)