from typing import Dict, Any, Optional
from quantify.features.A_stock import print_info_from_url
import pandas as pd
def check_and_print_if_undervalued(code: str, current_price: float, analysis_data: Dict[str, Optional[str]]):
    """
    检查分析结果，如果是'股价被低估'，则打印详细信息。
    """
    analysis_text = analysis_data.get("analysis")
    
    # 检查是否包含 "被低估"
    if analysis_text and "被低估" in analysis_text:
        print("==================")
        print(f"股票代码：{code}")
        print(f"当前股价：{current_price} 元")
        
        # 打印详细信息并获取补充数据（如果有变化）
        updated_data = print_info_from_url(stock_code=code, analysis_data=analysis_data)
        
        # 构造返回数据
        result = {
            "股票代码": code,
            "当前股价": current_price,
            "股票名称": updated_data.get("stock_text"), # 假设 analysis_data 或 updated_data 包含名称信息
            "分析结果": analysis_text,
            "相对估值范围": updated_data.get("relative_range"),
            "绝对估值范围": updated_data.get("absolute_range"),
            "估值准确性": updated_data.get("accuracy")
        }
        return result
    
    return None

 


def get_filtered_stock_list(file_path: str = 'a_stock_list.csv') -> list:
    """
    读取a_stock_list.csv文件，过滤所有st，st*的股票，返回股票代码列表
    """
    try:
        df = pd.read_csv(file_path, dtype=str)
        # 过滤掉名字中包含 'ST' 的股票
        filtered_df = df[~df['股票名称'].str.contains('ST', case=False, na=False)]
        return filtered_df['股票代码'].tolist()
    except FileNotFoundError:
        print(f"文件 {file_path} 未找到")
        return []
    except Exception as e:
        print(f"读取股票列表时出错: {e}")
        return []