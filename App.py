"""
Fresh Veggies Online Store
A complete, interactive vegetable selling web application built with Streamlit.
All code is contained in this single Python file with no external dependencies
beyond Streamlit itself.

To run:
  1. pip install streamlit
  2. streamlit run app.py
"""

import streamlit as st
from datetime import datetime

# ──────────────────────────────────────────────
# 1. PAGE CONFIGURATION
# Must be the very first Streamlit command.
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="Fresh Veggies Store",
    page_icon="🥕",
    layout="wide",
)

# ──────────────────────────────────────────────
# 2. INVENTORY DATA (in-memory dictionary list)
# Each vegetable has: name, emoji, price, unit,
# stock quantity, description, and category.
# ──────────────────────────────────────────────
VEGETABLES = [
    {
        "name": "Tomato",
        "emoji": "🍅",
        "price": 2.49,
        "unit": "per kg",
        "stock": 50,
        "description": "Vine-ripened, juicy tomatoes perfect for salads and sauces.",
        "category": "Fruit Vegetables",
    },
    {
        "name": "Carrot",
        "emoji": "🥕",
        "price": 1.99,
        "unit": "per kg",
        "stock": 40,
        "description": "Crunchy orange carrots, great for snacking and soups.",
        "category": "Root Vegetables",
    },
    {
        "name": "Broccoli",
        "emoji": "🥦",
        "price": 3.29,
        "unit": "per kg",
        "stock": 25,
        "description": "Fresh green broccoli florets loaded with vitamins.",
        "category": "Cruciferous",
    },
    {
        "name": "Spinach",
        "emoji": "🥬",
        "price": 4.49,
        "unit": "per bunch",
        "stock": 30,
        "description": "Tender baby spinach leaves for salads and smoothies.",
        "category": "Leafy Greens",
    },
    {
        "name": "Bell Pepper",
        "emoji": "🫑",
        "price": 3.99,
        "unit": "per kg",
        "stock": 35,
        "description": "Colorful mixed bell peppers — sweet, crisp, versatile.",
        "category": "Fruit Vegetables",
    },
    {
        "name": "Potato",
        "emoji": "🥔",
        "price": 1.49,
        "unit": "per kg",
        "stock": 80,
        "description": "All-purpose potatoes for baking, mashing, or frying.",
        "category": "Root Vegetables",
    },
    {
        "name": "Onion",
        "emoji": "🧅",
        "price": 1.29,
        "unit": "per kg",
        "stock": 60,
        "description": "Yellow onions — the essential base for every dish.",
        "category": "Bulb Vegetables",
    },
    {
        "name": "Corn",
        "emoji": "🌽",
        "price": 0.99,
        "unit": "per ear",
        "stock": 45,
        "description": "Sweet corn on the cob, perfect for grilling or boiling.",
        "category": "Grain Vegetables",
    },
]

# ──────────────────────────────────────────────
# 3. SESSION STATE INITIALIZATION
# Streamlit reruns the entire script on every
# user interaction. session_state lets us keep
# data (cart, stock, orders) between reruns.
# ──────────────────────────────────────────────

# Shopping cart: dict mapping vegetable name -> quantity
if "cart" not in st.session_state:
    st.session_state.cart = {}

# Live stock tracker: starts as a copy of original stock
if "stock" not in st.session_state:
    st.session_state.stock = {v["name"]: v["stock"] for v in VEGETABLES}

# List of completed orders for this session
if "orders" not in st.session_state:
    st.session_state.orders = []

# Flag that triggers the success banner after checkout
if "order_placed" not in st.session_state:
    st.session_state.order_placed = False


# ──────────────────────────────────────────────
# 4. HELPER FUNCTIONS
# ──────────────────────────────────────────────

def get_veg(name):
    """Return the vegetable dict that matches 'name'."""
    for v in VEGETABLES:
        if v["name"] == name:
            return v
    return {}


def add_to_cart(name, qty):
    """Add qty units of a vegetable to the cart; reduce stock accordingly."""
    if qty <= 0:
        return
    # Never add more than what is available
    available = st.session_state.stock.get(name, 0)
    qty = min(qty, available)
    if qty == 0:
        return
    # Update cart and stock
    st.session_state.cart[name] = st.session_state.cart.get(name, 0) + qty
    st.session_state.stock[name] -= qty


def remove_from_cart(name):
    """Remove a vegetable entirely from the cart; restore its stock."""
    if name in st.session_state.cart:
        returned = st.session_state.cart.pop(name)
        st.session_state.stock[name] += returned


def update_cart_qty(name, new_qty):
    """Set the cart quantity to new_qty, adjusting stock up or down."""
    old_qty = st.session_state.cart.get(name, 0)
    max_possible = old_qty + st.session_state.stock[name]
    new_qty = max(0, min(new_qty, max_possible))
    diff = new_qty - old_qty
    st.session_state.stock[name] -= diff
    if new_qty == 0:
        st.session_state.cart.pop(name, None)
    else:
        st.session_state.cart[name] = new_qty


def get_total():
    """Calculate and return the total price of everything in the cart."""
    total = 0.0
    for name, qty in st.session_state.cart.items():
        total += get_veg(name)["price"] * qty
    return total


def clear_cart():
    """Empty the cart completely and give all stock back."""
    for name, qty in st.session_state.cart.items():
        st.session_state.stock[name] += qty
    st.session_state.cart = {}


# ──────────────────────────────────────────────
# 5. SIDEBAR — CART + CHECKOUT
# ──────────────────────────────────────────────

with st.sidebar:
    st.header("🛒 Shopping Cart")
    st.divider()

    # ── Empty cart message ──
    if not st.session_state.cart:
        st.info("Your cart is empty. Add some veggies from the store!")

    # ── Cart items ──
    else:
        for item_name in list(st.session_state.cart.keys()):
            item_qty = st.session_state.cart[item_name]
            veg = get_veg(item_name)

            # Item header row
            c1, c2 = st.columns([3, 1])
            with c1:
                st.markdown(f"**{veg['emoji']} {item_name}**")
                st.caption(f"${veg['price']:.2f} {veg['unit']}")
            with c2:
                st.markdown(f"**x{item_qty}**")

            # Quantity adjuster + subtotal + remove button
            a1, a2, a3 = st.columns([2, 2, 1])
            with a1:
                max_q = item_qty + st.session_state.stock[item_name]
                new_q = st.number_input(
                    "Qty",
                    min_value=1,
                    max_value=max_q,
                    value=item_qty,
                    key=f"cq_{item_name}",
                    label_visibility="collapsed",
                )
                if new_q != item_qty:
                    update_cart_qty(item_name, new_q)
                    st.rerun()
            with a2:
                st.markdown(f"**${veg['price'] * item_qty:.2f}**")
            with a3:
                if st.button("❌", key=f"rm_{item_name}", help="Remove"):
                    remove_from_cart(item_name)
                    st.rerun()

            st.divider()

        # ── Totals ──
        total = get_total()
        item_count = sum(st.session_state.cart.values())
        st.markdown(f"### Total: **${total:.2f}**")
        st.caption(f"{item_count} item(s) in cart")

        # ── Clear cart ──
        if st.button("🗑️ Clear Cart", use_container_width=True):
            clear_cart()
            st.rerun()

        st.divider()

        # ── Checkout form ──
        st.subheader("📦 Checkout")
        with st.form("checkout_form"):
            cust_name = st.text_input("Full Name *", placeholder="Jane Doe")
            cust_address = st.text_area(
                "Delivery Address *",
                placeholder="123 Green St, Veggie Town",
            )
            payment = st.selectbox(
                "Payment Method",
                ["Cash on Delivery", "Credit Card", "Digital Wallet"],
            )
            submitted = st.form_submit_button(
                "✅ Place Order", use_container_width=True, type="primary"
            )

            if submitted:
                if not cust_name.strip():
                    st.error("Please enter your name.")
                elif not cust_address.strip():
                    st.error("Please enter a delivery address.")
                else:
                    # Save the order
                    order = {
                        "id": len(st.session_state.orders) + 1,
                        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "customer": cust_name.strip(),
                        "address": cust_address.strip(),
                        "payment": payment,
                        "items": dict(st.session_state.cart),
                        "total": total,
                    }
                    st.session_state.orders.append(order)
                    # Empty the cart (stock already reduced)
                    st.session_state.cart = {}
                    st.session_state.order_placed = True
                    st.rerun()

    # ── Order history ──
    if st.session_state.orders:
        st.divider()
        with st.expander(f"📋 Past Orders ({len(st.session_state.orders)})"):
            for o in reversed(st.session_state.orders):
                st.markdown(f"**Order #{o['id']}** — {o['time']}")
                for n, q in o["items"].items():
                    v = get_veg(n)
                    st.markdown(f"&nbsp;&nbsp;{v['emoji']} {n} x{q}")
                st.markdown(f"&nbsp;&nbsp;**Total: ${o['total']:.2f}**")
                st.divider()


# ──────────────────────────────────────────────
# 6. MAIN PAGE — STOREFRONT
# ──────────────────────────────────────────────

# Success banner (shown once after order is placed)
if st.session_state.order_placed:
    last = st.session_state.orders[-1]
    st.balloons()
    st.success(
        f"🎉 **Order #{last['id']} placed!** "
        f"Thank you, **{last['customer']}**! "
        f"Your veggies (${last['total']:.2f}) will be delivered to: "
        f"*{last['address']}*"
    )
    st.session_state.order_placed = False

# Page title
st.title("🥬 Fresh Veggies Online Store")
st.markdown(
    "Browse our **farm-fresh vegetables** below. "
    "Add items to your cart, then check out in the **sidebar →**"
)
st.divider()

# ── Filters ──
f1, f2 = st.columns([2, 3])
with f1:
    categories = sorted(set(v["category"] for v in VEGETABLES))
    sel_cat = st.selectbox("Filter by Category", ["All"] + categories)
with f2:
    search = st.text_input("🔍 Search", placeholder="e.g. tomato")

# Apply filters
shown = VEGETABLES
if sel_cat != "All":
    shown = [v for v in shown if v["category"] == sel_cat]
if search.strip():
    q = search.strip().lower()
    shown = [v for v in shown if q in v["name"].lower() or q in v["description"].lower()]

st.divider()

if not shown:
    st.warning("No vegetables match your search. Try something else!")
else:
    # Display veggies in a 3-column grid
    cols_per_row = 3
    for row in range(0, len(shown), cols_per_row):
        cols = st.columns(cols_per_row)
        for i, col in enumerate(cols):
            vi = row + i
            if vi >= len(shown):
                break
            veg = shown[vi]
            avail = st.session_state.stock[veg["name"]]
            in_cart = st.session_state.cart.get(veg["name"], 0)

            with col:
                with st.container(border=True):
                    st.markdown(f"## {veg['emoji']} {veg['name']}")
                    st.caption(veg["category"])
                    st.write(veg["description"])

                    p1, p2 = st.columns(2)
                    with p1:
                        st.markdown(f"### ${veg['price']:.2f}")
                        st.caption(veg["unit"])
                    with p2:
                        if avail > 5:
                            st.info(f"Stock: {avail}")
                        elif avail > 0:
                            st.warning(f"Only {avail} left!")
                        else:
                            st.error("Sold out")

                    if in_cart > 0:
                        st.success(f"✅ {in_cart} in cart")

                    if avail > 0:
                        qc, bc = st.columns([1, 1])
                        with qc:
                            qty = st.number_input(
                                "Qty",
                                min_value=1,
                                max_value=avail,
                                value=1,
                                key=f"q_{veg['name']}",
                                label_visibility="collapsed",
                            )
                        with bc:
                            if st.button(
                                "🛒 Add",
                                key=f"a_{veg['name']}",
                                use_container_width=True,
                                type="primary",
                            ):
                                add_to_cart(veg["name"], qty)
                                st.rerun()
                    else:
                        st.button(
                            "Sold Out",
                            key=f"so_{veg['name']}",
                            disabled=True,
                            use_container_width=True,
                        )

# ──────────────────────────────────────────────
# 7. FOOTER
# ──────────────────────────────────────────────
st.divider()
st.caption("🥬 Fresh Veggies Store — Built with Streamlit | Demo application, no real transactions.")
