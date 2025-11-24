# 获取A股全部股票代码和名称，并保存为csv
import akshare as ak
import pandas as pd

def fetch_a_stock_list(save_csv_path=None):
	"""
	获取A股全部股票代码和名称，返回DataFrame，并可选保存为csv。
	"""
	df = ak.stock_info_a_code_name()
	# 标准化列名
	df = df.rename(columns={"code": "股票代码", "name": "股票名称"})
	if save_csv_path:
		df.to_csv(save_csv_path, index=False, encoding="utf-8-sig")
	return df

if __name__ == "__main__":
	out_path = "a_stock_list.csv"
	df = fetch_a_stock_list(out_path)
	print(f"已保存 {len(df)} 条A股股票到 {out_path}")
