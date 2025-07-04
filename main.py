from fastapi import FastAPI
from recommendation import load_rules,get_recommend
import pandas as pd


app = FastAPI()

order_line = pd.read_csv('order_line.csv')
order_info = pd.read_csv("order_info.csv")
merged_df = pd.merge(order_info, order_line, on='Order ID', how='inner')
rules_df = load_rules(merged_df)
print(order_line.columns)

@app.get("/recommend/{customer_id}")
def recommend(customer_id : str):
    customer_products = set(merged_df[merged_df['Customer ID'] == customer_id]['Product ID'])
    print(f"Customer {customer_id} bought: {customer_products}")
    recommended = get_recommend(customer_products,rules_df)
    return {"customer_id" : customer_id,"recommended product" : recommended}

