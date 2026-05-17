from flask import Flask, render_template, request, jsonify
import sqlite3
import database
import pandas as pd
from datetime import date

app = Flask(__name__)
database.create_tables()

def get_db():
    conn = sqlite3.connect("art_gallery.db")
    conn.row_factory = sqlite3.Row
    return conn

# ── HOME ──
@app.route("/")
def home():
    return render_template("home.html")

# ── PRODUCTS ──
@app.route("/products")
def products():
    conn = get_db()
    cursor = conn.cursor()
    keychains = cursor.execute("SELECT * FROM keychains").fetchall()
    aipan = cursor.execute("SELECT * FROM aipan").fetchall()
    conn.close()
    return render_template("products.html", keychains=keychains, aipan=aipan )

# ── SAMPLES ──
@app.route("/samples")
def samples():
    return render_template("samples.html")

# ── CHATBOT ──
YOUR_WHATSAPP = "7455072891"  

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")
    customer_id = data.get("customer_id", None)

    reply = get_bot_reply(user_message)

    conn = get_db()
    cursor = conn.cursor()
    sentiment = "positive" if any(w in user_message.lower() for w in ["like","love","good","great","nice"]) else \
                "negative" if any(w in user_message.lower() for w in ["hate","bad","worst","dislike"]) else "neutral"

    cursor.execute("""
        INSERT INTO chatbot (customer_id, question_asked, response_given, sentiment, date)
        VALUES (?, ?, ?, ?, ?)
    """, (customer_id, user_message, reply, sentiment, date.today()))
    conn.commit()
    conn.close()

    return jsonify({"reply": reply})

def get_bot_reply(message):
    msg = message.lower()
    whatsapp_link = f"https://wa.me/{YOUR_WHATSAPP}"

    if any(w in msg for w in ["hello", "hi", "hey"]):
        return "Hello! Welcome to My World of art and craft🎨 How can I help you today?"
    elif "price" in msg or "cost" in msg or "how much" in msg:
        return "Keychains start from ₹179, aipan from ₹199. Check our Products page for full pricing!"
    elif "keychain" in msg:
        return "We have Wooden (₹99), Acrylic (₹149), Black acrylic (₹199) and hexagonal(₹249) keychains. All handmade!"
    elif "aipan" in msg or "traditional art" in msg:
        return "We have beautifully painted aipan artworks for mandir or pooja"
    elif "order" in msg or "buy" in msg or "purchase" in msg:
        return f"To place an order please contact us on WhatsApp 👇\n{whatsapp_link}"
    elif "available" in msg or "stock" in msg:
        return "Most products are in stock! Check the Products page for current availability."
    elif any(w in msg for w in ["like", "love", "good", "great", "nice", "beautiful"]):
        return "Thank you so much! 😊 Would you like to order? Contact us on WhatsApp 👇\n" + whatsapp_link
    elif any(w in msg for w in ["hate", "bad", "worst", "dislike", "ugly"]):
        return "We are sorry to hear that 😔 Please tell us how we can improve!"
    elif "custom" in msg or "personalize" in msg:
        return f"Yes we do custom orders! Contact us on WhatsApp 👇\n{whatsapp_link}"
    elif "delivery" in msg or "shipping" in msg:
        return f"For delivery details please contact us on WhatsApp 👇\n{whatsapp_link}"
    elif "feedback" in msg or "review" in msg:
        return "We would love your feedback! Click Leave Feedback on the Samples page."
    else:
        return f"I am not sure about that! Please contact us on WhatsApp and we will help you 😊👇\n{whatsapp_link}"

# ── FEEDBACK ──
@app.route("/feedback")
def feedback():
    return render_template("feedback.html")

@app.route("/submit_feedback", methods=["POST"])
def submit_feedback():
    data = request.get_json()
    name       = data.get("name", "")
    age        = data.get("age", "")
    email      = data.get("email", "")
    product_id = data.get("product_id", 1)
    liked      = data.get("liked", True)
    reason     = data.get("reason", "")
    rating     = data.get("rating", 5)

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO customers (name, age, email, visit_date)
        VALUES (?, ?, ?, ?)
    """, (name, age, email, date.today()))
    customer_id = cursor.lastrowid

    cursor.execute("""
        INSERT INTO feedback (customer_id, product_id, liked, reason, rating, date)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (customer_id, product_id, liked, reason, rating, date.today()))
    conn.commit()
    conn.close()

    return jsonify({"message": "Thank you for your feedback!"})

# ── ADMIN DASHBOARD ──
@app.route("/admin")
def admin():
    conn = get_db()
    customers_df = pd.read_sql_query("SELECT * FROM customers", conn)
    feedback_df  = pd.read_sql_query("SELECT * FROM feedback", conn)
    visits_df    = pd.read_sql_query("SELECT * FROM page_visits", conn)
    chatbot_df   = pd.read_sql_query("SELECT * FROM chatbot", conn)
    sales_df     = pd.read_sql_query("SELECT * FROM sales", conn)
    conn.close()

    total_visitors = len(customers_df)

    most_viewed = visits_df['product_viewed'].value_counts().idxmax() \
                  if not visits_df.empty and 'product_viewed' in visits_df.columns \
                  else "No data yet"

    most_sold = sales_df['product_type'].value_counts().idxmax() \
                if not sales_df.empty else "No data yet"

    if not customers_df.empty and 'age' in customers_df.columns:
        customers_df['age'] = pd.to_numeric(customers_df['age'], errors='coerce')
        bins   = [0, 18, 25, 35, 50, 100]
        labels = ['Under 18', '18-25', '26-35', '36-50', '50+']
        customers_df['age_group'] = pd.cut(customers_df['age'], bins=bins, labels=labels)
        age_groups = customers_df['age_group'].value_counts().to_dict()
        age_groups = {str(k): int(v) for k, v in age_groups.items()}
    else:
        age_groups = {}

    sentiment  = chatbot_df['sentiment'].value_counts().to_dict() if not chatbot_df.empty else {}
    avg_rating = feedback_df.groupby('product_id')['rating'].mean().to_dict() if not feedback_df.empty else {}
    avg_rating = {str(k): round(float(v), 1) for k, v in avg_rating.items()}

    liked_count    = int(feedback_df['liked'].sum()) if not feedback_df.empty else 0
    disliked_count = int(len(feedback_df) - liked_count) if not feedback_df.empty else 0

    return render_template("admin.html",
        total_visitors = total_visitors,
        most_viewed    = most_viewed,
        most_sold      = most_sold,
        age_groups     = age_groups,
        sentiment      = sentiment,
        avg_rating     = avg_rating,
        liked_count    = liked_count,
        disliked_count = disliked_count
    )

# ── RUN ──
if __name__ == "__main__":
    app.run(host="0.0.0.0",port=10000)