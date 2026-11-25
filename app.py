
import streamlit as st
import json
import os
from datetime import datetime

st.set_page_config(
    page_title="ShopPulse",
    page_icon="📊",
    layout="wide"
)

DATA_FILE = "shoppulse_data.json"


def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as file:
                data = json.load(file)
                return data.get("products", {}), data.get("sales", [])
        except (json.JSONDecodeError, OSError):
            pass
    return {}, []


def save_data():
    with open(DATA_FILE, "w") as file:
        json.dump({
            "products": st.session_state.products,
            "sales": st.session_state.sales
        }, file, indent=4)


if "products" not in st.session_state:
    products, sales = load_data()
    st.session_state.products = products
    st.session_state.sales = sales


products = st.session_state.products
sales = st.session_state.sales

st.title("📊 ShopPulse")
st.subheader("Smart Business Management")
st.caption("Manage your products, inventory, sales and profits.")

st.sidebar.title("ShopPulse Menu")

menu = st.sidebar.radio(
    "Navigate",
    [
        "Dashboard",
        "Add Product",
        "Inventory",
        "Record Sale",
        "Restock",
        "Sales History"
    ]
)

if menu == "Dashboard":
    st.header("📈 Business Dashboard")

    revenue = sum(s["revenue"] for s in sales)
    profit = sum(s["profit"] for s in sales)
    stock_count = sum(p["stock"] for p in products.values())

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Products", len(products))
    col2.metric("Items in Stock", stock_count)
    col3.metric("Total Revenue", f"₦{revenue:,.2f}")
    col4.metric("Total Profit", f"₦{profit:,.2f}")

    st.divider()
    st.subheader("Recent Sales")

    if sales:
        for sale in reversed(sales[-5:]):
            st.write(
                f"**{sale['product']}** | "
                f"Quantity: {sale['quantity']} | "
                f"Revenue: ₦{sale['revenue']:,.2f}"
            )
    else:
        st.info("No sales recorded yet.")


elif menu == "Add Product":
    st.header("➕ Add New Product")

    with st.form("add_product"):
        name = st.text_input("Product name")
        buying = st.number_input(
            "Buying price (₦)", min_value=0.0
        )
        selling = st.number_input(
            "Selling price (₦)", min_value=0.0
        )
        quantity = st.number_input(
            "Opening stock", min_value=0, step=1
        )

        submitted = st.form_submit_button("Save Product")

        if submitted:
            key = name.strip().lower()

            if not key:
                st.error("Please enter a product name.")
            elif buying <= 0 or selling <= 0:
                st.error("Prices must be greater than zero.")
            elif quantity <= 0:
                st.error("Opening stock must be greater than zero.")
            elif key in products:
                st.error("This product already exists.")
            else:
                products[key] = {
                    "name": name.strip(),
                    "buying_price": buying,
                    "selling_price": selling,
                    "stock": quantity
                }
                save_data()
                st.success("Product added successfully!")


elif menu == "Inventory":
    st.header("📦 Product Inventory")

    if products:
        for key, p in products.items():
            with st.container(border=True):
                st.subheader(p["name"])
                col1, col2, col3 = st.columns(3)
                col1.write(f"Buying: ₦{p['buying_price']:,.2f}")
                col2.write(f"Selling: ₦{p['selling_price']:,.2f}")
                col3.write(f"Stock: {p['stock']}")
    else:
        st.info("Your inventory is empty. Add a product first.")


elif menu == "Record Sale":
    st.header("💰 Record a Sale")

    if products:
        with st.form("record_sale"):
            selected = st.selectbox(
                "Select product",
                list(products.keys()),
                format_func=lambda x: products[x]["name"]
            )

            quantity = st.number_input(
                "Quantity sold", min_value=1, step=1
            )

            submitted = st.form_submit_button("Complete Sale")

            if submitted:
                product = products[selected]

                if quantity > product["stock"]:
                    st.error("Not enough stock available.")
                else:
                    revenue = product["selling_price"] * quantity
                    cost = product["buying_price"] * quantity
                    profit = revenue - cost

                    product["stock"] -= quantity

                    sales.append({
                        "product": product["name"],
                        "quantity": quantity,
                        "revenue": revenue,
                        "profit": profit,
                        "date": datetime.now().strftime(
                            "%Y-%m-%d %H:%M:%S"
                        )
                    })

                    save_data()

                    st.success("Sale recorded successfully!")
                    st.metric("Revenue", f"₦{revenue:,.2f}")
                    st.metric("Profit", f"₦{profit:,.2f}")
    else:
        st.info("Add a product before recording sales.")


elif menu == "Restock":
    st.header("📥 Restock Inventory")

    if products:
        with st.form("restock"):
            selected = st.selectbox(
                "Select product",
                list(products.keys()),
                format_func=lambda x: products[x]["name"]
            )

            quantity = st.number_input(
                "Quantity to add", min_value=1, step=1
            )

            submitted = st.form_submit_button("Update Stock")

            if submitted:
                products[selected]["stock"] += quantity
                save_data()
                st.success("Stock updated successfully!")
    else:
        st.info("No products available to restock.")


elif menu == "Sales History":
    st.header("📋 Sales History")

    if sales:
        for sale in reversed(sales):
            with st.container(border=True):
                st.write(f"**{sale['product']}**")
                st.write(f"Date: {sale['date']}")
                st.write(f"Quantity: {sale['quantity']}")
                st.write(f"Revenue: ₦{sale['revenue']:,.2f}")
                st.write(f"Profit: ₦{sale['profit']:,.2f}")
    else:
        st.info("No sales recorded yet.")


st.divider()
st.caption("ShopPulse © 2026 | Built for smarter businesses.")
