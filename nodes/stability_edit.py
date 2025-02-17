import torch
from typing import Tuple, Optional
from .stability_base_node import StabilityBaseNode
import time

class StabilityEdit(StabilityBaseNode):
    """Stability AIの画像編集機能を提供するノード。"""

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
            "edit_type": (["erase", "inpaint", "outpaint", "search-and-replace",
                         "search-and-recolor", "remove-background", "replace-background-relight"],),
        })

        # optional入力を追加 - edit_typeに応じて必要なものを定義
        types["optional"].update({
            # すべてのedit_type共通のオプション
            "output_format": (["png", "webp", "jpeg"], {"default": "png"}),
            
            # 基本的なedit_type用のオプション
            "prompt": ("STRING", {"multiline": True, "default": ""}),
            "negative_prompt": ("STRING", {"multiline": True, "default": ""}),
            "mask": ("MASK",),
            "grow_mask": ("INT", {"default": 5, "min": 0, "max": 100, "step":1}),
            "seed": ("INT", {"default": 0, "min": 0, "max": 4294967295, "step": 1}),
            "style_preset": (["none", "3d-model", "analog-film", "anime", "cinematic",
                           "comic-book", "digital-art", "enhance", "fantasy-art",
                           "isometric", "line-art", "low-poly", "modeling-compound",
                           "neon-punk", "origami", "photographic", "pixel-art",
                           "tile-texture"], {"default": "none"}),
            
            # search-and-replace, search-and-recolor用
            "search_or_select_prompt": ("STRING", {"multiline": True, "default": ""}),
            
            # outpaint用
            "left": ("INT", {"default": 0, "min": 0, "max": 2000, "step":1}),
            "right": ("INT", {"default": 0, "min": 0, "max": 2000, "step":1}),
            "up": ("INT", {"default": 0, "min": 0, "max": 2000, "step":1}),
            "down": ("INT", {"default": 0, "min": 0, "max": 2000, "step":1}),
            "creativity": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01}),

            # replace-background-relight用
            "background_image": ("IMAGE",),  # background_referenceとして使用
            "background_prompt": ("STRING", {"multiline": True, "default": ""}),
            "foreground_prompt": ("STRING", {"multiline": True, "default": ""}),
            "light_reference_image": ("IMAGE",),  # light_referenceとして使用
            "light_source_direction": (["none", "above", "below", "left", "right"], {"default": "none"}),
            "light_source_strength": ("FLOAT", {"default": 0.3, "min": 0.0, "max": 1.0, "step": 0.01}),
            "preserve_original_subject": ("FLOAT", {"default": 0.6, "min": 0.0, "max": 1.0, "step": 0.01}),
            "original_background_depth": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01}),
            "keep_original_background": (["true", "false"], {"default": "false"}),
        })

        return types

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "edit"

    def edit(self,
            image: torch.Tensor,
            edit_type: str,
            prompt: str = "",
            negative_prompt: str = "",
            mask: Optional[torch.Tensor] = None,
            grow_mask: int = 5,
            seed: int = 0,
            style_preset: str = "none",
            output_format: str = "png",
            search_or_select_prompt: str = "",
            left: int = 0,
            right: int = 0,
            up: int = 0,
            down: int = 0,
            creativity: float = 0.5,
            background_image: Optional[torch.Tensor] = None,
            background_prompt: str = "",
            foreground_prompt: str = "",
            light_reference_image: Optional[torch.Tensor] = None,
            light_source_direction: str = "none",
            light_source_strength: float = 0.3,
            preserve_original_subject: float = 0.6,
            original_background_depth: float = 0.5,
            keep_original_background: str = "false",
            api_key: str = "") -> Tuple[torch.Tensor]:
        """画像を編集"""

        client = self.get_client(api_key)

        # 画像サイズのバリデーション
        height, width = image.shape[1:3]
        
        # edit_typeに応じたバリデーション
        if edit_type == "remove-background":
            if width * height < 4096 or width * height > 4194304:
                raise ValueError(f"総ピクセル数は4,096から4,194,304ピクセルの間である必要があります。現在のピクセル数: {width * height}px")
            if output_format not in ["png", "webp"]:
                raise ValueError(f"remove-backgroundでは'png'または'webp'のみがサポートされています。指定された形式: {output_format}")
        else:
            # その他のedit_typeの共通バリデーション
            if width < 64 or height < 64:
                raise ValueError(f"画像の辺は64px以上である必要があります。現在のサイズ: {width}x{height}px")
            if width * height < 4096 or width * height > 9437184:
                raise ValueError(f"総ピクセル数は4096px以上9437184px以下である必要があります。現在のピクセル数: {width * height}px")
            aspect_ratio = width / height
            if aspect_ratio < 0.4 or aspect_ratio > 2.5:
                raise ValueError(f"アスペクト比は1:2.5から2.5:1の間である必要があります。現在のアスペクト比: {aspect_ratio:.2f}")

        if edit_type == "replace-background-relight":
            # replace-background-relightの特別なバリデーション
            if not background_prompt and background_image is None:
                raise ValueError("background_promptまたはbackground_imageのいずれかが必要です")
            
            if light_source_strength != 0.3 and light_source_direction == "none" and light_reference_image is None:
                raise ValueError("light_source_strengthを使用する場合は、light_source_directionまたはlight_reference_imageが必要です")

            # データの準備
            data = {
                "output_format": output_format,
                "preserve_original_subject": preserve_original_subject,
                "original_background_depth": original_background_depth,
                "keep_original_background": keep_original_background,
                "seed": seed
            }

            if background_prompt:
                data["background_prompt"] = background_prompt
            if foreground_prompt:
                data["foreground_prompt"] = foreground_prompt
            if negative_prompt:
                data["negative_prompt"] = negative_prompt
            if light_source_direction != "none":
                data["light_source_direction"] = light_source_direction
            if light_source_strength != 0.3:
                data["light_source_strength"] = light_source_strength

            # ファイルの準備
            files = {
                "subject_image": ("image.png", client.image_to_bytes(image))
            }

            if background_image is not None:
                files["background_reference"] = ("background.png", client.image_to_bytes(background_image))
            if light_reference_image is not None:
                files["light_reference"] = ("light.png", client.image_to_bytes(light_reference_image))

            # 非同期APIリクエストを実行
            response = client._make_request(
                "POST",
                "/v2beta/stable-image/edit/replace-background-relight",
                data=data,
                files=files
            )

            # レスポンスからgeneration_idを取得
            generation_id = response.json()["id"]

            # 結果が得られるまでポーリング
            retry_count = 0
            max_retries = 30  # 5分のタイムアウト (10秒 × 30)

            while retry_count < max_retries:
                try:
                    # 結果取得リクエスト
                    poll_response = client._make_request(
                        "GET",
                        f"/v2beta/results/{generation_id}",
                        headers={"Accept": "image/*"}
                    )

                    if poll_response.status_code == 200:
                        # 生成完了
                        image_tensor = client.bytes_to_tensor(poll_response.content)
                        return (image_tensor,)
                    elif poll_response.status_code == 202:
                        # まだ生成中
                        time.sleep(10)  # 10秒待機
                        retry_count += 1
                        continue
                    else:
                        raise Exception(f"Unexpected status code: {poll_response.status_code}")

                except Exception as e:
                    raise Exception(f"Error while waiting for completion: {str(e)}")

            raise Exception("Generation timed out after 5 minutes")

        elif edit_type == "remove-background":
            # remove-backgroundの実装
            data = {
                "output_format": output_format
            }
            files = {
                "image": ("image.png", client.image_to_bytes(image))
            }
            
        else:
            # その他のedit_typeの実装（既存のコード）
            data = {
                "prompt": prompt,
                "seed": seed,
                "output_format": output_format
            }

            if negative_prompt:
                data["negative_prompt"] = negative_prompt

            if style_preset != "none":
                data["style_preset"] = style_preset

            files = {
                "image": ("image.png", client.image_to_bytes(image))
            }

            # edit_type固有のパラメータを追加
            if edit_type in ["erase", "inpaint"] and mask is not None:
                if grow_mask != 5:
                    data["grow_mask"] = grow_mask
                mask_bytes = client.image_to_bytes(mask)
                files["mask"] = ("mask.png", mask_bytes)
            elif edit_type == "search-and-replace":
                data["search_prompt"] = search_or_select_prompt
            elif edit_type == "search-and-recolor":
                data["select_prompt"] = search_or_select_prompt
            elif edit_type == "outpaint":
                data["creativity"] = creativity
                if left: data["left"] = left
                if right: data["right"] = right
                if up: data["up"] = up
                if down: data["down"] = down

        # 非replace-background-relightの場合のAPIリクエスト
        if edit_type != "replace-background-relight":
            headers = {"Accept": "image/*"}
            response = client._make_request(
                "POST",
                f"/v2beta/stable-image/edit/{edit_type}",
                data=data,
                files=files,
                headers=headers
            )

            # レスポンスを画像テンソルに変換
            image_tensor = client.bytes_to_tensor(response.content)
            return (image_tensor,)