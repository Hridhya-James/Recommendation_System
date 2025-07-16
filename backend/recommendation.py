from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori, association_rules
import pandas as pd
import torch

def load_rules(merged_df,min_support_value=0.002):
    transactions = merged_df.groupby('Order ID')['Product ID'].apply(list).tolist()
    te = TransactionEncoder()
    te_array = te.fit(transactions).transform(transactions)
    df_trans = pd.DataFrame(te_array, columns=te.columns_)

    # Mine frequent itemsets
    frequent_itemsets = apriori(df_trans, min_support=min_support_value, use_colnames=True)

    # Generate association rules
    rules = association_rules(frequent_itemsets, metric="lift", min_threshold=1.0)
    return rules

def get_recommend(customer_product,rules,top_n=3):
    recommend = set()
    for _, rows in rules.iterrows():
        if rows['antecedents'].issubset(customer_product):
            recommend.update(rows['consequents'])
        if len(recommend)>= top_n:
            break
    return list(recommend)[:top_n]

def get_general_recommendations(rules,top_n=3):
    if rules.empty:
        return []
    
    # Get all products from consequents, sorted by confidence
    recommendations = set()
    
    # Sort rules by confidence (higher confidence = better recommendation)
    sorted_rules = rules.sort_values(by='confidence', ascending=False) #confidence :How often the rule is true, given the antecedent is true.()
    
    for _, row in sorted_rules.iterrows():
        recommendations.update(row['consequents'])
        if len(recommendations) >= top_n:
            break
    
    return list(recommendations)[:top_n]

def get_recommendations(model, user_sequence, item_encoder, device, top_k=10):
    model.eval()
    
    max_seq_len = 50
    if len(user_sequence) > max_seq_len:
        padded_seq = user_sequence[-max_seq_len:]
    else:
        padded_seq = [0] * (max_seq_len - len(user_sequence)) + user_sequence

    input_seq = torch.tensor(padded_seq, dtype=torch.long).unsqueeze(0).to(device)
    
    with torch.no_grad():
        outputs = model(input_seq)
        _, top_k_items = torch.topk(outputs, top_k, dim=1)
    
    recommended_items = []
    for item_id in top_k_items[0].cpu().numpy():
        if item_id < len(item_encoder.classes_):  # ✅ safe bound check
            original_item = item_encoder.inverse_transform([item_id])[0]
            recommended_items.append(original_item)
    
    return recommended_items