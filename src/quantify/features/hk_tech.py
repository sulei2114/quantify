import pandas as pd
import requests
import time
from typing import List, Optional

# 恒生科技指数成分股代码列表 (截至 2024年底)
HSTECH_CODES = [
    "00700", "03690", "09988", "01810", "09618", "01211", "00981", "02015",
    "09999", "01024", "09888", "09961", "00992", "06690", "02382", "00268",
    "00285", "03888", "00241", "09868", "09866", "09626", "00772", "00020",
    "01347", "00763", "00300", "02013", "00522", "00136", "00780"
]

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/119.0.0.0 Safari/537.36"
    ),
    "Referer": "https://tool.stockstar.com/",
}

def get_stock_name(code: str) -> Optional[str]:
    """通过腾讯接口获取股票名称"""
    try:
        url = f"http://qt.gtimg.cn/q=hk{code}"
        resp = requests.get(url, headers=DEFAULT_HEADERS, timeout=5)
        if resp.status_code == 200:
            # v_hk00700="100~腾讯控股~00700...
            content = resp.text
            if "=" in content:
                data = content.split('="')[1]
                parts = data.split('~')
                if len(parts) > 2:
                    return parts[1]
    except Exception as e:
        print(f"Error fetching {code}: {e}")
    return None

def fetch_hk_tech_stocks(csv_path: str = "hk_teck.csv") -> pd.DataFrame:
    """
    获取恒生科技指数成分股并保存为 CSV。
    使用硬编码列表 + 腾讯接口匹配名称。
    """
    print(f"正在获取 {len(HSTECH_CODES)} 只股票的名称...")
    
    data = []
    for code in HSTECH_CODES:
        name = get_stock_name(code)
        if name:
            data.append({"股票代码": code, "股票名称": name})
            print(f"已获取: {code} - {name}")
        else:
            print(f"未获取到名称: {code}")
        time.sleep(0.1) # 避免请求过快
        
    df = pd.DataFrame(data)
    
    if not df.empty and csv_path:
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        print(f"已保存 {len(df)} 条数据至 {csv_path}")
        
    return df

if __name__ == "__main__":
    fetch_hk_tech_stocks()
