import os
import configparser
from typing import Optional

class ConfigManager:
    """設定ファイルを管理するクラス"""
    
    _instance = None
    
    def __new__(cls):
        """シングルトンパターンの実装"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """初期化（シングルトンなので1回だけ実行）"""
        if self._initialized:
            return
            
        self._initialized = True
        self.config = configparser.ConfigParser()
        self.config_path = os.path.join(os.path.dirname(__file__), "config.ini")
        
        # 設定ファイルが存在しない場合は作成
        if not os.path.exists(self.config_path):
            self.config["stability"] = {
                "api_key": "your_api_key_here"
            }
            with open(self.config_path, "w") as f:
                self.config.write(f)
        
        # 設定ファイルを読み込み
        self.config.read(self.config_path)
    
    def get_api_key(self) -> Optional[str]:
        """Stability API Keyを取得"""
        try:
            # 環境変数が設定されている場合はそちらを優先
            env_key = os.getenv("STABILITY_API_KEY")
            if env_key:
                return env_key
                
            # config.iniからAPIキーを取得
            return self.config.get("stability", "api_key")
        except:
            return None
    
    def set_api_key(self, api_key: str) -> None:
        """Stability API Keyを設定"""
        if not self.config.has_section("stability"):
            self.config.add_section("stability")
        
        self.config.set("stability", "api_key", api_key)
        
        with open(self.config_path, "w") as f:
            self.config.write(f)