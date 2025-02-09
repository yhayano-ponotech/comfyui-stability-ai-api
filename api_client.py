import os
import json
import requests
from typing import Optional, Dict, Any, Union
import torch
import numpy as np
from PIL import Image
import io

class StabilityAPIClient:
    """
    Stability AI APIとの通信を行うクライアントクラス
    """
    def __init__(self, api_key: Optional[str] = None):
        """
        初期化
        
        Parameters:
        -----------
        api_key : str, optional
            Stability AI APIキー。未指定の場合は環境変数から読み込み
        """
        from .config_manager import ConfigManager
        
        # APIキーの取得優先順位:
        # 1. 直接指定されたAPIキー
        # 2. 環境変数のAPIキー
        # 3. config.iniのAPIキー
        self.api_key = api_key or ConfigManager().get_api_key()
        
        if not self.api_key or self.api_key == "your_api_key_here":
            raise ValueError("API key must be provided either directly, through STABILITY_API_KEY environment variable, or in config.ini")
        
        self.base_url = "https://api.stability.ai"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def _make_request(self, 
                     method: str, 
                     endpoint: str, 
                     data: Optional[Dict[str, Any]] = None,
                     files: Optional[Dict[str, Any]] = None,
                     headers: Optional[Dict[str, str]] = None) -> requests.Response:
        """
        API リクエストを実行
        
        Parameters:
        -----------
        method : str
            HTTPメソッド ('GET', 'POST' etc.)
        endpoint : str
            APIエンドポイント
        data : dict, optional
            リクエストボディ
        files : dict, optional 
            アップロードするファイル
        headers : dict, optional
            追加のヘッダー
            
        Returns:
        --------
        requests.Response
            APIレスポンス
        """
        url = f"{self.base_url}{endpoint}"
        request_headers = {
            "Authorization": f"Bearer {self.api_key}",
        }
        
        if headers:
            # Content-Typeヘッダーは削除（requestsが自動的に設定）
            if "Content-Type" in headers:
                del headers["Content-Type"]
            request_headers.update(headers)
            
        # リクエストを実行
        response = requests.request(
            method=method,
            url=url,
            data=data,
            files=files,
            headers=request_headers
        )
            
        if response.status_code not in [200, 202]:
            raise Exception(f"API request failed with status {response.status_code}: {response.text}")
            
        return response

    def tensor_to_pil(self, image: torch.Tensor) -> Image.Image:
        """
        PyTorch tensor をPIL画像に変換
        
        Parameters:
        -----------
        image : torch.Tensor
            変換する画像テンソル [H,W,C]
            
        Returns:
        --------
        PIL.Image
            変換されたPIL画像
        """
        # テンソルをnumpy配列に変換
        if image.ndim == 4:
            image = image.squeeze(0)  # バッチ次元を削除
        
        img_array = (image.cpu().numpy() * 255).astype(np.uint8)
        
        # PILイメージに変換
        pil_image = Image.fromarray(img_array)
        return pil_image

    def pil_to_tensor(self, image: Image.Image) -> torch.Tensor:
        """
        PIL画像をPyTorch tensorに変換
        
        Parameters:
        -----------
        image : PIL.Image
            変換するPIL画像
            
        Returns:
        --------
        torch.Tensor
            変換された画像テンソル [H,W,C]
        """
        # PIL画像をnumpy配列に変換
        img_array = np.array(image).astype(np.float32) / 255.0
        
        # numpyからPyTorchテンソルに変換
        img_tensor = torch.from_numpy(img_array)
        
        return img_tensor

    def image_to_bytes(self, image: Union[torch.Tensor, Image.Image], format: str = 'PNG') -> bytes:
        """
        画像をバイト列に変換
        
        Parameters:
        -----------
        image : Union[torch.Tensor, Image.Image]
            変換する画像(PyTorchテンソルまたはPIL画像)
        format : str
            出力フォーマット('PNG', 'JPEG', 'WEBP')
            
        Returns:
        --------
        bytes
            画像のバイト列
        """
        if isinstance(image, torch.Tensor):
            image = self.tensor_to_pil(image)
            
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format=format)
        return img_byte_arr.getvalue()

    def bytes_to_tensor(self, image_bytes: bytes) -> torch.Tensor:
        """
        バイト列から画像テンソルに変換
        
        Parameters:
        -----------
        image_bytes : bytes
            画像のバイト列
            
        Returns:
        --------
        torch.Tensor
            変換された画像テンソル [B,H,W,C] 形式
            B: バッチサイズ (1)
            H: 高さ
            W: 幅
            C: チャンネル数 (3: RGB)
            値の範囲は0-1のfloat32型
        """
        # バイト列からPIL画像を作成
        image = Image.open(io.BytesIO(image_bytes))
        
        # RGB形式に変換
        if image.mode != 'RGB':
            image = image.convert('RGB')
            
        # 画像サイズを確認
        width, height = image.size
        print(f"Image size: {width}x{height}")
        
        # PIL画像をnumpy配列に変換し、0-1の範囲に正規化
        img_array = np.array(image).astype(np.float32) / 255.0
        
        # バッチ次元を追加 [B,H,W,C]
        img_tensor = torch.from_numpy(img_array)
        img_tensor = img_tensor.unsqueeze(0)  # (1, H, W, C)
        
        # メモリリークを防ぐためにPIL画像を明示的に閉じる
        image.close()
        
        print(f"Tensor shape: {img_tensor.shape}, dtype: {img_tensor.dtype}")  # デバッグ情報
        return img_tensor

    def check_balance(self) -> float:
        """
        アカウントの残高を確認
        
        Returns:
        --------
        float
            利用可能なクレジット残高
        """
        response = self._make_request('GET', '/v1/user/balance')
        return response.json()['credits']