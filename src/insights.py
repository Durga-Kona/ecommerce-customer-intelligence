from pathlib import Path
import pandas as pd
from .config import OUTPUTS

def run():
    lines=[]
    cat=pd.read_csv(OUTPUTS/'category_sales.csv'); top=cat.iloc[0]; lines.append(f"Top revenue category: {top['category']} with revenue ₹{top['revenue']:,.2f}.")
    prod=pd.read_csv(OUTPUTS/'product_sales.csv'); p=prod.iloc[0]; lines.append(f"Top product by revenue: {p['product_name']} with ₹{p['revenue']:,.2f}.")
    reg=pd.read_csv(OUTPUTS/'region_sales.csv'); r=reg.iloc[0]; lines.append(f"Top location: {r['city']}, {r['state']} with revenue ₹{r['revenue']:,.2f}.")
    seg=pd.read_csv(OUTPUTS/'customer_segments.csv'); lines.append(f"Premium customers: {(seg.segment=='Premium').sum()} ({(seg.segment=='Premium').mean()*100:.1f}% of mined customers).")
    rules=pd.read_csv(OUTPUTS/'association_rules.csv');
    if len(rules): lines.append(f"Strongest product association: {rules.iloc[0].antecedents} -> {rules.iloc[0].consequents} (confidence {rules.iloc[0].confidence:.1%}, lift {rules.iloc[0].lift:.2f}).")
    Path(OUTPUTS/'business_insights.txt').write_text('\n'.join('- '+x for x in lines),encoding='utf8'); print('\n'.join(lines))
if __name__=='__main__': run()
