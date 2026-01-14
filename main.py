import os  # ← Add this new line at the top with other imports

from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio

# ================== CONFIG ==================
BOT_TOKEN = os.getenv("BOT_TOKEN")  # ← Loads the token securely from Railway secrets

if not BOT_TOKEN:  # ← Safety check – stops the bot if token is missing
    raise ValueError("BOT_TOKEN is not set in environment variables!")

ADMIN_ID = 5485797953

# Payment details
NAIRA_DETAILS = """
💳 <b>Naira Payment (Bank Transfer)</b>

<b>Bank Name:</b> Palmpay
<b>Account Name:</b> Justin Izuchukwu Eze
<b>Account Number:</b> <code>8073916532</code>

After transfer, click "I have sent payment" and send proof.
"""

USDT_DETAILS = """
🔗 <b>USDT TRC20 Payment</b>

<b>Address:</b> <code>TWC6grDAL1hccuNi83jbcnMGCjRASiXLcc</code>

<b>Network:</b> <b>TRC20 only!</b> (Wrong network = permanent loss of funds)

<b>Note:</b> Send the exact USD equivalent of your chosen plan.

After sending, click "I have sent payment" and send proof.
"""

BTC_DETAILS = """
🔗 <b>Bitcoin (BTC) Payment</b>

<b>Address:</b> <code>bc1q22k3rz5t0cjnq6crux3rnrvpdzsvm0nlkk5n6l</code>

<b>Note:</b> Send the exact USD equivalent of your chosen plan.
Use the Bitcoin network (on-chain).

After sending, click "I have sent payment" and send proof.
"""

FOREIGN_DETAILS = """
🌍 <b>Foreign / International Payment</b>

For PayPal, card, international transfer, or other methods,

contact support: @cypherfx

We will provide personalized instructions.
"""

# VIP Details (fixed HTML: removed empty bullet, closed the outer blockquote properly)
VIP_DETAILS = """
🔥 <b>VIP Signal Service</b> 🔥

<b>Premium Forex Signals with High Accuracy</b>
<blockquote>• Minimum 3–5 signals weekly (minimum!)
• Monday - Friday active Signals
• 90% win rate track record</blockquote>

<b>PAIRS WE TRADE</b>
<blockquote>»» Major Currency pairs
»» Gold and Silver Pair
»» Crypto (Bitcoin & Etherum)</blockquote>

<b>+FULL TRADE MANAGEMENT GUIDANCE</b>
<blockquote>• Stop Loss & Take Profit levels
• Break-even strategies
• When to close trades
• Partial profit techniques
• Additional risk management tips</blockquote>

<b>VIP SIGNALS SUBSCRIPTION PLANS</b>
<b>1 Month</b>
<blockquote>N50,000 ≈ $35</blockquote>

<b>3 Months</b>
<blockquote>• N130,000 ≈ $91</blockquote>

<b>6 Months</b>
<blockquote>N260,000 ≈ $182</blockquote>

<b>12 Months</b>
<blockquote>N520,000 ≈ $364</blockquote>

<b>GOOD NEWS</b> 🎉 
<blockquote>You don't need any trading experience to trade and make money with us in the Vip Signal Group!
Just create and fund your account with the link below, then subscribe to our vip signals group and start trading our buy and sell signals/projections every day ✅️
http://bit.ly/41jyYri</blockquote>

<blockquote>Join, sit back, and be alert for our buy or sell signals/charts projections. Once we post and confirm the signal, trade it exactly as you see and count your profit. With only our signals and trades, you will be making good profit daily. Be rest assured that your trading account will grow awesomely</blockquote>

<b>TERMS & CONDITIONS</b>
<blockquote>Complaints after a full month of following signals
Daily signals, analysis, and dedicated support! 🚀</blockquote>
""".strip()

# Training Details (fixed HTML: wrapped the final paragraph in its own blockquote to match tags)
TRAINING_DETAILS = """
📚 <b>FOREX TRAINING PROGRAM + MENTORSHIP</b> 📚

<b>PICK YOUR PREFERRED PACKAGE PLAN</b>
<blockquote>Exclusive One-On-One Mentorship (online)
Exclusive One-On-One Mentorship (physical)</blockquote>

<b>EXCLUSIVE ONE-ONE-ONE TRAINING
(online Private Training)</b>
<blockquote>• Live sessions (Zoom video meet/chat)
• 1 month + 2 weeks duration
• 3 sessions weekly (2–3 hrs per session)
• Access to my VIP Signals Group
• Lifetime Mentorship/follow-up</blockquote>
<b>PRICE:</b>
<blockquote>N150,000 ≈ $100 (ONE-TIME)</blockquote>


<b>EXCLUSIVE ONE-ONE-ONE TRAINING
(Physical Private Training) ~ [locals only]</b>
<blockquote>• In-person at trade office
• 1 month duration
• 3 sessions weekly (2–3 hrs per session)
• Access to my VIP Signals Group
• Lifetime Mentorship/follow-up</blockquote>
<b>PRICE:</b>
<blockquote>N450,000 ≈ $315 (ONE-TIME)</blockquote>


<b>VALUE DELIVERED:</b>
<blockquote>• Master and interprete market analysis
• Generate your own accurate buy/sell signals
• Trade independently as a full-time or part-time pro trader
• Make money daily from your analysis
• Be your own boss and not work 9 to 5
• Lifetime skills for consistent profits</blockquote>

<blockquote>We transform you from a novice trader to a Master Forex trader. We don't just mentor you to become a forex trader but to become a "Profitable Forex Trader" who is able to analyse the market, generate buy & sell signals for yourself and make money from it daily 💹</blockquote>
""".strip()

# Course Details (styled exactly like EA)
COURSE_DETAILS = """
📚 <b>INTRODUCTION TO FOREX TRADING Part 1&2</b> 📚

<blockquote>This course is strictly for newbies who want to have a very strong and unshakable root in Forex Trading.</blockquote>

<b>PRICE:</b>
<blockquote>N15,000 ≈ $13 only</blockquote>

<blockquote>This course started with "What is Forex". We broke Forex Trading down to a layman's understanding such that even an illitrate will be able to understand it clearly and have a strong ground in the Forex market
We also did practicals samples on how to use the trading platform for newbies

NB:
You must not skip this preliminary level if you ever want to trade the Forex Market.</blockquote>

<b>VALUE DELIVERED:</b>
<blockquote>The primary value of this course is providing a comprehensive foundational bridge for beginner traders. It aims to demystify the "preliminary aspect" of the market so that students are not confused when they reach advanced analytical levels. You can't do without them. By standardizing the "peculiar languages" and terminologies of the industry, it prepares the reader to understand professional market analysis and successfully navigate trading platforms like MT4. Doing without them is like jumping primary and secondary school into the University level</blockquote>

<b>SECRET:</b>
<blockquote>This course will open your eyes on what Forex Trading is all about.📉📈💹</blockquote>
""".strip()

# EA Details (unchanged)
EA_DETAILS = """
🤖 <b>ROBOT TRADING (Automated EA)</b>

<blockquote>I have optimized a very powerful and profitable Forex Expert Advisor (Trading Robot) that can trade for you and earn you profits on a daily basis, which compounds into an amazing monthly profit</blockquote>

<b>Monthly Profit Range</b>
<blockquote>5% and up to 20% profit monthly</blockquote>

<b>Recommended Capital</b>
<blockquote>Account size Range: $500 - $10,000</blockquote>

<blockquote>Send a message to @cypherfx for a guide to connect the robot to your trading account (MT4). It will start executing trades automatically once the market is favorable.</blockquote>

<b>NB</b>
<blockquote>A 40:60 MONTHLY PROFIT SPLIT APPLICABLE. 60% of the profit is yours while 40% is ours.</blockquote>

<b>NB</b>
<blockquote>There is a 10% activation fee before we proceed to copy trades into your account. This is NON NEGOTIABLE</blockquote>

<b>NB</b>
<blockquote>Your Forex account must be created with the broker link below</blockquote>
""".strip()

EXNESS_LINK = "http://bit.ly/41jyYri"
FTMO_LINK = "https://trader.ftmo.com/?affiliates=3211"

MAIN_MENU_TEXT = """
Hello good day, how may I help you? 😊

We have premium services available.
Choose an option from the menu below:
"""

# Persistent bottom keyboard with Menu and Start icons
persistent_kb_builder = ReplyKeyboardBuilder()
persistent_kb_builder.button(text="☰ Menu")
persistent_kb_builder.button(text="▶️ Start")
persistent_kb_builder.adjust(2)
persistent_kb = persistent_kb_builder.as_markup(resize_keyboard=True)

# Inline main menu (Vip renamed to Vip Signals, Training renamed, Course added right under Training)
def get_main_menu_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="Vip Signals", callback_data="menu_vip")
    kb.button(text="Forex Training/Mentorship", callback_data="menu_training")
    kb.button(text="Forex Course for beginners Part 1&2", callback_data="menu_course")
    kb.button(text="EA ~ Let robot trade for you", callback_data="menu_ea")
    kb.button(text="Partnership", callback_data="menu_partnership")
    kb.button(text="Gift", callback_data="menu_gift")
    kb.button(text="FAQ", callback_data="menu_faq")
    kb.button(text="Contact Support ➡️", callback_data="menu_contact")
    kb.adjust(1)
    return kb.as_markup()

# ===========================================
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()

class PaymentFlow(StatesGroup):
    choosing_method = State()
    waiting_for_proof = State()

# /start
@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Welcome back! 😊", reply_markup=persistent_kb)
    await message.answer(MAIN_MENU_TEXT, reply_markup=get_main_menu_kb())

# Persistent buttons
@router.message(F.text == "▶️ Start")
async def persistent_start(message: Message):
    await message.answer(MAIN_MENU_TEXT, reply_markup=get_main_menu_kb())

@router.message(F.text == "☰ Menu")
async def persistent_menu(message: Message):
    await message.answer(MAIN_MENU_TEXT, reply_markup=get_main_menu_kb())

# Main menu callbacks
@router.callback_query(F.data == "menu_vip")
async def menu_vip(call: CallbackQuery):
    kb = InlineKeyboardBuilder()
    kb.button(text="Proceed to Pay", callback_data="pay_vip")
    kb.button(text="🔙 Back to Main Menu", callback_data="main_menu")
    kb.adjust(1)
    await call.message.edit_text(VIP_DETAILS, reply_markup=kb.as_markup(), parse_mode=ParseMode.HTML)
    await call.answer()

@router.callback_query(F.data == "menu_training")
async def menu_training(call: CallbackQuery):
    kb = InlineKeyboardBuilder()
    kb.button(text="Proceed to Pay", callback_data="pay_training")
    kb.button(text="🔙 Back to Main Menu", callback_data="main_menu")
    kb.adjust(1)
    await call.message.edit_text(TRAINING_DETAILS, reply_markup=kb.as_markup(), parse_mode=ParseMode.HTML)
    await call.answer()

# New handler for Beginners Course (positioned under Training in menu)
@router.callback_query(F.data == "menu_course")
async def menu_course(call: CallbackQuery):
    kb = InlineKeyboardBuilder()
    kb.button(text="Proceed to Pay", callback_data="pay_course")
    kb.button(text="🔙 Back to Main Menu", callback_data="main_menu")
    kb.adjust(1)
    await call.message.edit_text(COURSE_DETAILS, reply_markup=kb.as_markup(), parse_mode=ParseMode.HTML)
    await call.answer()

@router.callback_query(F.data == "menu_ea")
async def menu_ea(call: CallbackQuery):
    kb = InlineKeyboardBuilder()
    kb.button(text="Create Account", url=EXNESS_LINK)
    kb.button(text="Message Cypher Fx", url="https://t.me/cypherfx")
    kb.button(text="🔙 Back to Main Menu", callback_data="main_menu")
    kb.adjust(1)
    await call.message.edit_text(EA_DETAILS, reply_markup=kb.as_markup(), parse_mode=ParseMode.HTML)
    await call.answer()

@router.callback_query(F.data == "menu_partnership")
async def menu_partnership(call: CallbackQuery):
    kb = InlineKeyboardBuilder()
    kb.button(text="Brokers", callback_data="part_brokers")
    kb.button(text="Prop firm", callback_data="part_propfirm")
    kb.button(text="🔙 Back to Main Menu", callback_data="main_menu")
    kb.adjust(1)
    await call.message.edit_text(
        "🤝 Partnership\n\n"
        "Choose a partnership type:",
        reply_markup=kb.as_markup()
    )
    await call.answer()

@router.callback_query(F.data == "menu_gift")
async def menu_gift(call: CallbackQuery):
    kb = InlineKeyboardBuilder()
    kb.button(text="🔙 Back to Main Menu", callback_data="main_menu")
    kb.adjust(1)
    await call.message.edit_text(
        "🎁 Gift\n\n"
        "Gift a subscription or training...\n"
        "Contact support to arrange.",
        reply_markup=kb.as_markup()
    )
    await call.answer()

@router.callback_query(F.data == "menu_faq")
async def menu_faq(call: CallbackQuery):
    faq_text = """
<b>❓ Frequently Asked Questions (FAQ)</b>

<b>1. How much is CypherFx VIP Signal, how do I pay and sign up?</b>
<blockquote>VIP Signal prices:
• Monthly — N50,000 ≈ $35
• 3 Months — N130,000 ≈ $91
• 6 Months — N260,000 ≈ $182
• 12 Months — N520,000 ≈ $364

To sign up: Select “Vip Signal” from the main menu → “Proceed to Pay” → choose your payment method.</blockquote>

<b>2. How are signals sent and what format do they use?</b>
<blockquote>Signals are premium buy/sell recommendations with entry price, stop loss, take profit, and full management guidance (break-even, partial profits, etc.).
Delivered directly with high accuracy (90% win rate target).</blockquote>

<b>3. When are signals sent?</b>
<blockquote>Minimum 3–5 (minimum) high-quality signals per week, sent during optimal market sessions for best results.</blockquote>

<b>4. What is the minimum capital to trade CypherFx signals?</b>
<blockquote>• Live account: Minimum $50 (no maximum)
• Prop firm accounts: Minimum $5000 (no maximum)</blockquote>

<b>5. Can I cancel my subscription and get a refund?</b>
<blockquote>You can choose not to renew — access ends automatically when the subscription expires.
No refunds after access is granted.</blockquote>

More questions? Contact support directly!
    """.strip()
    kb = InlineKeyboardBuilder()
    kb.button(text="🔙 Back to Main Menu", callback_data="main_menu")
    kb.adjust(1)
    await call.message.edit_text(faq_text, reply_markup=kb.as_markup(), parse_mode=ParseMode.HTML)
    await call.answer()

@router.callback_query(F.data == "menu_contact")
async def menu_contact(call: CallbackQuery):
    kb = InlineKeyboardBuilder()
    kb.button(text="🔙 Back to Main Menu", callback_data="main_menu")
    kb.adjust(1)
    await call.message.edit_text(
        "📞 Contact Support\n\n"
        "Message @cypherfx directly or reply here.\n"
        "We'll respond as soon as possible!",
        reply_markup=kb.as_markup()
    )
    await call.answer()

# Back to Main Menu
@router.callback_query(F.data == "main_menu")
async def back_to_main_menu(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text(MAIN_MENU_TEXT, reply_markup=get_main_menu_kb())
    await call.answer()

# Payment flow - updated to support the new course
@router.callback_query(F.data.startswith("pay_"))
async def process_pay(call: CallbackQuery, state: FSMContext):
    if call.data == "pay_vip":
        service = "Vip Signals"
    elif call.data == "pay_training":
        service = "Forex Training/Mentorship"
    elif call.data == "pay_course":
        service = "Forex Course for beginners Part 1&2"
    else:
        service = "Service"
    
    await state.set_state(PaymentFlow.choosing_method)
    await state.update_data(service=service)
    
    method_kb = InlineKeyboardBuilder()
    method_kb.button(text="Naira Payment", callback_data="method_naira")
    method_kb.button(text="USDT TRC20", callback_data="method_usdt")
    method_kb.button(text="BTC", callback_data="method_btc")
    method_kb.button(text="Foreign Payment", callback_data="method_foreign")
    method_kb.button(text="🔙 Back", callback_data="back")
    method_kb.adjust(1)
    
    await call.message.edit_text(
        f"💳 Payment for {service}\n\n"
        "Please select your preferred payment method:",
        reply_markup=method_kb.as_markup()
    )
    await call.answer()

@router.callback_query(F.data.startswith("method_"))
async def choose_payment_method(call: CallbackQuery, state: FSMContext):
    method_code = call.data[len("method_"):]
    
    methods = {
        "naira": ("Naira Payment", NAIRA_DETAILS),
        "usdt": ("USDT TRC20", USDT_DETAILS),
        "btc": ("BTC", BTC_DETAILS),
        "foreign": ("Foreign Payment", FOREIGN_DETAILS),
    }
    
    if method_code not in methods:
        await call.answer("Invalid option", show_alert=True)
        return
    
    method_name, details = methods[method_code]
    
    data = await state.get_data()
    service = data.get("service", "Service")
    
    await state.update_data(method=method_name)
    
    if method_code == "foreign":
        back_kb = InlineKeyboardBuilder()
        back_kb.button(text="🔙 Back", callback_data="back")
        back_kb.adjust(1)
        
        await call.message.edit_text(
            f"💳 {service} — {method_name}\n\n{details}",
            reply_markup=back_kb.as_markup(),
            parse_mode=ParseMode.HTML
        )
        await state.clear()
    else:
        sent_kb = InlineKeyboardBuilder()
        sent_kb.button(text="✅ I have sent payment", callback_data="sent_payment")
        sent_kb.button(text="🔙 Back", callback_data="back")
        sent_kb.adjust(1)
        
        await call.message.edit_text(
            f"💳 {service} — {method_name}\n\n"
            "<b>Tap the Account No or Crypto Address to copy it instantly (avoids typing errors!)</b>\n\n"  # ← Updated instruction
            f"{details}",
            reply_markup=sent_kb.as_markup(),
            parse_mode=ParseMode.HTML
        )
        await state.set_state(PaymentFlow.waiting_for_proof)
    
    await call.answer()

@router.callback_query(F.data == "sent_payment")
async def sent_payment(call: CallbackQuery):
    await call.message.edit_text(
        "📸 Please send a clear screenshot/photo of your payment proof.\n\n"
        "Make sure the transaction details are visible.",
        reply_markup=None
    )
    await call.answer()

# Progressive back (updated to support the new course)
@router.callback_query(F.data == "back")
async def handle_back(call: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    data = await state.get_data()
    
    if current_state == PaymentFlow.waiting_for_proof.state:
        await state.set_state(PaymentFlow.choosing_method)
        service = data.get("service", "Service")
        method_kb = InlineKeyboardBuilder()
        method_kb.button(text="Naira Payment", callback_data="method_naira")
        method_kb.button(text="USDT TRC20", callback_data="method_usdt")
        method_kb.button(text="BTC", callback_data="method_btc")
        method_kb.button(text="Foreign Payment", callback_data="method_foreign")
        method_kb.button(text="🔙 Back", callback_data="back")
        method_kb.adjust(1)
        await call.message.edit_text(
            f"💳 Payment for {service}\n\n"
            "Please select your preferred payment method:",
            reply_markup=method_kb.as_markup()
        )
        await call.answer()
        return
    
    if current_state == PaymentFlow.choosing_method.state or "service" in data:
        await state.clear()
        service = data.get("service", "Vip Signals")
        if service == "Vip Signals":
            text = VIP_DETAILS
            pay_data = "pay_vip"
        elif service == "Forex Training/Mentorship":
            text = TRAINING_DETAILS
            pay_data = "pay_training"
        elif service == "Forex Course for beginners Part 1&2":
            text = COURSE_DETAILS
            pay_data = "pay_course"
        else:
            text = VIP_DETAILS
            pay_data = "pay_vip"
        kb = InlineKeyboardBuilder()
        kb.button(text="Proceed to Pay", callback_data=pay_data)
        kb.button(text="🔙 Back to Main Menu", callback_data="main_menu")
        kb.adjust(1)
        await call.message.edit_text(text, reply_markup=kb.as_markup(), parse_mode=ParseMode.HTML)
        await call.answer()
        return
    
    await state.clear()
    await call.message.edit_text(MAIN_MENU_TEXT, reply_markup=get_main_menu_kb())
    await call.answer()

# Proof handling
@router.message(PaymentFlow.waiting_for_proof, F.photo)
async def receive_proof(message: Message, state: FSMContext):
    data = await state.get_data()
    service = data.get("service", "Unknown")
    method = data.get("method", "Unknown")
    username = data.get("username", "No username")
    user_id = message.from_user.id
    
    await message.forward(ADMIN_ID)
    
    await bot.send_message(
        ADMIN_ID,
        f"🆕 New Payment Proof Received!\n\n"
        f"Service: {service}\n"
        f"Payment Method: {method}\n"
        f"User: {username} (ID: {user_id})\n"
        f"Check the forwarded photo above."
    )
    
    await message.answer(
        "✅ Proof received! Thank you.\n\n"
        "I will verify it and contact you shortly to complete your access.\n"
        "Have a great day! 😊",
        reply_markup=persistent_kb
    )
    
    await state.clear()

@router.message(PaymentFlow.waiting_for_proof)
async def wrong_proof(message: Message):
    await message.answer("❌ Please send only a photo/screenshot of the payment proof.")

# Partnership
@router.callback_query(F.data == "part_brokers")
async def part_brokers(call: CallbackQuery):
    kb = InlineKeyboardBuilder()
    kb.button(text="EXNESS BROKER", url=EXNESS_LINK)
    kb.button(text="🔙 Back", callback_data="menu_partnership")
    kb.button(text="🔙 Back to Main Menu", callback_data="main_menu")
    kb.adjust(1)
    await call.message.edit_text(
        "🔗 Broker Partnership\n\n"
        "Recommended broker:\n"
        "Click below to register/open account:",
        reply_markup=kb.as_markup()
    )
    await call.answer()

@router.callback_query(F.data == "part_propfirm")
async def part_propfirm(call: CallbackQuery):
    kb = InlineKeyboardBuilder()
    kb.button(text="FTMO", url=FTMO_LINK)
    kb.button(text="🔙 Back", callback_data="menu_partnership")
    kb.button(text="🔙 Back to Main Menu", callback_data="main_menu")
    kb.adjust(1)
    await call.message.edit_text(
        "🔗 Prop Firm Partnership\n\n"
        "Recommended prop firm:\n"
        "Click below to register:",
        reply_markup=kb.as_markup()
    )
    await call.answer()

dp.include_router(router)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
