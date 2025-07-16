import torch
import torch.nn as nn

class SASRec(nn.Module):
    def __init__(self, num_users, num_items, hidden_size=64, num_blocks=2, num_heads=1, 
                 dropout_rate=0.5, max_seq_len=50):
        super(SASRec, self).__init__()
        
        self.num_users = num_users
        self.num_items = num_items
        self.hidden_size = hidden_size
        self.max_seq_len = max_seq_len
        
        
        self.item_embedding = nn.Embedding(num_items + 1, hidden_size, padding_idx=0)
        self.position_embedding = nn.Embedding(max_seq_len, hidden_size)
        
        
        self.attention_blocks = nn.ModuleList([
            nn.TransformerEncoderLayer(
                d_model=hidden_size,
                nhead=num_heads,
                dim_feedforward=hidden_size * 4,
                dropout=dropout_rate,
                activation='relu'
            ) for _ in range(num_blocks)
        ])
        
        
        self.layer_norm = nn.LayerNorm(hidden_size)
        
        
        self.dropout = nn.Dropout(dropout_rate)
        
        
        self.apply(self._init_weights)
        
    def _init_weights(self, module):
        if isinstance(module, nn.Embedding):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)
        elif isinstance(module, nn.Linear):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if module.bias is not None:
                nn.init.zeros_(module.bias)
        elif isinstance(module, nn.LayerNorm):
            nn.init.zeros_(module.bias)
            nn.init.ones_(module.weight)
    
    def forward(self, input_seq):
        batch_size, seq_len = input_seq.size()
        
        positions = torch.arange(seq_len, device=input_seq.device).unsqueeze(0).repeat(batch_size, 1)
        
        
        item_emb = self.item_embedding(input_seq)
        pos_emb = self.position_embedding(positions)
        
        
        x = item_emb + pos_emb
        x = self.dropout(x)
        
        
        attention_mask = (input_seq != 0).float()
        
        
        x = x.transpose(0, 1)  
        for block in self.attention_blocks:
            x = block(x, src_key_padding_mask=(attention_mask == 0))
        
        x = x.transpose(0, 1) 
        x = self.layer_norm(x)
        
       
        last_positions = attention_mask.sum(dim=1).long() - 1
        last_positions = last_positions.clamp(min=0)
        
        
        last_hidden = x[torch.arange(batch_size), last_positions]
        
        item_embeddings = self.item_embedding.weight[1:]  
        scores = torch.matmul(last_hidden, item_embeddings.transpose(0, 1))
        
        return scores