from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori, association_rules
import pandas as pd

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
    sorted_rules = rules.sort_values(by='confidence', ascending=False)
    
    for _, row in sorted_rules.iterrows():
        recommendations.update(row['consequents'])
        if len(recommendations) >= top_n:
            break
    
    return list(recommendations)[:top_n]