import akshare as ak
import pandas as pd

target_index = "HSTECH"

print(f"Testing functions for {target_index}...")

# Test 1: stock_hk_index_constituents_em
try:
    print("Trying stock_hk_index_constituents_em...")
    # It might be in a submodule or not exported?
    if hasattr(ak, "stock_hk_index_constituents_em"):
         df = ak.stock_hk_index_constituents_em(symbol=target_index)
         print("Success EM!")
         print(df.head())
    else:
         print("stock_hk_index_constituents_em not found in ak.")
except Exception as e:
    print(f"stock_hk_index_constituents_em failed: {e}")

# Test 2: index_stock_cons_sina
try:
    print("Trying index_stock_cons_sina with various symbols...")
    # Try just "HSTECH" or "hkHSTECH"
    for s in ["HSTECH", "hkHSTECH", "HSI", "hkHSI"]: 
        try:
            df = ak.index_stock_cons_sina(symbol=s)
            print(f"Success Sina ({s})!")
            print(df.head())
        except:
            pass
except Exception as e:
    print(f"index_stock_cons_sina failed: {e}")

# Test 3: Check for similar names
# print([f for f in dir(ak) if "cons" in f])
