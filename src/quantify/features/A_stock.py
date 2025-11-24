from __future__ import annotations

from typing import Optional

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


def print_a_stock_without_st(csv_path: str = "a_stock_list.csv") -> None:
    df = pd.read_csv(csv_path, dtype=str)
    mask = ~df["股票名称"].str.contains("ST", case=False, na=False)
    df_filtered = df[mask]
    for _, row in df_filtered.iterrows():
        print(f"{row['股票代码']},{row['股票名称']}")


def print_info_from_url(stock_code: str = "03690") -> None:
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

    analysis = extract_metric("分析结果")
    relative_range = extract_metric("相对估值范围")
    absolute_range = extract_metric("绝对估值范围")
    accuracy = extract_metric("估值准确性")

    print(f"股票：{stock_text or '未找到'}")
    print(f"分析结果：{analysis or '未找到'}")
    print(f"相对估值范围：{relative_range or '未找到'}")
    print(f"绝对估值范围：{absolute_range or '未找到'}")
    print(f"估值准确性：{accuracy or '未找到'}")

# 示例调用


if __name__ == "__main__":
    # print_a_stock_without_st()
    print_info_from_url()
