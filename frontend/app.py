import requests
import streamlit as st

st.title("Recommendation System")

customer_id=st.text_input("Enter the customer ID:")

st.sidebar.header("Apriori Settings")
min_support = st.sidebar.selectbox("Select Minimum Support",options=[0.001,0.002,0.003,0.004,0.005],index=1,format_func=lambda x:f"{x:.3f}")

if st.button("Get Recommendation"):
    if customer_id:
        try:
            fastapi_url = f"https://fastapi-backend-zdku.onrender.com/recommend/{customer_id}?min_support={min_support}"

            response =requests.get(fastapi_url)

            if response.status_code == 200:
                data = response.json()
                print(data)
                st.write(f"Customer ID:{data['customer_id']}")
                st.subheader(f"Products that customer already purchased:")
                for prod in data['Products bought']:
                    category = data['Category_bought'].get(prod,"unknown")
                    st.write(f" {prod} --- Category : {category}")
                st.subheader("Recommended Products:")
                for products in data['recommended product']:
                    category = data['Category_recommend'].get(products,"unknown")
                    st.write(f" {products} --- Category : {category}")
            else:
                st.error(f"Error {response.status_code}: {response.text}")
        except Exception as e:
            st.error(f"Failed to connect to fastapi : {e}")
        
    else:
        st.write("wrong customer id")
        #customer_products = set(merged_df[merged_df['Customer ID'] == customer_id]['Product ID'])
        #st.write(f"Customer {customer_id} previously purchased:")
        #st.write(", ".join(customer_products))

        #recommended = get_recommend(customer_products,rules_df)

        #if recommended:
        #    st.write("Recommended products are:")
        #    for products in recommended:
        #        st.write(f" {products}")
        #else:
        #    st.write("There is no recommended products")