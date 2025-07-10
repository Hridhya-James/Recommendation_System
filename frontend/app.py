import requests
import streamlit as st

st.title("Recommendation System")

customer_id=st.text_input("Enter the customer ID:")

st.sidebar.header("Apriori Settings")
min_support = st.sidebar.selectbox("Select Minimum Support",options=[0.002,0.0025,0.003,0.0035,0.004],index=1,format_func=lambda x:f"{x:.4f}")


if st.button("Get Recommendation"):
    if customer_id:
        try:
            fastapi_url = f"http://127.0.0.1:8000/recommend/{customer_id}?min_support={min_support}"
            response = requests.get(fastapi_url)

            if response.status_code == 200:
                data = response.json()
                if "message" in data:
                    st.warning(data["message"])
                elif "customer_id" in data:
                    st.write(f"Customer ID: {data['customer_id']}")
                    if "Products_bought" in data:
                        st.subheader("Products that customer already purchased:")

                        # Convert category -> products to product -> category
                        product_to_category = {}
                        for category, products in data['Category_bought'].items():
                            for product in products:
                                product_to_category[product] = category

                        # Group by category
                        category_map = {}
                        for prod in data['Products_bought']:
                            category = product_to_category.get(prod, "unknown")
                            category_map.setdefault(category, []).append(prod)

                        for category, products in category_map.items():
                            st.write(f"{category}: {', '.join(products)}")
                        if data['recommended_product']:
                                st.subheader("Recommended Products:")

    # Build product → category mapping from Category_recommend
                                product_to_category = {}
                                for category, products in data['Category_recommend'].items():
                                    for product in products:
                                        product_to_category[product] = category

                                # Group recommended products by category
                                category_map = {}
                                for prod in data['recommended_product']:
                                    category = product_to_category.get(prod, "unknown")
                                    category_map.setdefault(category, []).append(prod)

                                # Display grouped output
                                for category, products in category_map.items():
                                    st.write(f"{category}: {', '.join(products)}")
                        else:
                            st.warning("No Recommendation for the apriori settings")
                    elif "generic_product" in data:
                        st.subheader("Recommended Products for New Customer:")

                        # Build product → category mapping from Category_recommend
                        product_to_category = {}
                        for category, products in data['Category_recommend'].items():
                            for product in products:
                                product_to_category[product] = category

                        # Group generic products by category
                        category_map = {}
                        for prod in data['generic_product']:  # ✅ use correct key
                            category = product_to_category.get(prod, "unknown")
                            category_map.setdefault(category, []).append(prod)

                        for category, products in category_map.items():
                            st.write(f"{category}: {', '.join(products)}")


                else:
                    st.error("Unexpected response structure.")

            else:
                try:
                    error_response = response.json()
                    if "message" in error_response:
                        st.warning(error_response["message"])
                    elif "error" in error_response:
                        st.error(error_response["error"])
                    else:
                        st.error(f"Error {response.status_code}: {response.text}")
                except Exception:
                    st.error(f"Error {response.status_code}: {response.text}")

        except Exception as e:
            st.error(f"Failed to connect to fastapi : {e}")
    else:
        st.write("Enter Customer ID")

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


