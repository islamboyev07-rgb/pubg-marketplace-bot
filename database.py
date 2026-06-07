import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional

class Database:
    def __init__(self, db_path: str = "bot.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize database with tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Sellers table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sellers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                seller_id INTEGER UNIQUE NOT NULL,
                seller_name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Accounts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS accounts (
                id TEXT PRIMARY KEY,
                seller_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                price INTEGER NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (seller_id) REFERENCES sellers(seller_id)
            )
        ''')
        
        # Transactions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                buyer_id INTEGER NOT NULL,
                buyer_name TEXT NOT NULL,
                seller_id INTEGER NOT NULL,
                seller_name TEXT NOT NULL,
                account_id TEXT NOT NULL,
                account_name TEXT NOT NULL,
                price INTEGER NOT NULL,
                commission INTEGER NOT NULL,
                payment_method TEXT,
                buyer_phone TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (account_id) REFERENCES accounts(id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    # ===== SELLER METHODS =====
    def add_seller(self, seller_id: int, seller_name: str) -> bool:
        """Add new seller"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                'INSERT OR IGNORE INTO sellers (seller_id, seller_name) VALUES (?, ?)',
                (seller_id, seller_name)
            )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding seller: {e}")
            return False
    
    def add_account(self, account_id: str, seller_id: int, name: str, 
                   price: int, description: str) -> bool:
        """Add new account for seller"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                '''INSERT INTO accounts (id, seller_id, name, price, description) 
                   VALUES (?, ?, ?, ?, ?)''',
                (account_id, seller_id, name, price, description)
            )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding account: {e}")
            return False
    
    def get_seller_accounts(self, seller_id: int) -> List[Dict]:
        """Get all accounts for seller"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                '''SELECT id, name, price, description, status, created_at 
                   FROM accounts WHERE seller_id = ? ORDER BY created_at DESC''',
                (seller_id,)
            )
            rows = cursor.fetchall()
            conn.close()
            
            accounts = []
            for row in rows:
                accounts.append({
                    'id': row[0],
                    'name': row[1],
                    'price': row[2],
                    'description': row[3],
                    'status': row[4],
                    'created_at': row[5]
                })
            return accounts
        except Exception as e:
            print(f"Error getting seller accounts: {e}")
            return []
    
    def get_all_active_accounts(self) -> List[Dict]:
        """Get all active accounts from all sellers"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                '''SELECT a.id, a.seller_id, a.name, a.price, a.description, 
                          a.status, s.seller_name
                   FROM accounts a
                   JOIN sellers s ON a.seller_id = s.seller_id
                   WHERE a.status = 'active'
                   ORDER BY a.created_at DESC'''
            )
            rows = cursor.fetchall()
            conn.close()
            
            accounts = []
            for row in rows:
                accounts.append({
                    'id': row[0],
                    'seller_id': row[1],
                    'name': row[2],
                    'price': row[3],
                    'description': row[4],
                    'status': row[5],
                    'seller_name': row[6]
                })
            return accounts
        except Exception as e:
            print(f"Error getting all active accounts: {e}")
            return []
    
    def get_account(self, account_id: str) -> Optional[Dict]:
        """Get specific account details"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                '''SELECT a.id, a.seller_id, a.name, a.price, a.description, 
                          a.status, s.seller_name, s.seller_id
                   FROM accounts a
                   JOIN sellers s ON a.seller_id = s.seller_id
                   WHERE a.id = ?''',
                (account_id,)
            )
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'id': row[0],
                    'seller_id': row[1],
                    'name': row[2],
                    'price': row[3],
                    'description': row[4],
                    'status': row[5],
                    'seller_name': row[6]
                }
            return None
        except Exception as e:
            print(f"Error getting account: {e}")
            return None
    
    # ===== TRANSACTION METHODS =====
    def add_transaction(self, buyer_id: int, buyer_name: str, seller_id: int,
                       seller_name: str, account_id: str, account_name: str,
                       price: int, commission: int, payment_method: str,
                       buyer_phone: str) -> bool:
        """Add new transaction"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Add transaction
            cursor.execute(
                '''INSERT INTO transactions 
                   (buyer_id, buyer_name, seller_id, seller_name, account_id, 
                    account_name, price, commission, payment_method, buyer_phone)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (buyer_id, buyer_name, seller_id, seller_name, account_id,
                 account_name, price, commission, payment_method, buyer_phone)
            )
            
            # Mark account as sold
            cursor.execute(
                'UPDATE accounts SET status = ? WHERE id = ?',
                ('sold', account_id)
            )
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding transaction: {e}")
            return False
    
    def get_seller_earnings(self, seller_id: int) -> Dict:
        """Get seller earnings"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                '''SELECT COUNT(*), SUM(commission) 
                   FROM transactions WHERE seller_id = ?''',
                (seller_id,)
            )
            row = cursor.fetchone()
            conn.close()
            
            count = row[0] or 0
            total = row[1] or 0
            
            return {'total_sales': count, 'total_earnings': total}
        except Exception as e:
            print(f"Error getting seller earnings: {e}")
            return {'total_sales': 0, 'total_earnings': 0}
    
    def get_all_transactions(self) -> List[Dict]:
        """Get all transactions"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                '''SELECT buyer_id, buyer_name, seller_id, seller_name, 
                          account_name, price, commission, payment_method, created_at
                   FROM transactions ORDER BY created_at DESC'''
            )
            rows = cursor.fetchall()
            conn.close()
            
            transactions = []
            for row in rows:
                transactions.append({
                    'buyer_id': row[0],
                    'buyer_name': row[1],
                    'seller_id': row[2],
                    'seller_name': row[3],
                    'account_name': row[4],
                    'price': row[5],
                    'commission': row[6],
                    'payment_method': row[7],
                    'created_at': row[8]
                })
            return transactions
        except Exception as e:
            print(f"Error getting all transactions: {e}")
            return []
