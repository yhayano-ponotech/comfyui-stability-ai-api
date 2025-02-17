import torch
from typing import List, Tuple, Dict, Any, Optional
from ..api_client import StabilityAPIClient

class StabilityBaseNode:
    """StabilityAI APIノードの基底クラス"""
    CATEGORY = "Stability AI"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "optional": {
                "api_key": ("STRING", {"multiline": False, "default": ""})
            }
        }

    def __init__(self):
        self.client = None

    def get_client(self, api_key: str = "") -> StabilityAPIClient:
        """APIクライアントを取得
        
        Parameters
        ----------
        api_key : str, optional
            APIキー。指定された場合、このキーを優先的に使用
            
        Returns
        -------
        StabilityAPIClient
            APIクライアントインスタンス
        """
        # APIキーが変更された場合、または初回の場合は新しいクライアントを作成
        if self.client is None or (api_key and api_key != self.client.api_key):
            self.client = StabilityAPIClient(api_key if api_key else None)
        return self.client