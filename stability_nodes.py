import torch
from typing import List, Tuple, Dict, Any, Optional
from .api_client import StabilityAPIClient

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
                "api_key": ("STRING", {"default": ""})
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
                api_key: str = "") -> Tuple[torch.Tensor]:
        """画像を生成"""
        
        # API Keyが指定されていれば、それを使用
        if api_key:
            self.client = StabilityAPIClient(api_key)

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
                "api_key": ("STRING", {"default": ""})
            }
        }

    RETURN_TYPES = ("BYTES",)
    FUNCTION = "generate"
    
    def generate(self,
                image: torch.Tensor,
                seed: int = 0,
                cfg_scale: float = 1.8,
                motion_bucket_id: int = 127,
                api_key: str = "") -> Tuple[bytes]:
        """画像からビデオを生成"""
        
        # API Keyが指定されていれば、それを使用
        if api_key:
            self.client = StabilityAPIClient(api_key)

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

class StabilityImageSD3(StabilityBaseNode):
    """Stability SD3 Image Generationノード"""
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "prompt": ("STRING", {"multiline": True}),
                "model": ("STRING", {
                    "default": "sd3.5-large",
                    "options": [
                        "sd3-large", "sd3-large-turbo", "sd3-medium",
                        "sd3.5-large", "sd3.5-large-turbo", "sd3.5-medium"
                    ]
                }),
                "mode": ("STRING", {
                    "default": "text-to-image",
                    "options": ["text-to-image", "image-to-image"]
                }),
            },
            "optional": {
                "negative_prompt": ("STRING", {"multiline": True, "default": ""}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 4294967295}),
                "cfg_scale": ("FLOAT", {"default": 7.0, "min": 0.0, "max": 10.0, "step": 0.1}),
                "image": ("IMAGE",),
                "strength": ("FLOAT", {"default": 0.7, "min": 0.0, "max": 1.0, "step": 0.01}),
                "aspect_ratio": ("STRING", {
                    "default": "1:1",
                    "options": ["16:9", "1:1", "21:9", "2:3", "3:2", "4:5", "5:4", "9:16", "9:21"]
                }),
                "style_preset": ("STRING", {
                    "default": "none",
                    "options": [
                        "none", "3d-model", "analog-film", "anime", "cinematic", "comic-book", 
                        "digital-art", "enhance", "fantasy-art", "isometric", "line-art", 
                        "low-poly", "modeling-compound", "neon-punk", "origami", "photographic", 
                        "pixel-art", "tile-texture"
                    ]
                }),
                "api_key": ("STRING", {"default": ""})
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
                api_key: str = "") -> Tuple[torch.Tensor]:
        """画像を生成"""
        
        # API Keyが指定されていれば、それを使用
        if api_key:
            self.client = StabilityAPIClient(api_key)

        # リクエストデータの準備
        data = {
            "prompt": prompt,
            "model": model,
            "seed": seed,
            "cfg_scale": cfg_scale,
            "output_format": "png"
        }
        
        if negative_prompt:
            data["negative_prompt"] = negative_prompt
            
        if style_preset != "none":
            data["style_preset"] = style_preset
            
        if mode == "text-to-image":
            data["aspect_ratio"] = aspect_ratio
        elif mode == "image-to-image" and image is not None:
            data["strength"] = strength
            files = {"image": ("image.png", self.client.image_to_bytes(image))}
        else:
            raise ValueError("image-to-imageモードでは画像が必要です")

        # APIリクエストを実行
        headers = {"Accept": "image/*"}
        response = self.client._make_request(
            "POST", 
            "/v2beta/stable-image/generate/sd3", 
            data=data,
            files=files if mode == "image-to-image" else None,
            headers=headers
        )
        
        # レスポンスを画像テンソルに変換
        image_tensor = self.client.bytes_to_tensor(response.content)
        return (image_tensor,)

class StabilityUpscaleFast(StabilityBaseNode):
    """Stability Fast Upscalerノード"""
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
            },
            "optional": {
                "api_key": ("STRING", {"default": ""})
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "upscale"
    
    def upscale(self,
                image: torch.Tensor,
                api_key: str = "") -> Tuple[torch.Tensor]:
        """画像をアップスケール"""
        
        # API Keyが指定されていれば、それを使用
        if api_key:
            self.client = StabilityAPIClient(api_key)

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
                "api_key": ("STRING", {"default": ""})
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
                api_key: str = "") -> Tuple[torch.Tensor]:
        """画像をアップスケール"""
        
        # API Keyが指定されていれば、それを使用
        if api_key:
            self.client = StabilityAPIClient(api_key)

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
                "style_preset": ("STRING", {
                    "default": "none",
                    "options": [
                        "none", "3d-model", "analog-film", "anime", "cinematic", "comic-book", 
                        "digital-art", "enhance", "fantasy-art", "isometric", "line-art", 
                        "low-poly", "modeling-compound", "neon-punk", "origami", "photographic", 
                        "pixel-art", "tile-texture"
                    ]
                }),
                "api_key": ("STRING", {"default": ""})
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
                api_key: str = "") -> Tuple[torch.Tensor]:
        """画像をアップスケール"""
        
        # API Keyが指定されていれば、それを使用
        if api_key:
            self.client = StabilityAPIClient(api_key)

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
                "edit_type": (["erase", "inpaint", "outpaint", "search-and-replace", "search-and-recolor", "remove-background"], {"default": "erase"}),
                "prompt": ("STRING", {"multiline": True}),
            },
            "optional": {
                "negative_prompt": ("STRING", {"multiline": True, "default": ""}),
                "mask": ("MASK",),
                "grow_mask": ("INT", {"default": 5, "min": 0, "max": 100}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 4294967295}),
                "style_preset": (["none", "3d-model", "analog-film", "anime", "cinematic", "comic-book", "digital-art", "enhance", "fantasy-art", "isometric", "line-art", "low-poly", "modeling-compound", "neon-punk", "origami", "photographic", "pixel-art", "tile-texture"], {"default": "none"}),
                "api_key": ("STRING", {"default": ""})
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
            api_key: str = "") -> Tuple[torch.Tensor]:
        """画像を編集"""
        
        # API Keyが指定されていれば、それを使用
        if api_key:
            self.client = StabilityAPIClient(api_key)

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
                "aspect_ratio": ("STRING", {
                    "default": "1:1",
                    "options": ["16:9", "1:1", "21:9", "2:3", "3:2", "4:5", "5:4", "9:16", "9:21"]
                }),
            },
            "optional": {
                "negative_prompt": ("STRING", {"multiline": True, "default": ""}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 4294967295}),
                "style_preset": ("STRING", {
                    "default": "none",
                    "options": [
                        "none", "3d-model", "analog-film", "anime", "cinematic", "comic-book", 
                        "digital-art", "enhance", "fantasy-art", "isometric", "line-art", 
                        "low-poly", "modeling-compound", "neon-punk", "origami", "photographic", 
                        "pixel-art", "tile-texture"
                    ]
                }),
                "api_key": ("STRING", {"default": ""})
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
                api_key: str = "") -> Tuple[torch.Tensor]:
        """画像を生成"""
        
        # API Keyが指定されていれば、それを使用
        if api_key:
            self.client = StabilityAPIClient(api_key)

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
            "/v2beta/stable-image/generate/ultra", 
            data=data,
            headers=headers
        )
        
        # レスポンスを画像テンソルに変換
        image_tensor = self.client.bytes_to_tensor(response.content)
        return (image_tensor,)

class StabilityImageCore(StabilityBaseNode):
    """Stability Core Image Generationノード"""
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "prompt": ("STRING", {"multiline": True}),
                "aspect_ratio": ("STRING", {
                    "default": "1:1",
                    "options": ["16:9", "1:1", "21:9", "2:3", "3:2", "4:5", "5:4", "9:16", "9:21"]
                }),
            },
            "optional": {
                "negative_prompt": ("STRING", {"multiline": True, "default": ""}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 4294967295}),
                "style_preset": ("STRING", {
                    "default": "none",
                    "options": [
                        "none", "3d-model", "analog-film", "anime", "cinematic", "comic-book", 
                        "digital-art", "enhance", "fantasy-art", "isometric", "line-art", 
                        "low-poly", "modeling-compound", "neon-punk", "origami", "photographic", 
                        "pixel-art", "tile-texture"
                    ]
                }),
                "api_key": ("STRING", {"default": ""})
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
                api_key: str = "") -> Tuple[torch.Tensor]:
        """画像を生成"""
        
        # API Keyが指定されていれば、それを使用
        if api_key:
            self.client = StabilityAPIClient(api_key)

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