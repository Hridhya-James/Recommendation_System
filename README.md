# 🛒 Product Recommendation System (FastAPI)

This project is a simple recommendation system built with **FastAPI**. It recommends products based on customer purchase history using association rule mining (Apriori algorithm).

## 🚀 Features

- Recommends products using historical purchase patterns
- Built with FastAPI for API serving
- Rules generated using mlxtend’s Apriori algorithm
- CSV-based input (order_line.csv)
- Lightweight and easy to run locally

## 📦 Installation

### Option 1: Using `uv` (recommended for speed)
```bash
uv pip install -r requirements.txt

### Option 2: Using pip 

pip install -r requirements.txt

## Running the Server

uvicorn main:app --reload

