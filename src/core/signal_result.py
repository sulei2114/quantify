class SignalResult:
    """
    信号结果类，用于存储策略生成的信号和相关元数据
    """
    
    def __init__(self, signals=None, metadata=None):
        """
        初始化信号结果
        
        Args:
            signals: 信号数据
            metadata: 元数据字典
        """
        self.signals = signals if signals is not None else []
        self.metadata = metadata if metadata is not None else {}
    
    def add_signal(self, signal):
        """
        添加信号到结果中
        
        Args:
            signal: 要添加的信号
        """
        self.signals.append(signal)
    
    def set_metadata(self, key, value):
        """
        设置元数据
        
        Args:
            key: 元数据键
            value: 元数据值
        """
        self.metadata[key] = value
    
    def get_signals(self):
        """
        获取信号列表
        
        Returns:
            list: 信号列表
        """
        return self.signals
    
    def get_metadata(self):
        """
        获取元数据
        
        Returns:
            dict: 元数据字典
        """
        return self.metadata