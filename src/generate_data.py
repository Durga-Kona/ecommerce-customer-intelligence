import random
from pathlib import Path
import numpy as np
import pandas as pd
from .config import RAW

SEED=42
random.seed(SEED); np.random.seed(SEED)
CATEGORIES={'Electronics':['Laptop','Smartphone','Headphones','Keyboard','Mouse','Smartwatch'],
'Clothing':['T-Shirt','Jeans','Jacket','Sneakers','Backpack'],
'Home':['Chair','Desk Lamp','Coffee Maker','Bedsheet','Storage Box'],
'Beauty':['Face Wash','Moisturizer','Shampoo','Perfume'],
'Sports':['Yoga Mat','Running Shoes','Cricket Bat','Water Bottle']}
BRANDS=['Nova','Apex','Zenith','UrbanX','Prime','Orbit']
CITIES={'Andhra Pradesh':['Vijayawada','Visakhapatnam','Guntur','Tirupati'], 'Telangana':['Hyderabad','Warangal','Nizamabad'], 'Karnataka':['Bengaluru','Mysuru'], 'Tamil Nadu':['Chennai','Coimbatore'], 'Maharashtra':['Mumbai','Pune'], 'Delhi':['New Delhi']}
REGION={'Andhra Pradesh':'South','Telangana':'South','Karnataka':'South','Tamil Nadu':'South','Maharashtra':'West','Delhi':'North'}
PAY=['UPI','Credit Card','Debit Card','Net Banking','Cash on Delivery']

def make():
    n_customers,n_products,n_orders=1000,120,6000
    customers=[]
    states=list(CITIES)
    for i in range(1,n_customers+1):
        state=random.choice(states); city=random.choice(CITIES[state]); age=random.randint(18,65)
        customers.append([f'C{i:05d}',f'Customer {i}',random.choice(['Male','Female','Other']),age,city,state,REGION[state]])
    products=[]; pid=1
    for cat,items in CATEGORIES.items():
        for item in items:
            for b in BRANDS[:max(1,min(3,len(items)))]:
                if pid>n_products: break
                price=round(random.uniform(250,85000),2)
                products.append([f'P{pid:04d}',item,b,cat,'General',price,round(price*random.uniform(.12,.35),2)]); pid+=1
            if pid>n_products: break
        if pid>n_products: break
    dates=pd.date_range('2025-01-01','2026-09-30',freq='D')
    orders=[]; items=[]; payments=[]; returns=[]
    for oid in range(1,n_orders+1):
        cid=random.choice(customers)[0]; dt=random.choice(dates); status=random.choices(['Completed','Cancelled'],[.94,.06])[0]
        orders.append([f'O{oid:06d}',cid,dt.date(),status])
        k=random.randint(1,5); chosen=random.sample(products,k=min(k,len(products)))
        for prod in chosen:
            qty=random.randint(1,3); base=prod[5]; disc=round(random.choice([0,.05,.10,.15,.20]),2)
            items.append([f'OI{len(items)+1:08d}',f'O{oid:06d}',prod[0],qty,base,disc])
        payments.append([f'PAY{oid:06d}',f'O{oid:06d}',random.choice(PAY),round(random.uniform(250,100000),2),'Paid' if status=='Completed' else 'Failed'])
        if status=='Completed' and random.random()<.08: returns.append([f'R{len(returns)+1:06d}',f'O{oid:06d}',random.choice(chosen)[0],random.choice(['Damaged','Wrong Item','Changed Mind','Quality']),dt.date()+pd.Timedelta(days=random.randint(1,20))])
    pd.DataFrame(customers,columns=['customer_id','name','gender','age','city','state','region']).to_csv(RAW/'customers.csv',index=False)
    pd.DataFrame(products,columns=['product_id','product_name','brand','category','sub_category','unit_price','unit_cost']).to_csv(RAW/'products.csv',index=False)
    pd.DataFrame(orders,columns=['order_id','customer_id','order_date','status']).to_csv(RAW/'orders.csv',index=False)
    pd.DataFrame(items,columns=['order_item_id','order_id','product_id','quantity','unit_price','discount']).to_csv(RAW/'order_items.csv',index=False)
    pd.DataFrame(payments,columns=['payment_id','order_id','payment_method','amount','payment_status']).to_csv(RAW/'payments.csv',index=False)
    pd.DataFrame(returns,columns=['return_id','order_id','product_id','reason','return_date']).to_csv(RAW/'returns.csv',index=False)
    print(f'Generated {n_customers} customers, {len(products)} products, {n_orders} orders, {len(items)} order lines.')

if __name__=='__main__': make()
