import os
import sqlite3
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters
)

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = {
    int(x.strip()) for x in os.getenv("ADMIN_IDS", "6180671831").split(",")
    if x.strip().isdigit()
}
DB_PATH = os.getenv("DB_PATH", "orders.db")

# Add real payment details later through Render Environment Variables.
PAYMENT_DETAILS = {
    "binance_pay": os.getenv("BINANCE_PAY_ID", ""),
    "binance_bep20": os.getenv("BINANCE_BEP20", ""),
    "bybit_pay": os.getenv("BYBIT_PAY_ID", ""),
    "bybit_bep20": os.getenv("BYBIT_BEP20", ""),
}

PRODUCTS = {
    "10k": ("10K PP", 1.00),
    "20k": ("20K PP", 2.00),
    "30k": ("30K PP", 3.00),
    "40k": ("40K PP", 4.00),
    "50k": ("50K PP", 5.00),
    "60k": ("60K PP", 6.00),
    "70k": ("70K PP", 7.00),
    "80k": ("80K PP", 8.00),
    "90k": ("90K PP", 9.00),
    "100k": ("100K PP", 10.00),
    "200k": ("200K PP", 20.00),
    "300k": ("300K PP", 30.00),
    "400k": ("400K PP", 40.00),
    "500k": ("500K PP", 50.00),
    "1m": ("1M PP", 100.00),
    "animation": ("50K Animation Card", 6.00),
    "helicopter": ("125K Popularity Helicopter", 15.00),
}
UC_PRODUCTS = {"60uc": ("60 UC", 1.00)}

PAYMENT_NAMES = {
    "binance_pay": "Binance Pay ID",
    "binance_bep20": "Binance USDT BEP20",
    "bybit_pay": "Bybit Pay",
    "bybit_bep20": "Bybit USDT BEP20",
}

TEXT = {
    "en": {
        "choose_lang": "🌐 Please select your language:",
        "welcome": "🎮 ELITE PUBG STORE\n⚡ Fast & Instant Delivery\n\nWelcome! Choose an option:",
        "mix": "⚡ MIX POPULARITY",
        "uc": "💎 UC TOP-UP",
        "orders": "📦 MY ORDERS",
        "history": "📜 ORDER HISTORY",
        "payments": "💳 PAYMENT METHODS",
        "contact": "💬 CONTACT ADMIN",
        "how": "❓ HOW TO ORDER",
        "language": "🌐 CHANGE LANGUAGE",
        "choose_product": "Select one product. Each product creates a separate order:",
        "choose_qty": "Select quantity for {product}:",
        "total": "Total: ${total:.2f}",
        "enter_uid": "Enter your PUBG UID:",
        "choose_payment": "Choose a payment method:",
        "payment_missing": "Payment details are not configured yet. Please contact the admin before paying.",
        "payment_info": "Payment method: {method}\nPayment details: {details}\n\nAfter paying, send your transaction ID (TXID).",
        "enter_txid": "Send your transaction ID (TXID) as text:",
        "send_photo": "Now send your payment screenshot as a photo.",
        "photo_only": "Please send the payment screenshot as a photo.",
        "order_received": "✅ Your order #{oid} has been submitted. Payment is pending admin verification.",
        "my_orders": "📦 Your latest orders:\n",
        "no_orders": "You don't have any orders yet.",
        "order_line": "#{oid} | {product} × {qty} | ${total:.2f} | {status}",
        "contact_text": "Please contact the store administrator through the Telegram contact provided by the store.",
        "how_text": "1. Select a product.\n2. Choose quantity.\n3. Enter PUBG UID.\n4. Choose payment method.\n5. Send TXID and payment screenshot.\n6. Wait for admin payment verification.",
        "back": "⬅️ Back to menu",
        "admin_new": "🆕 NEW ORDER #{oid}\nBuyer ID: {buyer}\nProduct: {product}\nQuantity: {qty}\nPUBG UID: {uid}\nPayment: {payment}\nTXID: {txid}\nTotal: ${total:.2f}\nStatus: Payment Pending",
        "admin_only": "This action is for admins only.",
        "updated": "Order #{oid} status updated: {status}",
        "buyer_update": "📦 Update for order #{oid}: {status}",
        "unknown": "Please use the menu buttons or /start.",
        "status_pending": "Payment Pending",
        "status_confirmed": "Payment Confirmed",
        "status_processing": "Processing",
        "status_completed": "Completed",
        "status_cancelled": "Cancelled",
        "payments_text": "Available payment methods:\n• Binance Pay ID\n• Binance USDT BEP20\n• Bybit Pay\n• Bybit USDT BEP20\n\nSelect a product to start an order and choose a method at checkout.",
    },
    "ru": {
        "choose_lang": "🌐 Пожалуйста, выберите язык:",
        "welcome": "🎮 ELITE PUBG STORE\n⚡ Быстрая доставка\n\nДобро пожаловать! Выберите действие:",
        "mix": "⚡ ПОПУЛЯРНОСТЬ",
        "uc": "💎 ПОПОЛНЕНИЕ UC",
        "orders": "📦 МОИ ЗАКАЗЫ",
        "history": "📜 ИСТОРИЯ ЗАКАЗОВ",
        "payments": "💳 СПОСОБЫ ОПЛАТЫ",
        "contact": "💬 СВЯЗАТЬСЯ С АДМИНИСТРАТОРОМ",
        "how": "❓ КАК ЗАКАЗАТЬ",
        "language": "🌐 ИЗМЕНИТЬ ЯЗЫК",
        "choose_product": "Выберите один товар. Для каждого товара создаётся отдельный заказ:",
        "choose_qty": "Выберите количество для {product}:",
        "total": "Итого: ${total:.2f}",
        "enter_uid": "Введите ваш PUBG UID:",
        "choose_payment": "Выберите способ оплаты:",
        "payment_missing": "Платёжные реквизиты ещё не настроены. Перед оплатой свяжитесь с администратором.",
        "payment_info": "Способ оплаты: {method}\nРеквизиты: {details}\n\nПосле оплаты отправьте ID транзакции (TXID).",
        "enter_txid": "Отправьте ID транзакции (TXID) текстом:",
        "send_photo": "Теперь отправьте скриншот оплаты фотографией.",
        "photo_only": "Пожалуйста, отправьте скриншот оплаты фотографией.",
        "order_received": "✅ Ваш заказ №{oid} отправлен. Ожидается проверка оплаты администратором.",
        "my_orders": "📦 Ваши последние заказы:\n",
        "no_orders": "У вас пока нет заказов.",
        "order_line": "№{oid} | {product} × {qty} | ${total:.2f} | {status}",
        "contact_text": "Свяжитесь с администратором магазина через указанный магазином контакт Telegram.",
        "how_text": "1. Выберите товар.\n2. Выберите количество.\n3. Введите PUBG UID.\n4. Выберите способ оплаты.\n5. Отправьте TXID и скриншот оплаты.\n6. Дождитесь проверки оплаты администратором.",
        "back": "⬅️ Назад в меню",
        "admin_new": "🆕 НОВЫЙ ЗАКАЗ №{oid}\nID покупателя: {buyer}\nТовар: {product}\nКоличество: {qty}\nPUBG UID: {uid}\nОплата: {payment}\nTXID: {txid}\nИтого: ${total:.2f}\nСтатус: Ожидает оплаты",
        "admin_only": "Это действие доступно только администраторам.",
        "updated": "Статус заказа №{oid} изменён: {status}",
        "buyer_update": "📦 Обновление заказа №{oid}: {status}",
        "unknown": "Пожалуйста, используйте кнопки меню или команду /start.",
        "status_pending": "Ожидает проверки оплаты",
        "status_confirmed": "Оплата подтверждена",
        "status_processing": "В обработке",
        "status_completed": "Выполнен",
        "status_cancelled": "Отменён",
        "payments_text": "Доступные способы оплаты:\n• Binance Pay ID\n• Binance USDT BEP20\n• Bybit Pay\n• Bybit USDT BEP20\n\nВыберите товар, чтобы оформить заказ и выбрать способ оплаты.",
    },
}

def db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY, lang TEXT NOT NULL DEFAULT 'en'
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL, chat_id INTEGER NOT NULL,
        product TEXT NOT NULL, qty INTEGER NOT NULL, total REAL NOT NULL,
        uid TEXT NOT NULL, payment TEXT NOT NULL, txid TEXT NOT NULL,
        status TEXT NOT NULL, created_at TEXT NOT NULL
    )""")
    conn.commit()
    return conn

def get_lang(user_id):
    conn = db()
    row = conn.execute("SELECT lang FROM users WHERE user_id=?", (user_id,)).fetchone()
    conn.close()
    return row[0] if row else "en"

def set_lang(user_id, lang):
    conn = db()
    conn.execute("INSERT INTO users(user_id,lang) VALUES(?,?) "
                 "ON CONFLICT(user_id) DO UPDATE SET lang=excluded.lang",
                 (user_id, lang))
    conn.commit()
    conn.close()

def tr(user_id, key, **kwargs):
    lang = get_lang(user_id)
    return TEXT[lang].get(key, TEXT["en"].get(key, key)).format(**kwargs)

def main_keyboard(user_id):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(tr(user_id, "mix"), callback_data="mix")],
        [InlineKeyboardButton(tr(user_id, "uc"), callback_data="uc")],
        [InlineKeyboardButton(tr(user_id, "orders"), callback_data="orders")],
        [InlineKeyboardButton(tr(user_id, "history"), callback_data="orders")],
        [InlineKeyboardButton(tr(user_id, "payments"), callback_data="payments")],
        [InlineKeyboardButton(tr(user_id, "contact"), callback_data="contact")],
        [InlineKeyboardButton(tr(user_id, "how"), callback_data="how")],
        [InlineKeyboardButton(tr(user_id, "language"), callback_data="language")],
    ])

def language_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🇬🇧 English", callback_data="lang:en")],
        [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang:ru")],
    ])

def product_keyboard(products, prefix, user_id):
    rows, row = [], []
    for key, (name, price) in products.items():
        row.append(InlineKeyboardButton(f"{name} — ${price:g}", callback_data=f"product:{prefix}:{key}"))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    return InlineKeyboardMarkup(rows + [[InlineKeyboardButton(tr(user_id, "back"), callback_data="home")]])

def quantity_keyboard(user_id):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(str(n), callback_data=f"qty:{n}") for n in (1, 2, 3)],
        [InlineKeyboardButton(str(n), callback_data=f"qty:{n}") for n in (5, 10)],
        [InlineKeyboardButton(tr(user_id, "back"), callback_data="home")],
    ])

def payment_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Binance Pay ID", callback_data="pay:binance_pay")],
        [InlineKeyboardButton("Binance USDT BEP20", callback_data="pay:binance_bep20")],
        [InlineKeyboardButton("Bybit Pay", callback_data="pay:bybit_pay")],
        [InlineKeyboardButton("Bybit USDT BEP20", callback_data="pay:bybit_bep20")],
    ])

def admin_keyboard(order_id):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Confirm Payment", callback_data=f"admin:confirmed:{order_id}")],
        [InlineKeyboardButton("⚙️ Processing", callback_data=f"admin:processing:{order_id}")],
        [InlineKeyboardButton("🎉 Completed", callback_data=f"admin:completed:{order_id}")],
        [InlineKeyboardButton("❌ Cancel", callback_data=f"admin:cancelled:{order_id}")],
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not db_user_exists(user_id):
        await update.message.reply_text(tr(user_id, "choose_lang"), reply_markup=language_keyboard())
    else:
        await update.message.reply_text(tr(user_id, "welcome"), reply_markup=main_keyboard(user_id))

def db_user_exists(user_id):
    conn = db()
    row = conn.execute("SELECT 1 FROM users WHERE user_id=?", (user_id,)).fetchone()
    conn.close()
    return row is not None

async def callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user_id = q.from_user.id
    data = q.data

    if data.startswith("lang:"):
        lang = data.split(":")[1]
        set_lang(user_id, lang)
        await q.edit_message_text(tr(user_id, "welcome"), reply_markup=main_keyboard(user_id))
        return

    if data == "language":
        await q.edit_message_text(tr(user_id, "choose_lang"), reply_markup=language_keyboard())
    elif data == "home":
        context.user_data.clear()
        await q.edit_message_text(tr(user_id, "welcome"), reply_markup=main_keyboard(user_id))
    elif data == "mix":
        await q.edit_message_text(tr(user_id, "choose_product"), reply_markup=product_keyboard(PRODUCTS, "mix", user_id))
    elif data == "uc":
        await q.edit_message_text(tr(user_id, "choose_product"), reply_markup=product_keyboard(UC_PRODUCTS, "uc", user_id))
    elif data.startswith("product:"):
        _, category, key = data.split(":")
        catalog = PRODUCTS if category == "mix" else UC_PRODUCTS
        name, price = catalog[key]
        context.user_data.clear()
        context.user_data.update({"product": name, "price": price, "category": category})
        await q.edit_message_text(
            tr(user_id, "choose_qty", product=name),
            reply_markup=quantity_keyboard(user_id)
        )
    elif data.startswith("qty:"):
        qty = int(data.split(":")[1])
        context.user_data["qty"] = qty
        total = context.user_data["price"] * qty
        context.user_data["total"] = total
        await q.edit_message_text(
            f"{tr(user_id, 'total', total=total)}\n\n{tr(user_id, 'enter_uid')}"
        )
        context.user_data["step"] = "uid"
    elif data == "payments":
        await q.edit_message_text(tr(user_id, "payments_text"), reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton(tr(user_id, "back"), callback_data="home")]]
        ))
    elif data == "orders":
        conn = db()
        rows = conn.execute(
            "SELECT id,product,qty,total,status FROM orders WHERE user_id=? ORDER BY id DESC LIMIT 10",
            (user_id,)
        ).fetchall()
        conn.close()
        if not rows:
            message = tr(user_id, "no_orders")
        else:
            message = tr(user_id, "my_orders") + "\n".join(
                tr(user_id, "order_line", oid=r[0], product=r[1], qty=r[2], total=r[3], status=TEXT[get_lang(user_id)].get(f"status_{r[4]}", r[4]))
                for r in rows
            )
        await q.edit_message_text(message, reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton(tr(user_id, "back"), callback_data="home")]]
        ))
    elif data == "contact":
        await q.edit_message_text(tr(user_id, "contact_text"), reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton(tr(user_id, "back"), callback_data="home")]]
        ))
    elif data == "how":
        await q.edit_message_text(tr(user_id, "how_text"), reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton(tr(user_id, "back"), callback_data="home")]]
        ))
    elif data.startswith("pay:"):
        method = data.split(":")[1]
        details = PAYMENT_DETAILS.get(method, "")
        if not details:
            await q.edit_message_text(
                tr(user_id, "payment_missing"),
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(tr(user_id, "back"), callback_data="home")]])
            )
            return
        context.user_data["payment"] = method
        context.user_data["step"] = "txid"
        await q.edit_message_text(tr(user_id, "payment_info", method=PAYMENT_NAMES[method], details=details) +
                                  "\n\n" + tr(user_id, "enter_txid"))
    elif data.startswith("admin:"):
        if user_id not in ADMIN_IDS:
            return
        _, status, oid = data.split(":")
        oid = int(oid)
        conn = db()
        row = conn.execute("SELECT user_id FROM orders WHERE id=?", (oid,)).fetchone()
        if row:
            conn.execute("UPDATE orders SET status=? WHERE id=?", (status, oid))
            conn.commit()
        conn.close()
        if row:
            status_text = TEXT[get_lang(row[0])].get(f"status_{status}", status)
            await context.bot.send_message(row[0], tr(row[0], "buyer_update", oid=oid, status=status_text))
            await q.edit_message_caption(caption=(q.message.caption or "") + f"\n\nUpdated: {status}")
        else:
            await q.answer("Order not found.", show_alert=True)

async def text_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = (update.message.text or "").strip()
    step = context.user_data.get("step")

    if step == "uid":
        if not text.isdigit():
            await update.message.reply_text(tr(user_id, "enter_uid"))
            return
        context.user_data["uid"] = text
        context.user_data["step"] = "payment"
        await update.message.reply_text(tr(user_id, "choose_payment"), reply_markup=payment_keyboard())
    elif step == "txid":
        context.user_data["txid"] = text
        context.user_data["step"] = "photo"
        await update.message.reply_text(tr(user_id, "send_photo"))
    else:
        await update.message.reply_text(tr(user_id, "unknown"), reply_markup=main_keyboard(user_id))

async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if context.user_data.get("step") != "photo":
        await update.message.reply_text(tr(user_id, "photo_only"))
        return

    required = ("product", "qty", "total", "uid", "payment", "txid")
    if not all(k in context.user_data for k in required):
        context.user_data.clear()
        await update.message.reply_text(tr(user_id, "unknown"), reply_markup=main_keyboard(user_id))
        return

    conn = db()
    cur = conn.execute(
        """INSERT INTO orders
        (user_id,chat_id,product,qty,total,uid,payment,txid,status,created_at)
        VALUES(?,?,?,?,?,?,?,?,?,?)""",
        (user_id, update.effective_chat.id, context.user_data["product"],
         context.user_data["qty"], context.user_data["total"], context.user_data["uid"],
         PAYMENT_NAMES[context.user_data["payment"]], context.user_data["txid"],
         "pending", datetime.utcnow().isoformat(timespec="seconds"))
    )
    order_id = cur.lastrowid
    conn.commit()
    conn.close()

    caption = tr(user_id, "admin_new", oid=order_id, buyer=user_id,
                 product=context.user_data["product"], qty=context.user_data["qty"],
                 uid=context.user_data["uid"], payment=PAYMENT_NAMES[context.user_data["payment"]],
                 txid=context.user_data["txid"], total=context.user_data["total"])

    for admin_id in ADMIN_IDS:
        try:
            await context.bot.send_photo(
                chat_id=admin_id,
                photo=update.message.photo[-1].file_id,
                caption=caption,
                reply_markup=admin_keyboard(order_id)
            )
        except Exception:
            pass

    await update.message.reply_text(tr(user_id, "order_received", oid=order_id),
                                    reply_markup=main_keyboard(user_id))
    context.user_data.clear()

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(tr(update.effective_user.id, "welcome"),
                                    reply_markup=main_keyboard(update.effective_user.id))

def main():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN environment variable is missing.")
    db().close()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cancel", cancel))
    app.add_handler(CallbackQueryHandler(callbacks))
    app.add_handler(MessageHandler(filters.PHOTO, photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_messages))
    app.run_polling()

if __name__ == "__main__":
    main()
