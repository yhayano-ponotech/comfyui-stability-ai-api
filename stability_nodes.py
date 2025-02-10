import torch
from typing import List, Tuple, Dict, Any, Optional
from .api_client import StabilityAPIClient
import json
import cv2
import numpy as np
import io

class StabilityBaseNode:
    """StabilityAI APIノードの基底クラス"""
    CATEGORY = "Stability AI"

    def __init__(self):
        self.client = StabilityAPIClient()
        
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

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "generate"
    
    def generate(self,
                image: torch.Tensor,
                seed: int = 0,
                cfg_scale: float = 1.8,
                motion_bucket_id: int = 127) -> Tuple[torch.Tensor]:
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
        
        if response.status_code == 200:        
            # 生成完了まで待機
            while True:
                response = self.client._make_request(
                    "GET",
                    f"/v2beta/image-to-video/result/{generation_id}",
                    headers={"Accept": "video/*"}
                )
                
                if response.status_code == 200:
                    # ビデオデータをバイトストリームとして読み込む
                    video_bytes = io.BytesIO(response.content)
                    
                    # 一時ファイルにビデオを保存
                    temp_file = "temp_video.mp4"
                    with open(temp_file, "wb") as f:
                        f.write(response.content)
                    
                    # ビデオを読み込む
                    cap = cv2.VideoCapture(temp_file)
                    
                    frames = []
                    while True:
                        ret, frame = cap.read()
                        if not ret:
                            break
                        # BGRからRGBに変換
                        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        frames.append(frame)
                    
                    cap.release()
                    import os
                    os.remove(temp_file)
                    
                    # フレームをnumpy配列に変換 [B, H, W, C]形式
                    frames_array = np.stack(frames)
                    # float32に変換し、0-1の範囲にスケーリング
                    frames_array = frames_array.astype(np.float32) / 255.0
                    # フレームをtorch.Tensorに変換（形状は[B, H, W, C]のまま）
                    frames_tensor = torch.from_numpy(frames_array)
                    
                    return (frames_tensor,)
                
        else:
            throw_error = response.json()["error"]
            raise Exception(throw_error)

class StabilityUpscaleFast(StabilityBaseNode):
    """高速な画像アップスケールを行うノード"""
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
            },
            "optional": {
                "output_format": (["png", "jpeg", "webp"], {"default": "png"}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "upscale"
    
    def upscale(self,
                image: torch.Tensor,
                output_format: str = "png") -> Tuple[torch.Tensor]:
        """画像を高速にアップスケール

        Parameters
        ----------
        image : torch.Tensor
            入力画像。形式は[1, H, W, 3] (RGB)
            制限:
            - 幅: 32-1536 px
            - 高さ: 32-1536 px
            - 総ピクセル数: 1024-1048576 px
        output_format : str, optional
            出力フォーマット, デフォルト: "png"

        Returns
        -------
        Tuple[torch.Tensor]
            アップスケールされた画像。形式は[1, H*2, W*2, 3] (RGB)
        """
        # 画像サイズのバリデーション
        height, width = image.shape[1:3]
        if width < 32 or width > 1536:
            raise ValueError(f"画像の幅は32px以上1536px以下である必要があります。現在の幅: {width}px")
        if height < 32 or height > 1536:
            raise ValueError(f"画像の高さは32px以上1536px以下である必要があります。現在の高さ: {height}px")
        if width * height < 1024 or width * height > 1048576:
            raise ValueError(f"総ピクセル数は1024px以上1048576px以下である必要があります。現在のピクセル数: {width * height}px")

        # リクエストデータの準備
        data = {
            "output_format": output_format
        }

        files = {
            "image": ("image.png", self.client.image_to_bytes(image)),
        }

        # APIリクエストを実行
        headers = {"Accept": "image/*"}
        response = self.client._make_request(
            "POST", 
            "/v2beta/stable-image/upscale/fast", 
            data=data,
            files=files,
            headers=headers
        )
        
        # レスポンスを画像テンソルに変換
        image_tensor = self.client.bytes_to_tensor(response.content)
        return (image_tensor,)

class StabilityUpscaleConservative(StabilityBaseNode):
    """保守的な画像アップスケールを行うノード。
    高品質な結果を維持しながら、元の画像の特徴を活かしてアップスケールします。
    """
    
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
                "style_preset": (["none", "3d-model", "analog-film", "anime", "cinematic", 
                               "comic-book", "digital-art", "enhance", "fantasy-art", 
                               "isometric", "line-art", "low-poly", "modeling-compound", 
                               "neon-punk", "origami", "photographic", "pixel-art", 
                               "tile-texture"], {"default": "none"}),
                "output_format": (["png", "jpeg", "webp"], {"default": "png"}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "upscale"
    
    def upscale(self,
                image: torch.Tensor,
                prompt: str,
                negative_prompt: str = "",
                seed: int = 0,
                creativity: float = 0.35,
                style_preset: str = "none",
                output_format: str = "png") -> Tuple[torch.Tensor]:
        """画像を保守的にアップスケール

        Parameters
        ----------
        image : torch.Tensor
            入力画像。形式は[1, H, W, 3] (RGB)
            制限:
            - 辺の長さ: 64px以上
            - 総ピクセル数: 4096-9437184 px
            - アスペクト比: 1:2.5 から 2.5:1 の間
        prompt : str
            アップスケール時に参照するプロンプト。
            例: "A high quality photograph with sharp details"
        negative_prompt : str, optional
            避けたい要素を指定するプロンプト
            例: "blurry, low quality, artifacts"
        seed : int, optional
            生成の再現性のためのシード値
            デフォルト: 0 (ランダム)
        creativity : float, optional
            クリエイティビティの度合い(0.2-0.5)
            - 0.2: より保守的
            - 0.5: より創造的
            デフォルト: 0.35
        style_preset : str, optional
            スタイルプリセット
            デフォルト: "none"
        output_format : str, optional
            出力フォーマット
            デフォルト: "png"

        Returns
        -------
        Tuple[torch.Tensor]
            アップスケールされた画像。形式は[1, H*4, W*4, 3] (RGB)
            
        Raises
        ------
        ValueError
            画像サイズが制限を超えている場合
        Exception
            API呼び出しに失敗した場合
        """
        # 画像サイズのバリデーション
        height, width = image.shape[1:3]
        if width < 64 or height < 64:
            raise ValueError(f"画像の辺は64px以上である必要があります。現在のサイズ: {width}x{height}px")
        if width * height < 4096 or width * height > 9437184:
            raise ValueError(f"総ピクセル数は4096px以上9437184px以下である必要があります。現在のピクセル数: {width * height}px")
        aspect_ratio = width / height
        if aspect_ratio < 0.4 or aspect_ratio > 2.5:
            raise ValueError(f"アスペクト比は1:2.5から2.5:1の間である必要があります。現在のアスペクト比: {aspect_ratio:.2f}")

        # リクエストデータの準備
        data = {
            "prompt": prompt,
            "seed": seed,
            "creativity": creativity,
            "output_format": output_format
        }

        if negative_prompt:
            data["negative_prompt"] = negative_prompt
            
        if style_preset != "none":
            data["style_preset"] = style_preset

        files = {
            "image": ("image.png", self.client.image_to_bytes(image))
        }

        # 生成開始リクエスト - image/*を使用
        print("Requesting conservative upscale generation...")
        print("Request data:", data)
        
        # クライアントに直接画像データを要求
        response = self.client._make_request(
            "POST", 
            "/v2beta/stable-image/upscale/conservative", 
            data=data,
            files=files,
            headers={"Accept": "image/*"}
        )
        
        # レスポンスのContent-Typeを確認
        content_type = response.headers.get('content-type', '')
        print("Response Content-Type:", content_type)
        
        if 'image/' in content_type:
            # 画像データを直接テンソルに変換
            image_tensor = self.client.bytes_to_tensor(response.content)
            return (image_tensor,)
        else:
            raise Exception(f"Unexpected content type received: {content_type}")

class StabilityUpscaleCreative(StabilityBaseNode):
    """クリエイティブな画像アップスケールを行うノード。
    入力画像をAIを使って詳細を追加しながら高解像度化します。
    """
    
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
                "style_preset": (["none", "3d-model", "analog-film", "anime", "cinematic", 
                               "comic-book", "digital-art", "enhance", "fantasy-art", 
                               "isometric", "line-art", "low-poly", "modeling-compound", 
                               "neon-punk", "origami", "photographic", "pixel-art", 
                               "tile-texture"], {"default": "none"}),
                "output_format": (["png", "jpeg", "webp"], {"default": "png"}),
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
                style_preset: str = "none",
                output_format: str = "png") -> Tuple[torch.Tensor]:
        """画像をクリエイティブにアップスケール

        Parameters
        ----------
        image : torch.Tensor
            入力画像。形式は[1, H, W, 3] (RGB)
            制限:
            - 辺の長さ: 64px以上
            - 総ピクセル数: 4096-1048576 px
        prompt : str
            アップスケール時に参照するプロンプト。
            例: "A detailed portrait of a cat with sharp eyes"
        negative_prompt : str, optional
            避けたい要素を指定するプロンプト
            例: "blurry, low quality"
        seed : int, optional
            生成の再現性のためのシード値
            デフォルト: 0 (ランダム)
        creativity : float, optional
            クリエイティビティの度合い(0.1-0.5)
            - 0.1: オリジナルに近い
            - 0.5: より創造的
            デフォルト: 0.3
        style_preset : str, optional
            スタイルプリセット
            デフォルト: "none"
        output_format : str, optional
            出力フォーマット
            デフォルト: "png"

        Returns
        -------
        Tuple[torch.Tensor]
            アップスケールされた画像。形式は[1, H*4, W*4, 3] (RGB)
            
        Raises
        ------
        ValueError
            画像サイズが制限を超えている場合
        Exception
            API呼び出しに失敗した場合やタイムアウトした場合
        """
        import base64
        import io
        from PIL import Image
        import time

        # 画像サイズのバリデーション
        height, width = image.shape[1:3]
        if width < 64 or height < 64:
            raise ValueError(f"画像の辺は64px以上である必要があります。現在のサイズ: {width}x{height}px")
        if width * height < 4096 or width * height > 1048576:
            raise ValueError(f"総ピクセル数は4096px以上1048576px以下である必要があります。現在のピクセル数: {width * height}px")

        # リクエストデータの準備
        data = {
            "prompt": prompt,
            "seed": seed,
            "creativity": creativity,
            "output_format": output_format
        }

        if negative_prompt:
            data["negative_prompt"] = negative_prompt
            
        if style_preset != "none":
            data["style_preset"] = style_preset

        files = {
            "image": ("image.png", self.client.image_to_bytes(image))
        }

        # 生成開始リクエスト
        print("Requesting upscale generation...")
        print("Request data:", data)
        
        init_response = self.client._make_request(
            "POST", 
            "/v2beta/stable-image/upscale/creative", 
            data=data,
            files=files,
            headers={"Accept": "*/*"}
        )
        
        init_data = init_response.json()
        print("Initial response:", init_data)
        
        if "id" not in init_data:
            raise Exception("No generation ID in response")
            
        generation_id = init_data["id"]
        print(f"Got generation ID: {generation_id}")
        
        # 生成完了を待機（最大5分）
        retry_count = 0
        max_retries = 30  # 10秒 × 30回 = 5分
        
        while retry_count < max_retries:
            try:
                print(f"Checking result... (attempt {retry_count + 1}/{max_retries})")
                
                # 結果取得リクエスト - application/jsonを使用
                poll_response = self.client._make_request(
                    "GET",
                    f"/v2beta/results/{generation_id}",
                    headers={"Accept": "*/*"}  # ヘッダーを*/*に変更
                )
                
                print("Poll response status:", poll_response.status_code)
                print("Poll response headers:", poll_response.headers)
                
                if poll_response.status_code == 200:
                    # アップスケール完了
                    print(f"Upscale completed after {retry_count * 10} seconds")
                    
                    # Content-Typeに基づいて処理を分岐
                    content_type = poll_response.headers.get('content-type', '')
                    print("Response Content-Type:", content_type)
                    
                    if 'application/json' in content_type:
                        # JSONレスポンスの場合
                        response_data = poll_response.json()
                        print("JSON Response:", response_data)
                        
                        if 'artifacts' in response_data and response_data['artifacts']:
                            if 'base64' in response_data['artifacts'][0]:
                                image_data = base64.b64decode(response_data['artifacts'][0]['base64'])
                            else:
                                raise Exception("No base64 data in artifact")
                        else:
                            raise Exception("No valid artifacts in response")
                            
                    elif 'image/' in content_type:
                        # 直接画像データが返される場合
                        image_data = poll_response.content
                    else:
                        raise Exception(f"Unexpected content type: {content_type}")
                    
                    # 画像データをテンソルに変換
                    image_tensor = self.client.bytes_to_tensor(image_data)
                    return (image_tensor,)
                    
                elif poll_response.status_code == 202:
                    # まだ生成中
                    print(f"Still processing... ({retry_count + 1}/{max_retries})")
                    time.sleep(10)  # 10秒待機
                    retry_count += 1
                    continue
                else:
                    raise Exception(f"Unexpected status code: {poll_response.status_code}")
                    
            except Exception as e:
                print(f"Error occurred: {str(e)}")
                raise Exception(f"Error while waiting for upscale completion: {str(e)}")
        
        raise Exception("Upscale timed out after 5 minutes")

class StabilityEdit(StabilityBaseNode):
    """Stability AIの画像編集機能を提供するノード。
    以下の編集モードをサポート:
    - erase: マスクで指定した領域を消去
    - inpaint: マスクで指定した領域を再生成
    - outpaint: 画像を任意の方向に拡張
    - search-and-replace: 指定したオブジェクトを置換
    - search-and-recolor: 指定したオブジェクトの色を変更
    - remove-background: 背景を自動的に削除
    """
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "edit_type": (["erase", "inpaint", "outpaint", "search-and-replace", 
                             "search-and-recolor", "remove-background"],),
                "prompt": ("STRING", {"multiline": True}),
            },
            "optional": {
                "negative_prompt": ("STRING", {"multiline": True, "default": ""}),
                "mask": ("MASK",),
                "grow_mask": ("INT", {"default": 5, "min": 0, "max": 100}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 4294967295}),
                "style_preset": (["none", "3d-model", "analog-film", "anime", "cinematic", 
                               "comic-book", "digital-art", "enhance", "fantasy-art", 
                               "isometric", "line-art", "low-poly", "modeling-compound", 
                               "neon-punk", "origami", "photographic", "pixel-art", 
                               "tile-texture"], {"default": "none"}),
                "output_format": (["png", "jpeg", "webp"], {"default": "png"}),
                # search-and-replace, search-and-recolor用
                "select_prompt": ("STRING", {"multiline": True, "default": ""}),
                "fidelity": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01}),
                # outpaint用
                "left": ("INT", {"default": 0, "min": 0, "max": 2000}),
                "right": ("INT", {"default": 0, "min": 0, "max": 2000}),
                "up": ("INT", {"default": 0, "min": 0, "max": 2000}),
                "down": ("INT", {"default": 0, "min": 0, "max": 2000}),
                "creativity": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01}),
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
            style_preset: str = "none",
            output_format: str = "png",
            select_prompt: str = "",
            fidelity: float = 0.5,
            left: int = 0,
            right: int = 0,
            up: int = 0,
            down: int = 0,
            creativity: float = 0.5) -> Tuple[torch.Tensor]:
        """画像を編集

        Parameters
        ----------
        image : torch.Tensor
            入力画像。形式は[1, H, W, 3] (RGB)
            制限:
            - 辺の長さ: 64px以上
            - 総ピクセル数: 4096-9437184 px
            - アスペクト比: 1:2.5 から 2.5:1 の間
        edit_type : str
            編集タイプ:
            - erase: マスクで指定した領域を消去
            - inpaint: マスクで指定した領域を再生成
            - outpaint: 画像を拡張
            - search-and-replace: 指定したオブジェクトを置換
            - search-and-recolor: 指定したオブジェクトの色を変更
            - remove-background: 背景を削除
        prompt : str
            生成を導くプロンプト。用途:
            - inpaint: 再生成する内容の指定
            - search-and-replace: 置換後のオブジェクトの指定
            - search-and-recolor: 変更後の色の指定
        negative_prompt : str, optional
            避けたい要素を指定するプロンプト
        mask : torch.Tensor, optional
            編集マスク。形式は[H, W]。値の範囲は0-1
            erase, inpaintモードで必須
        grow_mask : int, optional
            マスクの拡張サイズ(px)。マスクの境界をぼかすために使用
            デフォルト: 5
        seed : int, optional
            生成の再現性のためのシード値
            デフォルト: 0 (ランダム)
        style_preset : str, optional
            スタイルプリセット
            デフォルト: "none"
        output_format : str, optional
            出力フォーマット
            デフォルト: "png"
        select_prompt : str, optional
            search-and-replace, search-and-recolor用の検索プロンプト
            例: "red car" -> 赤い車を検索
        fidelity : float, optional
            search-and-recolorでの色の忠実度
            - 0.0: 完全に新しい色
            - 1.0: 元の色に近い
            デフォルト: 0.5
        left, right, up, down : int, optional
            outpaint用の拡張サイズ(px)
            少なくとも1つの方向に0より大きい値が必要
        creativity : float, optional
            outpaintでの創造性の度合い
            - 0.0: 保守的
            - 1.0: 創造的
            デフォルト: 0.5

        Returns
        -------
        Tuple[torch.Tensor]
            編集された画像。形式は[1, H', W', 3] (RGB)
            H', W'は編集タイプによって変化:
            - outpaint: 指定された方向に拡張
            - その他: 入力と同じサイズ
            
        Raises
        ------
        ValueError
            - 画像サイズが制限を超えている場合
            - 必要なパラメータが不足している場合
            - パラメータの値が不適切な場合
        Exception
            API呼び出しに失敗した場合
        """
        # マスクの前処理を追加
        if mask is not None and edit_type in ["erase", "inpaint"]:
            # マスクの形状を確認
            if len(mask.shape) == 4:  # [B,C,H,W]形式
                mask = mask.squeeze(0).squeeze(0)  # [H,W]形式に変換
            elif len(mask.shape) == 3:  # [B,H,W]形式
                mask = mask.squeeze(0)  # [H,W]形式に変換
            
            # マスクの値を0-1の範囲に正規化
            if mask.dtype != torch.float32:
                mask = mask.float()
            if mask.max() > 1.0:
                mask = mask / 255.0

        # 以下は既存のコード
        # 画像サイズのバリデーション
        height, width = image.shape[1:3]
        if width < 64 or height < 64:
            raise ValueError(f"画像の辺は64px以上である必要があります。現在のサイズ: {width}x{height}px")
        if width * height < 4096 or width * height > 9437184:
            raise ValueError(f"総ピクセル数は4096px以上9437184px以下である必要があります。現在のピクセル数: {width * height}px")
        aspect_ratio = width / height
        if aspect_ratio < 0.4 or aspect_ratio > 2.5:
            raise ValueError(f"アスペクト比は1:2.5から2.5:1の間である必要があります。現在のアスペクト比: {aspect_ratio:.2f}")

        # 編集タイプごとのバリデーション
        if edit_type in ["erase", "inpaint"]:
            if mask is None:
                raise ValueError(f"{edit_type}にはマスクが必要です")
        elif edit_type in ["search-and-replace", "search-and-recolor"]:
            if not select_prompt:
                raise ValueError(f"{edit_type}には select_prompt が必要です")
            if edit_type == "search-and-recolor":
                if not 0 <= fidelity <= 1:
                    raise ValueError("fidelityは0から1の間である必要があります")
        elif edit_type == "outpaint":
            if not any([left, right, up, down]):
                raise ValueError("outpaintには少なくとも1つの方向の拡張サイズが必要です")
            if not 0 <= creativity <= 1:
                raise ValueError("creativityは0から1の間である必要があります")

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
            
        if grow_mask != 5 and edit_type in ["erase", "inpaint"]:
            data["grow_mask"] = grow_mask

        # 編集タイプごとの追加パラメータ
        if edit_type in ["search-and-replace", "search-and-recolor"]:
            data["select_prompt"] = select_prompt
            if edit_type == "search-and-recolor":
                data["fidelity"] = fidelity
        elif edit_type == "outpaint":
            data["creativity"] = creativity
            if left: data["left"] = left
            if right: data["right"] = right
            if up: data["up"] = up
            if down: data["down"] = down

        # ファイルの準備
        files = {
            "image": ("image.png", self.client.image_to_bytes(image))
        }
        
        if edit_type in ["erase", "inpaint"] and mask is not None:
            # マスクをPNG形式のバイト列に変換
            mask_bytes = self.client.image_to_bytes(mask)
            files["mask"] = ("mask.png", mask_bytes)

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

class StabilityControlSketch(StabilityBaseNode):
    """スケッチや輪郭線から画像を生成するノード。
    入力スケッチの線や形状を参照して、詳細な画像を生成します。
    """
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "prompt": ("STRING", {"multiline": True}),
            },
            "optional": {
                "negative_prompt": ("STRING", {"multiline": True, "default": ""}),
                "control_strength": ("FLOAT", {"default": 0.7, "min": 0.0, "max": 1.0, "step": 0.01}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 4294967295}),
                "style_preset": (["none", "3d-model", "analog-film", "anime", "cinematic", 
                               "comic-book", "digital-art", "enhance", "fantasy-art", 
                               "isometric", "line-art", "low-poly", "modeling-compound", 
                               "neon-punk", "origami", "photographic", "pixel-art", 
                               "tile-texture"], {"default": "none"}),
                "output_format": (["png", "jpeg", "webp"], {"default": "png"}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "generate"
    
    def generate(self,
                image: torch.Tensor,
                prompt: str,
                negative_prompt: str = "",
                control_strength: float = 0.7,
                seed: int = 0,
                style_preset: str = "none",
                output_format: str = "png") -> Tuple[torch.Tensor]:
        """スケッチから画像を生成

        Parameters
        ----------
        image : torch.Tensor
            入力スケッチ画像。形式は[1, H, W, 3] (RGB)
            制限:
            - 辺の長さ: 64px以上
            - 総ピクセル数: 4096-9437184 px
            - アスペクト比: 1:2.5 から 2.5:1 の間
        prompt : str
            生成したい画像の説明
        negative_prompt : str, optional
            避けたい要素を指定するプロンプト
        control_strength : float, optional
            スケッチの影響度(0.0-1.0)
            - 0.0: プロンプトのみに基づいて生成
            - 1.0: スケッチを厳密に参照
            デフォルト: 0.7
        seed : int, optional
            生成の再現性のためのシード値
        style_preset : str, optional
            スタイルプリセット
        output_format : str, optional
            出力フォーマット

        Returns
        -------
        Tuple[torch.Tensor]
            生成された画像。形式は[1, H, W, 3] (RGB)
        """
        # 画像サイズのバリデーション
        height, width = image.shape[1:3]
        if width < 64 or height < 64:
            raise ValueError(f"画像の辺は64px以上である必要があります。現在のサイズ: {width}x{height}px")
        if width * height < 4096 or width * height > 9437184:
            raise ValueError(f"総ピクセル数は4096px以上9437184px以下である必要があります。現在のピクセル数: {width * height}px")
        aspect_ratio = width / height
        if aspect_ratio < 0.4 or aspect_ratio > 2.5:
            raise ValueError(f"アスペクト比は1:2.5から2.5:1の間である必要があります。現在のアスペクト比: {aspect_ratio:.2f}")

        # リクエストデータの準備
        data = {
            "prompt": prompt,
            "control_strength": control_strength,
            "seed": seed,
            "output_format": output_format
        }

        if negative_prompt:
            data["negative_prompt"] = negative_prompt
            
        if style_preset != "none":
            data["style_preset"] = style_preset

        # ファイルの準備
        files = {
            "image": ("image.png", self.client.image_to_bytes(image))
        }

        # APIリクエストを実行
        headers = {"Accept": "image/*"}
        response = self.client._make_request(
            "POST", 
            "/v2beta/stable-image/control/sketch", 
            data=data,
            files=files,
            headers=headers
        )
        
        # レスポンスを画像テンソルに変換
        image_tensor = self.client.bytes_to_tensor(response.content)
        return (image_tensor,)

class StabilityControlStructure(StabilityBaseNode):
    """入力画像の構造を維持して画像を生成するノード。
    3Dモデルの再作成やキャラクターのポーズ維持などに適しています。
    """
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "prompt": ("STRING", {"multiline": True}),
            },
            "optional": {
                "negative_prompt": ("STRING", {"multiline": True, "default": ""}),
                "control_strength": ("FLOAT", {"default": 0.7, "min": 0.0, "max": 1.0, "step": 0.01}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 4294967295}),
                "style_preset": (["none", "3d-model", "analog-film", "anime", "cinematic", 
                               "comic-book", "digital-art", "enhance", "fantasy-art", 
                               "isometric", "line-art", "low-poly", "modeling-compound", 
                               "neon-punk", "origami", "photographic", "pixel-art", 
                               "tile-texture"], {"default": "none"}),
                "output_format": (["png", "jpeg", "webp"], {"default": "png"}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "generate"
    
    def generate(self,
                image: torch.Tensor,
                prompt: str,
                negative_prompt: str = "",
                control_strength: float = 0.7,
                seed: int = 0,
                style_preset: str = "none",
                output_format: str = "png") -> Tuple[torch.Tensor]:
        """画像の構造を維持して生成

        Parameters
        ----------
        image : torch.Tensor
            入力画像。形式は[1, H, W, 3] (RGB)
            制限:
            - 辺の長さ: 64px以上
            - 総ピクセル数: 4096-9437184 px
            - アスペクト比: 1:2.5 から 2.5:1 の間
        prompt : str
            生成したい画像の説明
        negative_prompt : str, optional
            避けたい要素を指定するプロンプト
        control_strength : float, optional
            構造の維持度(0.0-1.0)
            - 0.0: プロンプトのみに基づいて生成
            - 1.0: 入力画像の構造を厳密に維持
            デフォルト: 0.7
        seed : int, optional
            生成の再現性のためのシード値
        style_preset : str, optional
            スタイルプリセット
        output_format : str, optional
            出力フォーマット

        Returns
        -------
        Tuple[torch.Tensor]
            生成された画像。形式は[1, H, W, 3] (RGB)
        """
        # 画像サイズのバリデーション
        height, width = image.shape[1:3]
        if width < 64 or height < 64:
            raise ValueError(f"画像の辺は64px以上である必要があります。現在のサイズ: {width}x{height}px")
        if width * height < 4096 or width * height > 9437184:
            raise ValueError(f"総ピクセル数は4096px以上9437184px以下である必要があります。現在のピクセル数: {width * height}px")
        aspect_ratio = width / height
        if aspect_ratio < 0.4 or aspect_ratio > 2.5:
            raise ValueError(f"アスペクト比は1:2.5から2.5:1の間である必要があります。現在のアスペクト比: {aspect_ratio:.2f}")

        # リクエストデータの準備
        data = {
            "prompt": prompt,
            "control_strength": control_strength,
            "seed": seed,
            "output_format": output_format
        }

        if negative_prompt:
            data["negative_prompt"] = negative_prompt
            
        if style_preset != "none":
            data["style_preset"] = style_preset

        # ファイルの準備
        files = {
            "image": ("image.png", self.client.image_to_bytes(image))
        }

        # APIリクエストを実行
        headers = {"Accept": "image/*"}
        response = self.client._make_request(
            "POST", 
            "/v2beta/stable-image/control/structure", 
            data=data,
            files=files,
            headers=headers
        )
        
        # レスポンスを画像テンソルに変換
        image_tensor = self.client.bytes_to_tensor(response.content)
        return (image_tensor,)

class StabilityControlStyle(StabilityBaseNode):
    """入力画像のスタイルを参照して画像を生成するノード。
    色使い、テクスチャ、アート性などのスタイル要素を抽出して使用します。
    """
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "prompt": ("STRING", {"multiline": True}),
            },
            "optional": {
                "negative_prompt": ("STRING", {"multiline": True, "default": ""}),
                "fidelity": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01}),
                "aspect_ratio": (["1:1", "16:9", "21:9", "2:3", "3:2", "4:5", "5:4", "9:16", "9:21"], {"default": "1:1"}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 4294967295}),
                "style_preset": (["none", "3d-model", "analog-film", "anime", "cinematic", 
                               "comic-book", "digital-art", "enhance", "fantasy-art", 
                               "isometric", "line-art", "low-poly", "modeling-compound", 
                               "neon-punk", "origami", "photographic", "pixel-art", 
                               "tile-texture"], {"default": "none"}),
                "output_format": (["png", "jpeg", "webp"], {"default": "png"}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "generate"
    
    def generate(self,
                image: torch.Tensor,
                prompt: str,
                negative_prompt: str = "",
                fidelity: float = 0.5,
                aspect_ratio: str = "1:1",
                seed: int = 0,
                style_preset: str = "none",
                output_format: str = "png") -> Tuple[torch.Tensor]:
        """画像のスタイルを参照して生成

        Parameters
        ----------
        image : torch.Tensor
            入力画像。形式は[1, H, W, 3] (RGB)
            制限:
            - 辺の長さ: 64px以上
            - 総ピクセル数: 4096-9437184 px
            - アスペクト比: 1:2.5 から 2.5:1 の間
        prompt : str
            生成したい画像の説明
        negative_prompt : str, optional
            避けたい要素を指定するプロンプト
        fidelity : float, optional
            スタイルの忠実度(0.0-1.0)
            - 0.0: プロンプトを重視
            - 1.0: 入力画像のスタイルを重視
            デフォルト: 0.5
        aspect_ratio : str, optional
            出力画像のアスペクト比
            デフォルト: "1:1"
        seed : int, optional
            生成の再現性のためのシード値
        style_preset : str, optional
            スタイルプリセット
        output_format : str, optional
            出力フォーマット

        Returns
        -------
        Tuple[torch.Tensor]
            生成された画像。形式は[1, H, W, 3] (RGB)
        """
        # 画像サイズのバリデーション
        height, width = image.shape[1:3]
        if width < 64 or height < 64:
            raise ValueError(f"画像の辺は64px以上である必要があります。現在のサイズ: {width}x{height}px")
        if width * height < 4096 or width * height > 9437184:
            raise ValueError(f"総ピクセル数は4096px以上9437184px以下である必要があります。現在のピクセル数: {width * height}px")
        aspect_ratio_value = width / height
        if aspect_ratio_value < 0.4 or aspect_ratio_value > 2.5:
            raise ValueError(f"アスペクト比は1:2.5から2.5:1の間である必要があります。現在のアスペクト比: {aspect_ratio_value:.2f}")

        # リクエストデータの準備
        data = {
            "prompt": prompt,
            "fidelity": fidelity,
            "aspect_ratio": aspect_ratio,
            "seed": seed,
            "output_format": output_format
        }

        if negative_prompt:
            data["negative_prompt"] = negative_prompt
            
        if style_preset != "none":
            data["style_preset"] = style_preset

        # ファイルの準備
        files = {
            "image": ("image.png", self.client.image_to_bytes(image))
        }

        # APIリクエストを実行
        headers = {"Accept": "image/*"}
        response = self.client._make_request(
            "POST", 
            "/v2beta/stable-image/control/style", 
            data=data,
            files=files,
            headers=headers
        )
        
        # レスポンスを画像テンソルに変換
        image_tensor = self.client.bytes_to_tensor(response.content)
        return (image_tensor,)