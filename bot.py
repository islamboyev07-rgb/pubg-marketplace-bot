import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ConversationHandler, filters, ContextTypes
from datetime import datetime
from dotenv import load_dotenv
from database import Database

# Load environment variables
load_dotenv()

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

SELLER_CHOOSE, SELLER_ADD_ACCOUNT, SELLER_PRICE, SELLER_DESCRIPTION = range(4)
BUYER_CHOOSE, BUYER_SELECT_ACCOUNT, BUYER_PHONE, BUYER_PAYMENT = range(4)

class PUBGMarketplaceBot:
    def __init__(self, token):
        self.token = token
        self.db = Database()
        self.app = Application.builder().token(token).build()
        self.setup_handlers()
    
    def setup_handlers(self):
        self.app.add_handler(CommandHandler("start", self.start))
        seller_conv = ConversationHandler(
            entry_points=[CallbackQueryHandler(self.seller_menu, pattern="^seller$")],
            states={
                SELLER_CHOOSE: [
                    CallbackQueryHandler(self.seller_add_account, pattern="^add_account$"),
                    CallbackQueryHandler(self.seller_my_accounts, pattern="^my_accounts$"),
                    CallbackQueryHandler(self.seller_earnings, pattern="^earnings$"),
                ],
                SELLER_ADD_ACCOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.seller_account_name)],
                SELLER_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.seller_price_input)],
                SELLER_DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.seller_description_input)],
            },
            fallbacks=[CommandHandler("cancel", self.cancel)]
        )
        buyer_conv = ConversationHandler(
            entry_points=[CallbackQueryHandler(self.buyer_menu, pattern="^buyer$")],
            states={
                BUYER_CHOOSE: [CallbackQueryHandler(self.buyer_list_accounts, pattern="^buy_account$")],
                BUYER_SELECT_ACCOUNT: [CallbackQueryHandler(self.buyer_select_specific, pattern="^buy_")],
                BUYER_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.buyer_phone_input)],
                BUYER_PAYMENT: [CallbackQueryHandler(self.buyer_payment_method)],
            },
            fallbacks=[CommandHandler("cancel", self.cancel)]
        )
        self.app.add_handler(seller_conv)
        self.app.add_handler(buyer_conv)
        self.app.add_handler(CallbackQueryHandler(self.button_callback))
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = [[InlineKeyboardButton("🛍️ XARIDOR", callback_data="buyer"), InlineKeyboardButton("💰 SOTUVCHI", callback_data="seller")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("🎮 *PUBG MARKETPLACE - BUYSELL.BS*\n\nNima qilmoxchisiz?", reply_markup=reply_markup, parse_mode="Markdown")
    
    async def seller_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        seller_id = query.from_user.id
        seller_name = query.from_user.first_name or "Unknown"
        
        # Add seller to database
        self.db.add_seller(seller_id, seller_name)
        
        keyboard = [[InlineKeyboardButton("➕ Akkaunt qo'sh", callback_data="add_account")], [InlineKeyboardButton("📋 Mening akkauntlarim", callback_data="my_accounts")], [InlineKeyboardButton("💰 Daromadim", callback_data="earnings")], [InlineKeyboardButton("⬅️ Orqaga", callback_data="start")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("💰 *SOTUVCHI PANELI*\n\nNima qilmoxchisiz?", reply_markup=reply_markup, parse_mode="Markdown")
        return SELLER_CHOOSE
    
    async def seller_add_account(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        await query.edit_message_text("📝 *Akkaunt nomini kiriting:*\n\nMasalan: `pubg_level100`", parse_mode="Markdown")
        return SELLER_ADD_ACCOUNT
    
    async def seller_account_name(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data['account_name'] = update.message.text
        await update.message.reply_text("💵 *Narxini kiriting (so'm):*\n\nMasalan: `250000`", parse_mode="Markdown")
        return SELLER_PRICE
    
    async def seller_price_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            price = int(update.message.text.replace(",", "").replace(" ", ""))
            context.user_data['price'] = price
            await update.message.reply_text("📖 *Akkaunt haqida ma'lumot:*\n\n(Masalan: `Level 120`)\n\nYoki `/skip`", parse_mode="Markdown")
            return SELLER_DESCRIPTION
        except:
            await update.message.reply_text("❌ Faqat raqam!")
            return SELLER_PRICE
    
    async def seller_description_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        description = update.message.text if update.message.text != "/skip" else "Ma'lumot yo'q"
        seller_id = update.effective_user.id
        seller_name = update.effective_user.first_name or "Unknown"
        
        account_id = f"{seller_id}_{datetime.now().timestamp()}"
        
        # Add account to database
        self.db.add_account(
            account_id,
            seller_id,
            context.user_data.get('account_name'),
            context.user_data.get('price'),
            description
        )
        
        account = {
            'id': account_id,
            'name': context.user_data.get('account_name'),
            'price': context.user_data.get('price'),
            'description': description,
            'seller_name': seller_name,
            'seller_id': seller_id,
            'status': 'active'
        }
        
        commission = int(account['price'] * 0.05)
        seller_gets = account['price'] - commission
        keyboard = [[InlineKeyboardButton("✅ Tasdiqlash", callback_data="confirm_add")], [InlineKeyboardButton("❌ Bekor qilish", callback_data="cancel_add")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        text = f"✅ *TASDIQLANG*\n\n📝 *Akkaunt:* `{account['name']}`\n💵 *Narx:* `{account['price']:,}` so'm\n💰 *Komissiya (5%):* `{commission:,}` so'm\n👤 *Sizni olib qolishingiz:* `{seller_gets:,}` so'm"
        context.user_data['temp_account'] = account
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")
        return SELLER_CHOOSE
    
    async def seller_my_accounts(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        seller_id = query.from_user.id
        accounts = self.db.get_seller_accounts(seller_id)
        
        if not accounts:
            await query.edit_message_text("📭 Akkaunt yo'q")
            return SELLER_CHOOSE
        
        text = "*AKKAUNTLARINGIZ:*\n\n"
        for i, acc in enumerate(accounts, 1):
            status_emoji = "✅" if acc['status'] == 'active' else "❌"
            text += f"{i}. {status_emoji} `{acc['name']}` - `{acc['price']:,}` so'm\n"
        
        await query.edit_message_text(text, parse_mode="Markdown")
        return SELLER_CHOOSE
    
    async def seller_earnings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        seller_id = query.from_user.id
        earnings = self.db.get_seller_earnings(seller_id)
        
        text = f"💰 *DAROMADINGIZ*\n\nJami: `{earnings['total_earnings']:,}` so'm\nSotilgan: `{earnings['total_sales']}` dona"
        await query.edit_message_text(text, parse_mode="Markdown")
        return SELLER_CHOOSE
    
    async def buyer_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        keyboard = [[InlineKeyboardButton("🛍️ Akkauntlarni ko'r", callback_data="buy_account")], [InlineKeyboardButton("⬅️ Orqaga", callback_data="start")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("🛍️ *XARIDOR PANELI*", reply_markup=reply_markup, parse_mode="Markdown")
        return BUYER_CHOOSE
    
    async def buyer_list_accounts(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        all_accounts = self.db.get_all_active_accounts()
        
        if not all_accounts:
            await query.edit_message_text("📭 Akkaunt yo'q")
            return BUYER_CHOOSE
        
        keyboard = []
        for acc in all_accounts:
            keyboard.append([InlineKeyboardButton(f"{acc['name']} - {acc['price']:,} so'm", callback_data=f"buy_{acc['id']}")])
        keyboard.append([InlineKeyboardButton("⬅️ Orqaga", callback_data="buyer")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        text = f"📋 *{len(all_accounts)} TA AKKAUNT:*"
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")
        return BUYER_SELECT_ACCOUNT
    
    async def buyer_select_specific(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        account_id = query.data.replace("buy_", "")
        selected_account = self.db.get_account(account_id)
        
        if not selected_account:
            await query.edit_message_text("❌ Akkaunt topilmadi")
            return BUYER_SELECT_ACCOUNT
        
        context.user_data['selected_account'] = selected_account
        text = f"✅ *AKKAUNT TANLANDI*\n\n📝 *Akkaunt:* `{selected_account['name']}`\n💵 *Narx:* `{selected_account['price']:,}` so'm\n📖 *Ma'lumot:* {selected_account['description']}\n\n📱 *Telefon raqamingizni kiriting:*"
        await query.edit_message_text(text, parse_mode="Markdown")
        return BUYER_PHONE
    
    async def buyer_phone_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data['buyer_phone'] = update.message.text
        keyboard = [[InlineKeyboardButton("💳 Click UZ", callback_data="payment_click")], [InlineKeyboardButton("🏦 Paynet", callback_data="payment_paynet")], [InlineKeyboardButton("💰 Ko'chirma", callback_data="payment_transfer")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("💳 *TO'LOV USULI:*", reply_markup=reply_markup, parse_mode="Markdown")
        return BUYER_PAYMENT
    
    async def buyer_payment_method(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        payment_method = query.data.replace("payment_", "")
        buyer_id = query.from_user.id
        buyer_name = query.from_user.first_name or "Unknown"
        buyer_phone = context.user_data.get('buyer_phone', 'N/A')
        selected_account = context.user_data.get('selected_account')
        
        if not selected_account:
            await query.edit_message_text("❌ Xato")
            return BUYER_CHOOSE
        
        commission = int(selected_account['price'] * 0.05)
        
        # Add transaction to database
        self.db.add_transaction(
            buyer_id,
            buyer_name,
            selected_account['seller_id'],
            selected_account['seller_name'],
            selected_account['id'],
            selected_account['name'],
            selected_account['price'],
            commission,
            payment_method,
            buyer_phone
        )
        
        buyer_text = f"✅ *BUYURTMA QABUL QILINDI!*\n\n📝 *Akkaunt:* `{selected_account['name']}`\n💵 *Narx:* `{selected_account['price']:,}` so'm\n💳 *To'lov usuli:* {payment_method}\n\n⏳ Admin 5 minut ichida ma'lumot jo'natadi!"
        await query.edit_message_text(buyer_text, parse_mode="Markdown")
        return BUYER_CHOOSE
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        if query.data == "start":
            keyboard = [[InlineKeyboardButton("🛍️ XARIDOR", callback_data="buyer"), InlineKeyboardButton("💰 SOTUVCHI", callback_data="seller")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text("🎮 *PUBG MARKETPLACE*\n\nNima qilmoxchisiz?", reply_markup=reply_markup, parse_mode="Markdown")
        elif query.data == "confirm_add":
            await query.edit_message_text("✅ *AKKAUNT QO'SHILDI!*\n\n🎉 Xaridor kelsa bildirishni olasiz!")
        elif query.data == "cancel_add":
            await query.edit_message_text("❌ Bekor qilindi")
    
    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("❌ Bekor qilindi")
        return ConversationHandler.END
    
    def run(self):
        self.app.run_polling()

if __name__ == '__main__':
    TOKEN = os.getenv('TELEGRAM_TOKEN')
    if not TOKEN:
        print("❌ TELEGRAM_TOKEN environment variable not set!")
        print("📝 Please set TELEGRAM_TOKEN in .env file")
        exit(1)
    
    bot = PUBGMarketplaceBot(TOKEN)
    print("🚀 Bot ishga tushdi!")
    bot.run()
