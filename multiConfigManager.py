import json
from typing import Dict, Any, Optional
import threading



class Config:
    """配置实体类，包含所有指定的固定配置字段"""
    
    def __init__(self, 
                 five_min_open_flag: bool = False,
                 five_min_volume_flag: bool = False,
                 target_object_price_1: float = 0,
                 target_object_price_2: float = 0,
                 gobal_box_period: int = 12,
                 box_low: float = 0,
                 box_high: float = 0,
                 open_volum: float = 0.1,
                 close_points: float = 4.0,
                 forecast_open: float = 0,
                 forecast_close: float = 0,
                 nomal_boder_length: float = 0,
                 min_box_size: float = 3,
                 sys_: bool = False,
):
        """
        初始化配置实体，包含所有指定字段及默认值
        """
        self.FIVE_MIN_OPEN_FLAG = five_min_open_flag
        self.FIVE_MIN_VOLUME_FLAG = five_min_volume_flag
        self.TARGET_OBJECT_PRICE_1 = target_object_price_1
        self.TARGET_OBJECT_PRICE_2 = target_object_price_2
        self.GOBAL_BOX_PERIOD = gobal_box_period  
        self.BOX_LOW = box_low
        self.BOX_HIGH = box_high
        self.OPEN_VOLUM = open_volum
        self.CLOSE_POINTS = close_points
        self.FORECAST_OPEN = forecast_open
        self.FORECAST_CLOSE = forecast_close
        self.NOMAL_BORDER_LENGTH = nomal_boder_length
        self.MIN_BOX_SIZE = min_box_size
    
    def to_dict(self) -> Dict[str, Any]:
        """将配置转换为字典，用于序列化"""
        return {
            "FIVE_MIN_OPEN_FLAG": self.FIVE_MIN_OPEN_FLAG,
            "FIVE_MIN_VOLUME_FLAG": self.FIVE_MIN_VOLUME_FLAG,
            "TARGET_OBJECT_PRICE_1": self.TARGET_OBJECT_PRICE_1,
            "TARGET_OBJECT_PRICE_2": self.TARGET_OBJECT_PRICE_2,
            "GOBAL_BOX_PERIOD": self.GOBAL_BOX_PERIOD,
            "BOX_LOW": self.BOX_LOW,
            "BOX_HIGH": self.BOX_HIGH,
            "OPEN_VOLUM": self.OPEN_VOLUM,
            "CLOSE_POINTS": self.CLOSE_POINTS,
            "FORECAST_OPEN": self.FORECAST_OPEN,
            "FORECAST_CLOSE": self.FORECAST_CLOSE,
            "NOMAL_BORDER_LENGTH": self.NOMAL_BORDER_LENGTH,
            "MIN_BOX_SIZE": self.MIN_BOX_SIZE
        }
        
    def reinit(self):
        self.TARGET_OBJECT_PRICE_1 = 0
        self.TARGET_OBJECT_PRICE_2 = 0
        self.BOX_LOW = 0
        self.BOX_HIGH = 0
        self.FIVE_MIN_OPEN_FLAG,self.FIVE_MIN_VOLUME_FLAG = False,False 
        return self
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Config':
        """从字典创建配置实体，用于反序列化"""
        return cls(
            five_min_open_flag=data.get("FIVE_MIN_OPEN_FLAG", False),
            five_min_volume_flag=data.get("FIVE_MIN_VOLUME_FLAG", False),
            target_object_price_1=data.get("TARGET_OBJECT_PRICE_1", 0),
            target_object_price_2=data.get("TARGET_OBJECT_PRICE_2", 0),
            gobal_box_period=data.get("GOBAL_BOX_PERIOD", 12),
            box_low=data.get("BOX_LOW", 0),
            box_high=data.get("BOX_HIGH", 0),
            open_volum=data.get("OPEN_VOLUM", 0.1),
            close_points=data.get("CLOSE_POINTS", 4.0),
            forecast_open=data.get("FORECAST_OPEN", 0),
            forecast_close=data.get("FORECAST_CLOSE", 0),
            nomal_boder_length=data.get("NOMAL_BORDER_LENGTH", 0),
            min_box_size=data.get("MIN_BOX_SIZE", 3)
        )


class ConfigManager:
    """配置管理器，用于根据key管理多个Config实例并提供持久化功能"""
    
    def __init__(self,filePath: str):
        """初始化配置管理器，创建空的配置字典"""
        self.configs: Dict[str, Config] = {}  # 用字典存储多个配置，key为配置标识
        self.filePath = filePath
        self._lock = threading.RLock()  # Add reentrant lock for thread safety

    
    def add_config(self, config_key: str, config: Config) -> None:
        """添加一个配置实例"""
        with self._lock:
            self.configs[config_key] = config
            self.save_to_file()
    
    def get_config(self, config_key: str) -> Optional[Config]:
        """根据key获取配置实例"""
        return self.configs.get(config_key)
    
    def update_config(self, config_key: str, **kwargs) -> bool:
        """更新指定key的配置字段"""
        with self._lock:
            if config_key not in self.configs:
                return False
                
            # 所有有效的配置字段
            valid_fields = [
                "FIVE_MIN_OPEN_FLAG", 
                "FIVE_MIN_VOLUME_FLAG",
                "TARGET_OBJECT_PRICE_1",
                "TARGET_OBJECT_PRICE_2",
                "GOBAL_BOX_PERIOD",
                "BOX_LOW",
                "BOX_HIGH",
                "OPEN_VOLUM",
                "CLOSE_POINTS"
            ]
            
            config = self.configs[config_key]
            
            for key, value in kwargs.items():
                if key in valid_fields and hasattr(config, key):
                    setattr(config, key, value)
            self.save_to_file()
        return True
    
    def delete_config(self, config_key: str) -> bool:
        with self._lock:
            """删除指定key的配置"""
            if config_key in self.configs:
                del self.configs[config_key]
                self.save_to_file()
                return True
            return False
    
    def save_to_file(self) -> bool:
        """将所有配置保存到文件"""
        try:
            config_data = {}
            for key, config in self.configs.items():
                config_dict = config.to_dict()
                # Ensure all values are JSON serializable
                serialized_config = {}
                for k, v in config_dict.items():
                    # Convert numpy types to native Python types
                    if hasattr(v, 'item'):  # numpy scalar types have .item() method
                        serialized_config[k] = v.item()
                    elif isinstance(v, bool):  # Ensure it's a standard Python bool
                        serialized_config[k] = bool(v)
                    elif isinstance(v, (int, float, str)) or v is None:
                        serialized_config[k] = v
                    else:
                        # Convert any other type to string representation
                        serialized_config[k] = v
                config_data[key] = serialized_config
            
            with open(self.filePath, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存配置失败: {str(e)}")
            return False
    
    def load_from_file(self) -> bool:
        """从文件加载所有配置"""
        try:
            with open(self.filePath, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            self.configs.clear()
            
            for key, data in config_data.items():
                self.configs[key] = Config.from_dict(data)
            
            return True
        except FileNotFoundError:
            print(f"配置文件不存在: {self.filePath}，将使用空配置")
            return False
        except Exception as e:
            print(f"加载配置失败: {str(e)}，将使用空配置")
            return False
        
    def get_configFromFile(self, config_key: str) -> Optional[Config]:
        """根据key获取配置实例"""
        self.load_from_file()
        return self.configs.get(config_key)