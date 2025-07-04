from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori, association_rules
import pandas as pd

def load_rules(merged_df):
    transactions = merged_df.groupby('Order ID')['Product ID'].apply(list).tolist()
    te = TransactionEncoder()
    te_array = te.fit(transactions).transform(transactions)
    df_trans = pd.DataFrame(te_array, columns=te.columns_)

    # Mine frequent itemsets
    frequent_itemsets = apriori(df_trans, min_support=0.002, use_colnames=True)

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