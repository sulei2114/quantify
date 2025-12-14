import akshare as ak
import pandas as pd

try:
    print("Fetching HK indices...")
    df = ak.stock_hk_index_spot_em()
    print("Columns:", df.columns)
    # Search for "Tech" or "Technology" or "HSTECH"
    tech_indices = df[df['名称'].str.contains('科技', na=False) | df['名称'].str.contains('Tech', case=False, na=False)]
    print("\nPotential Tech Indices:")
    print(tech_indices[['代码', '名称']])
    
    if not tech_indices.empty:
        code = tech_indices.iloc[0]['代码']
        name = tech_indices.iloc[0]['名称']
        print(f"\nTrying to fetch components for {name} ({code})...")
        # Try different functions
        try:
            comps = ak.index_stock_cons(symbol=code) # This is usually for A-shares
            print("Found via index_stock_cons:", len(comps))
        except:
            print("index_stock_cons failed.")
            
except Exception as e:
    print(e)
