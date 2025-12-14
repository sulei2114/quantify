import sys
import time
import concurrent.futures
import pandas as pd
from datetime import datetime
sys.path.append("../")
from quantify.features.A_stock import print_a_stock_without_st, fetch_realtime_price, fetch_stock_analysis, is_price_in_front_half, print_info_from_url
from quantify.strategies.analysis import check_and_print_if_undervalued, get_filtered_stock_list
from quantify.consts.stack_code import HSTECH_CODES, A_STOCK_CODES

def process_stock(code):
    """处理单个股票：获取数据并分析"""
    try:
        current_price = fetch_realtime_price(code, timeout=10)
        analysis_data = fetch_stock_analysis(code)
        
        # 检查是否被低估（打印操作在函数内部，注意线程安全问题，print通常是线程安全的）
        return check_and_print_if_undervalued(code, current_price, analysis_data)
        
    except Exception as e:
        # 忽略一般错误，避免刷屏
        # print(f"处理 {code} 失败: {e}")
        pass

if __name__ == "__main__":
    stack_market = ["HK","A"]
    stock_list = []
    # 获取待筛选的股票列表
    if stack_market.__contains__("A"):
        stock_list = stock_list + get_filtered_stock_list()
    if stack_market.__contains__("HK"):
        stock_list = stock_list + HSTECH_CODES
    print(f"开始处理 {len(stock_list)} 只股票...")
    if len(stock_list) == 0:
        print("没有找到股票列表，程序结束。")
        return  
    
    # 使用线程池并发处理
    # max_workers 可以根据机器性能调整，设置为 10-20 比较合适
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        # 提交所有任务
        future_to_code = {executor.submit(process_stock, code): code for code in stock_list}
        
        # 获取结果
        for future in concurrent.futures.as_completed(future_to_code):
            try:
                result = future.result()
                if result:
                    results.append(result)
            except Exception as exc:
                # print(f"任务执行异常: {exc}")
                pass
            
    print("扫描完成。")
    
    if results:
        print(f"发现 {len(results)} 只低估股票，正在保存到文件...")
        df = pd.DataFrame(results)
        today_str = datetime.now().strftime('%Y年%m月%d日')
        # 添加日期列
        df['日期'] = today_str
        
        # 调整列顺序，将日期放在第一列
        cols = ['日期'] + [c for c in df.columns if c != '日期']
        df = df[cols]
        
        output_file = f'低估股票{today_str}_{stack_market}.csv'
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"已保存到 {output_file}")
    else:
        print("未发现低估股票。")