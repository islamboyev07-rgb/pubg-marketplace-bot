````markdown
# 🎮 PUBG Marketplace Bot - BUYSELL.BS

**Telegram bot for buying and selling PUBG game accounts | PUBG akkauntlarini sotish va sotib olish uchun Telegram boti**

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Telegram Bot API](https://img.shields.io/badge/Telegram%20Bot%20API-20.3-blue)
![SQLite](https://img.shields.io/badge/Database-SQLite-green)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 📚 **English | Uzbek**

### 🇬🇧 English

#### **Overview**
PUBG Marketplace Bot is a Telegram bot that allows users to buy and sell PUBG game accounts securely. The bot manages transactions, seller accounts, and payment methods.

#### **Features**
- 🛍️ **For Buyers:**
  - Browse available PUBG accounts
  - Select and purchase accounts
  - Choose payment method (Click UZ, Paynet, Bank Transfer)
  - Track purchase details

- 💰 **For Sellers:**
  - Add and manage game accounts
  - Set account price and description
  - View earnings and transaction history
  - Monitor account status

- 🔒 **Security:**
  - SQLite database for data persistence
  - Environment variables for sensitive data
  - Transaction logging
  - User information storage

#### **Tech Stack**
- **Language:** Python 3.8+
- **Bot Framework:** python-telegram-bot 20.3
- **Database:** SQLite3
- **Environment:** python-dotenv

---

### 🇺🇿 Uzbek

#### **Tavsif**
PUBG Marketplace Bot - bu PUBG o'yinining akkauntlarini xavfsiz sotish va sotib olish uchun Telegram boti. Bot tranzaksiyalarni, sotuvchi akkauntlarini va to'lov usullarini boshqaradi.

#### **Xususiyatlar**
- 🛍️ **Xaridorlar uchun:**
  - Mavjud PUBG akkauntlarini ko'rish
  - Akkaunt tanlash va sotib olish
  - To'lov usulini tanlash (Click UZ, Paynet, Ko'chirma)
  - Sotib olish ma'lumotlarini kuzatish

- 💰 **Sotuvchilar uchun:**
  - O'yin akkauntlarini qo'shish va boshqarish
  - Akkaunt narxi va tavsifini belgilash
  - Daromad va tranzaksiya tarixini ko'rish
  - Akkaunt holatini kuzatish

- 🔒 **Xavfsizlik:**
  - Ma'lumotlarni saqlash uchun SQLite baza
  - Maxfiy ma'lumotlar uchun environment o'zgaruvchilari
  - Tranzaksiya loglamasi
  - Foydalanuvchi ma'lumotlarini saqlash

#### **Texnologiyalar**
- **Til:** Python 3.8+
- **Bot Framework:** python-telegram-bot 20.3
- **Baza:** SQLite3
- **Muhit:** python-dotenv

---

## 🚀 **Installation | O'rnatish**

### **Prerequisites | Kerakli narsalar:**
- Python 3.8 or higher
- Telegram Bot Token (from [@BotFather](https://t.me/BotFather))

### **Steps | Qadamlar:**

1. **Clone the repository | Repositoriyani klonlash:**
```bash
git clone https://github.com/islamboyev07-rgb/pubg-marketplace-bot.git
cd pubg-marketplace-bot
```

2. **Create virtual environment | Virtual muhitni yaratish:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies | Kutubxonalarni o'rnatish:**
```bash
pip install -r requirements.txt
```

4. **Configure environment | Muhitni sozlash:**
```bash
cp .env.example .env
```

Edit `.env` file and add your Telegram bot token:
```
TELEGRAM_TOKEN=your_token_here
```

5. **Run the bot | Botni ishga tushirish:**
```bash
python bot.py
```

---

## 📖 **Usage | Foydalanish**

### **For Sellers | Sotuvchilar uchun:**

1. Open bot: `/start`
2. Click "💰 SOTUVCHI" (SELLER)
3. Choose "➕ Akkaunt qo'sh" (Add Account)
4. Enter:
   - Account name (e.g., `pubg_level100`)
   - Price in UZS (e.g., `250000`)
   - Account description (optional)
5. Confirm and publish

### **For Buyers | Xaridorlar uchun:**

1. Open bot: `/start`
2. Click "🛍️ XARIDOR" (BUYER)
3. Choose "🛍️ Akkauntlarni ko'r" (View Accounts)
4. Select account you want
5. Enter phone number
6. Choose payment method
7. Complete purchase

---

## 📁 **Project Structure | Loyiha Tuzilishi**

```
pubg-marketplace-bot/
├── bot.py                 # Main bot file
├── database.py            # SQLite database module
├── requirements.txt       # Python dependencies
├── .env.example          # Environment template
├── .gitignore            # Git ignore file
└── README.md             # This file
```

---

## 🗄️ **Database | Ma'lumotlar Bazasi**

The bot uses SQLite with the following tables:

**Sellers (Sotuvchilar)**
- seller_id (Unique)
- seller_name
- created_at

**Accounts (Akkauntlar)**
- id (Unique)
- seller_id
- name
- price
- description
- status (active/sold)
- created_at

**Transactions (Tranzaksiyalar)**
- id
- buyer_id, buyer_name
- seller_id, seller_name
- account_id, account_name
- price, commission
- payment_method
- buyer_phone
- created_at

---

## 🔑 **Environment Variables | Muhit O'zgaruvchilari**

Create `.env` file:

```env
# Telegram Bot Token
TELEGRAM_TOKEN=your_bot_token_here

# Database path (optional)
DATABASE_PATH=bot.db
```

---

## 📊 **Bot Commands | Bot Buyruqlari**

| Command | Description | Tavsif |
|---------|-------------|--------|
| `/start` | Start bot | Botni boshlash |
| `/cancel` | Cancel operation | Operatsiyani bekor qilish |

---

## 💳 **Payment Methods | To'lov Usullari**

The bot supports the following payment methods:
- 💳 **Click UZ** - Uzbek payment system
- 🏦 **Paynet** - Bank payments
- 💰 **Ko'chirma** - Direct bank transfer

---

## 📝 **Transaction Flow | Tranzaksiya Qadamlari**

### **Seller Flow:**
```
Seller → Add Account → Set Price → Set Description → Publish → Await Buyer
```

### **Buyer Flow:**
```
Buyer → Browse Accounts → Select Account → Enter Phone → Choose Payment → Purchase
```

---

## ⚙️ **Configuration | Sozlash**

### **Commission | Komissiya:**
- Default: 5% of account price
- Seller receives: 95% of price

### **Database | Baza:**
- Automatically created on first run
- Located in project root: `bot.db`

---

## 🚨 **Error Handling | Xato Boshqarish**

The bot includes error handling for:
- Invalid price input
- Missing database
- Connection errors
- Invalid tokens

---

## 📈 **Features Coming Soon | Tez Orada Keladi**

- [ ] Admin dashboard
- [ ] Account rating system
- [ ] Advanced search filters
- [ ] Auto-decline old accounts
- [ ] Email notifications
- [ ] Multi-language support
- [ ] Account verification

---

## 🤝 **Contributing | Hissa Qo'shish**

Feel free to:
1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📞 **Support | Yordam**

- **Issues:** [GitHub Issues](https://github.com/islamboyev07-rgb/pubg-marketplace-bot/issues)
- **Telegram:** [@buysell_bs_bot](https://t.me/buysell_bs_bot)

---

## 📄 **License | Litsenziya**

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 👨‍💻 **Author | Muallif**

**Developed by:** [@islamboyev07-rgb](https://github.com/islamboyev07-rgb)

---

## ⭐ **Support**

If you find this project helpful, please give it a star! ⭐

---

**Last Updated:** June 2026 | **Version:** 1.0.0
````
