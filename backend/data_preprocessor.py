import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder

class DataPreprocessor:
    def __init__(self, order_info, order_line):
        self.order_info = order_info
        self.order_line = order_line
        
    def preprocess_data(self):
        merged_data = pd.merge(self.order_line, self.order_info, on='Order ID', how='left')
        merged_data['Date'] = pd.to_datetime(merged_data['Date'])
        merged_data = merged_data.sort_values(['Customer ID', 'Date'])

        self.user_encoder = LabelEncoder()
        self.item_encoder = LabelEncoder()

        merged_data['user_id'] = self.user_encoder.fit_transform(merged_data['Customer ID'])
        merged_data['item_id'] = self.item_encoder.fit_transform(merged_data['Product ID']) + 1

        user_sequences = {}
        for customer_id in merged_data['Customer ID'].unique():
            user_data = merged_data[merged_data['Customer ID'] == customer_id]
            sequence = user_data.groupby('Date')['item_id'].apply(list).reset_index()
            items = []
            for item_list in sequence['item_id']:
                items.extend(item_list)
            user_sequences[customer_id] = list(dict.fromkeys(items))

        min_seq_len = 3
        user_sequences = {k: v for k, v in user_sequences.items() if len(v) >= min_seq_len}

        self.customer_to_user = {customer_id: idx for idx, customer_id in enumerate(user_sequences.keys())}
        self.user_to_customer = {idx: customer_id for customer_id, idx in self.customer_to_user.items()}

        user_sequences_internal = {}
        for customer_id, sequence in user_sequences.items():
            user_id = self.customer_to_user[customer_id]
            user_sequences_internal[user_id] = sequence

        self.user_sequences = user_sequences_internal
        self.num_users = len(user_sequences_internal)
        self.num_items = len(self.item_encoder.classes_) + 1

        print(f"Number of users: {self.num_users}")
        print(f"Number of items: {self.num_items}")
        print(f"Average sequence length: {np.mean([len(seq) for seq in user_sequences_internal.values()]):.2f}")

        return user_sequences_internal
