from fastapi import FastAPI
from recommendation import load_rules,get_recommend,get_general_recommendations
import pandas as pd


app = FastAPI()

@app.get("/recommend/{customer_id}")
def recommend(customer_id : str , min_support : float):
    order_line = pd.read_csv('order_line.csv')
    order_info = pd.read_csv("order_info.csv")
    merged_df = pd.merge(order_info, order_line, on='Order ID', how='inner')
    try:
        rules_df = load_rules(merged_df, min_support)
        if rules_df.empty:
            return {"message": f"No association rules found for customer {customer_id} at min_support={min_support}"}

    except Exception as e:
        return {"error": f"Apriori failed: {str(e)}"}

    print(order_line.columns)



    id_exists = customer_id in merged_df['Customer ID'].values

    if id_exists:
        category_map_bought = {}
        category_map_recommended = {}
        customer_products = set(merged_df[merged_df['Customer ID'] == customer_id]['Product ID'])

        for product in customer_products:
            category = merged_df[merged_df['Product ID'] == product]['Category'].head(1).item()
            category_map_bought.setdefault(category, []).append(product)

        print(f"Customer {customer_id} bought: {customer_products}")
        recommended = get_recommend(customer_products,rules_df)
        print(f"Recommended Products for {customer_id}: {recommended}")

        for product in recommended:
            category = merged_df[merged_df['Product ID'] == product]['Category'].head(1).item()
            category_map_recommended.setdefault(category, []).append(product)
        return {"customer_id" : customer_id,"recommended_product" : list(recommended),"Products_bought" : list(customer_products),"Category_bought":category_map_bought,"Category_recommend":category_map_recommended}
    
    else:
        category_map_generic = {}
        generic_recommended = get_general_recommendations(rules_df)

        for product in generic_recommended:
            category = merged_df[merged_df['Product ID'] == product]['Category'].head(1).item()
            category_map_generic.setdefault(category, []).append(product)
        return {"customer_id" : customer_id,"generic_product" : generic_recommended,"Category_recommend":category_map_generic}
