from __future__ import annotations

import re
from typing import Optional, Dict

import pandas as pd
import requests
from bs4 import BeautifulSoup


DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/119.0.0.0 Safari/537.36"
    ),
    "Referer": "https://tool.stockstar.com/",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}


def print_a_stock_without_st(
    csv_path: str = "a_stock_list.csv",
    keyword: Optional[str] = None,
    print_output: bool = True,
) -> pd.DataFrame:
    """返回剔除 ST 后的 A 股列表，可选按名称关键字筛选并打印。"""

    df = pd.read_csv(csv_path, dtype=str)
    mask = ~df["股票名称"].str.contains("ST", case=False, na=False)
    df_filtered = df[mask]

    if keyword:
        df_target = df_filtered[df_filtered["股票名称"].str.contains(keyword, case=False, na=False)].copy()
    else:
        df_target = df_filtered.copy()

    if print_output:
        for _, row in df_target.iterrows():
            print(f"{row['股票代码']},{row['股票名称']}")

    return df_target


def fetch_stock_analysis(stock_code: str = "03690") -> Dict[str, Optional[str]]:
    url = f"https://tool.stockstar.com/access/GZAppraisement/{stock_code}"
    response = requests.get(url, headers=DEFAULT_HEADERS, timeout=10)
    if response.status_code != 200:
        raise RuntimeError(
            f"请求失败，状态码 {response.status_code}，请检查网络或更新请求头。"
        )
    response.encoding = response.apparent_encoding or response.encoding or "utf-8"
    soup = BeautifulSoup(response.text, "html.parser")
    header_div = soup.select_one(".head_nav div:nth-of-type(2)")
    stock_text = None
    if header_div:
        stock_text = header_div.get_text(strip=True)
        if stock_text.endswith("估值分析"):
            stock_text = stock_text[: -len("估值分析")].strip()
    if not stock_text:
        stock_text = soup.title.string.strip() if soup.title else None

    def extract_metric(label: str) -> Optional[str]:
        target = soup.find(
            lambda tag: tag.name in {"p", "div", "span"}
            and tag.get_text(strip=True).startswith(label)
        )
        if not target:
            return None
        text = target.get_text(separator="", strip=True)
        for sep in ("：", ":"):
            if sep in text:
                return text.split(sep, 1)[1].strip()
        return text.strip()

    return {
        "stock_text": stock_text,
        "analysis": extract_metric("分析结果"),
        "relative_range": extract_metric("相对估值范围"),
        "absolute_range": extract_metric("绝对估值范围"),
        "accuracy": extract_metric("估值准确性"),
    }


def print_info_from_url(
    stock_code: str = "03690",
    analysis_data: Optional[Dict[str, Optional[str]]] = None,
) -> Dict[str, Optional[str]]:
    analysis_data = analysis_data or fetch_stock_analysis(stock_code)
    stock_text = analysis_data.get("stock_text")
    analysis = analysis_data.get("analysis")
    relative_range = analysis_data.get("relative_range")
    absolute_range = analysis_data.get("absolute_range")
    accuracy = analysis_data.get("accuracy")

    print(f"股票：{stock_text or '未找到'}")
    print(f"分析结果：{analysis or '未找到'}")
    print(f"相对估值范围：{relative_range or '未找到'}")
    print(f"绝对估值范围：{absolute_range or '未找到'}")
    print(f"估值准确性：{accuracy or '未找到'} ")
    return analysis_data


def fetch_realtime_price(stock_code: str, timeout: float = 5.0) -> float:
    normalized = stock_code.strip()
    if not normalized.isdigit():
        raise ValueError("股票代码需为数字。")
    
    if len(normalized) == 5:
        prefix = "hk"
    elif len(normalized) == 6:
        prefix = "sh" if normalized.startswith(("5", "6", "9")) else "sz"
    else:
        raise ValueError("股票代码需为 5 位 (港股) 或 6 位 (A股) 数字。")

    url = f"http://qt.gtimg.cn/q={prefix}{normalized}"
    response = requests.get(url, headers=DEFAULT_HEADERS, timeout=timeout)
    if response.status_code != 200:
        raise RuntimeError(f"请求实时行情失败，状态码 {response.status_code}。")
    payload = response.text.strip()
    if "=" not in payload:
        raise ValueError("返回内容异常，未找到行情数据。")
    raw_data = payload.split("=", 1)[1].strip().strip('";')
    if not raw_data:
        raise ValueError("实时行情数据为空。")
    fields = raw_data.split("~")
    if len(fields) <= 3 or not fields[3]:
        raise ValueError("无法解析实时价格。")
    return float(fields[3])


def parse_relative_range(range_text: str) -> Optional[tuple[float, float]]:
    if not range_text:
        return None
    matches = re.findall(r"-?\d+(?:\.\d+)?", range_text)
    if len(matches) < 2:
        return None
    lower, upper = map(float, matches[:2])
    if lower > upper:
        lower, upper = upper, lower
    return lower, upper


def is_price_in_front_half(price: float, range_text: Optional[str]) -> bool:
    parsed = parse_relative_range(range_text) if range_text else None
    if not parsed:
        return False
    lower, upper = parsed
    if lower == upper:
        return price <= lower
    midpoint = lower + (upper - lower) / 2
    return lower <= price <= midpoint


# 示例调用


if __name__ == "__main__":
    byd_df = print_a_stock_without_st(keyword="比亚迪", print_output=False)
    if byd_df.empty:
        raise RuntimeError("未在列表中找到比亚迪的股票代码。")
    byd_code = byd_df.iloc[0]["股票代码"]
    try:
        current_price = fetch_realtime_price(byd_code)
        analysis_data = fetch_stock_analysis(byd_code)
        # if not is_price_in_front_half(current_price, analysis_data.get("relative_range")):
        #     print("比亚迪当前股价未处于相对估值范围前 50%。")
        # else:
        print("==================")
        print(f"股票代码：{byd_code}")
        print(f"当前股价：{current_price} 元")
        print_info_from_url(stock_code=byd_code, analysis_data=analysis_data)
    except Exception as exc:
        print(f"处理股票 {byd_code} 失败：{exc}")
