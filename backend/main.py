from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from recommendation import load_rules,get_recommend,get_general_recommendations,get_recommendations
from data_preprocessor import DataPreprocessor
from sasrec_model import SASRec
import pandas as pd
import pickle
import torch

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://streamlit-recommender.onrender.com",  
        "http://localhost:8501",  
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

sasrec_model = None
preprocessor = None
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

order_info = pd.read_csv("order_info.csv")
order_line = pd.read_csv("order_line.csv")
merged_df = pd.merge(order_info, order_line, on="Order ID", how="inner")

@app.get("/")
@app.head("/")
def root():
    return {"message": "FastAPI backend is running", "status": "OK"}


@app.on_event("startup")
def load_model():
    try:
        global sasrec_model, preprocessor

        num_users = 992
        num_items = 199
        print("Starting model loading...")
        sasrec_model = SASRec(num_users=num_users,num_items=num_items,hidden_size=64,num_blocks=2,num_heads=1,dropout_rate=0.5,max_seq_len=50).to(device)
        sasrec_model.load_state_dict(torch.load("sasrec_weights.pth", map_location=device))
        sasrec_model.eval()

        with open("preprocessor.pkl", "rb") as f:
            preprocessor = pickle.load(f)

        print("SASRec model and preprocessor loaded.")
    except Exception as e:
        print(f"Error loading model: {e}")

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "FastAPI Recommender Backend"}


@app.get("/recommend/apriori/{customer_id}")
def recommend(customer_id: str, min_support: float = Query(...)):
    

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

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "FastAPI Recommender Backend"}

@app.get("/recommend/sasrec/{customer_id}")
def recommend_sasrec(customer_id: str):
    global sasrec_model, preprocessor
    id_exists = customer_id in merged_df['Customer ID'].values
    
    if id_exists:
        category_map_recommended = {}
        category_map_bought = {}

        
        customer_data = merged_df[merged_df["Customer ID"] == customer_id].copy()
        customer_data = customer_data.sort_values("Date")

        
        customer_products = customer_data["Product ID"].unique().tolist()

       
        for product in customer_products:
            category = customer_data[customer_data["Product ID"] == product]["Category"].head(1).item()
            category_map_bought.setdefault(category, []).append(product)

    
        try:
            item_sequence = preprocessor.item_encoder.transform(customer_products) + 1
            item_sequence = item_sequence.tolist()
        except ValueError:
            return {"message": "No known product history for customer"}

        recommendations = get_recommendations(sasrec_model, item_sequence, preprocessor.item_encoder, device, top_k=10)

        for product in recommendations:
            category = merged_df[merged_df["Product ID"] == product]["Category"].head(1).item()
            category_map_recommended.setdefault(category, []).append(product)

        return {"customer_id": customer_id,"Products_bought": list(customer_products),"Category_bought": category_map_bought,"recommended_product": recommendations,"Category_recommend": category_map_recommended}
    
    else:
        category_map_generic = {}
        top_items = merged_df["Product ID"].value_counts().head(10).index.tolist()
        # Group generic recommendations by category
        
        for product in top_items:
            category = merged_df[merged_df["Product ID"] == product]["Category"].head(1).item()
            category_map_generic.setdefault(category, []).append(product)

        return {
            "customer_id": customer_id,
            "generic_product": top_items,
            "Category_recommend": category_map_generic,
            "message": "No purchase history — showing generic recommendations."
        }

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "FastAPI Recommender Backend"}



