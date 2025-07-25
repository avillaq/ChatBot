import sqlite3
import os
from datetime import datetime, timedelta
import random

class FinancialDatabase:
    """Base de datos financiera con datos específicos por nodo"""
    
    def __init__(self, db_path="financial.db", node_id="main"):
        self.db_path = db_path
        self.node_id = node_id
        self.init_database()
        self.populate_node_specific_data()
    
    def init_database(self):
        """Inicializar esquema de base de datos"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabla de cuentas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                balance REAL NOT NULL,
                account_type TEXT DEFAULT 'checking',
                created_date TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla de transacciones
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY,
                from_account INTEGER,
                to_account INTEGER,
                amount REAL NOT NULL,
                transaction_date TEXT NOT NULL,
                description TEXT,
                type TEXT DEFAULT 'transfer',
                FOREIGN KEY (from_account) REFERENCES accounts (id),
                FOREIGN KEY (to_account) REFERENCES accounts (id)
            )
        ''')
        
        # Tabla de intentos de acceso
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS access_attempts (
                id INTEGER PRIMARY KEY,
                account_id INTEGER,
                attempt_time TEXT NOT NULL,
                success BOOLEAN NOT NULL,
                ip_address TEXT,
                FOREIGN KEY (account_id) REFERENCES accounts (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        print(f"✅ Base de datos inicializada: {self.db_path}")
    
    def populate_node_specific_data(self):
        """Poblar base de datos con datos específicos del nodo"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Verificar si ya hay datos
        cursor.execute("SELECT COUNT(*) FROM accounts")
        if cursor.fetchone()[0] > 0:
            conn.close()
            return  # Ya hay datos
        
        # Datos específicos por nodo
        if "main" in self.node_id.lower() or "8000" in str(self.node_id):
            self.populate_main_bank_data(cursor)
        elif "nacional" in self.node_id.lower() or "8001" in str(self.node_id):
            self.populate_nacional_bank_data(cursor)
        elif "central" in self.node_id.lower() or "8002" in str(self.node_id):
            self.populate_central_bank_data(cursor)
        elif "regional" in self.node_id.lower() or "8003" in str(self.node_id):
            self.populate_regional_bank_data(cursor)
        else:
            self.populate_default_data(cursor)
        
        conn.commit()
        conn.close()
        print(f"✅ Datos específicos poblados para {self.node_id}")
    
    def populate_main_bank_data(self, cursor):
        """Datos para Banco Principal (Nodo Main)"""
        # Cuentas con problemas críticos
        accounts = [
            (1, 'Juan', 'Pérez', 45.00, 'checking'),
            (2, 'María', 'García', 25000.00, 'checking'),
            (3, 'Carlos', 'López', 15.00, 'savings'),
            (4, 'Ana', 'Martínez', 85.00, 'checking'),
            (5, 'Luis', 'Rodríguez', 50000.00, 'business')
        ]
        
        cursor.executemany(
            "INSERT INTO accounts (id, first_name, last_name, balance, account_type) VALUES (?, ?, ?, ?, ?)",
            accounts
        )
        
        # Transacciones sospechosas
        transactions = [
            (1, 2, 1, 20000.00, '2024-01-15 10:30:00', 'Transferencia urgente', 'transfer'),
            (2, 5, 2, 15000.00, '2024-01-15 14:20:00', 'Pago comercial', 'transfer'),
            (3, 2, 3, 500.00, '2024-01-14 09:15:00', 'Transferencia regular', 'transfer'),
            (4, 1, 4, 30.00, '2024-01-13 16:45:00', 'Pago pequeño', 'transfer')
        ]
        
        cursor.executemany(
            "INSERT INTO transactions (id, from_account, to_account, amount, transaction_date, description, type) VALUES (?, ?, ?, ?, ?, ?, ?)",
            transactions
        )
        
        # Intentos fallidos
        failed_attempts = [
            (1, 3, '2024-01-15 08:00:00', False, '192.168.1.100'),
            (2, 3, '2024-01-15 08:05:00', False, '192.168.1.100'),
            (3, 3, '2024-01-15 08:10:00', False, '192.168.1.100'),
            (4, 1, '2024-01-15 09:00:00', False, '192.168.1.200'),
            (5, 1, '2024-01-15 09:05:00', False, '192.168.1.200')
        ]
        
        cursor.executemany(
            "INSERT INTO access_attempts (id, account_id, attempt_time, success, ip_address) VALUES (?, ?, ?, ?, ?)",
            failed_attempts
        )
    
    def populate_nacional_bank_data(self, cursor):
        """Datos para Banco Nacional"""
        accounts = [
            (1, 'Roberto', 'Silva', 75.00, 'checking'),
            (2, 'Carmen', 'Torres', 12000.00, 'savings'),
            (3, 'Diego', 'Vargas', 95.00, 'checking'),
            (4, 'Lucía', 'Morales', 35000.00, 'business'),
            (5, 'Fernando', 'Castro', 25.00, 'checking')
        ]
        
        cursor.executemany(
            "INSERT INTO accounts (id, first_name, last_name, balance, account_type) VALUES (?, ?, ?, ?, ?)",
            accounts
        )
        
        transactions = [
            (1, 4, 2, 18000.00, '2024-01-15 11:30:00', 'Inversión comercial', 'transfer'),
            (2, 2, 1, 200.00, '2024-01-14 15:20:00', 'Pago servicios', 'transfer'),
            (3, 3, 5, 70.00, '2024-01-13 10:15:00', 'Transferencia familiar', 'transfer')
        ]
        
        cursor.executemany(
            "INSERT INTO transactions (id, from_account, to_account, amount, transaction_date, description, type) VALUES (?, ?, ?, ?, ?, ?, ?)",
            transactions
        )
        
        failed_attempts = [
            (1, 1, '2024-01-15 07:30:00', False, '10.0.0.50'),
            (2, 1, '2024-01-15 07:35:00', False, '10.0.0.50'),
            (3, 1, '2024-01-15 07:40:00', False, '10.0.0.50'),
            (4, 5, '2024-01-14 20:00:00', False, '10.0.0.75')
        ]
        
        cursor.executemany(
            "INSERT INTO access_attempts (id, account_id, attempt_time, success, ip_address) VALUES (?, ?, ?, ?, ?)",
            failed_attempts
        )
    
    def populate_central_bank_data(self, cursor):
        """Datos para Banco Central"""
        accounts = [
            (1, 'Patricia', 'Jiménez', 60.00, 'checking'),
            (2, 'Miguel', 'Hernández', 8500.00, 'savings'),
            (3, 'Sandra', 'Ruiz', 120000.00, 'business'),
            (4, 'Andrés', 'Gutiérrez', 90.00, 'checking'),
            (5, 'Valeria', 'Mendoza', 40.00, 'savings')
        ]
        
        cursor.executemany(
            "INSERT INTO accounts (id, first_name, last_name, balance, account_type) VALUES (?, ?, ?, ?, ?)",
            accounts
        )
        
        transactions = [
            (1, 3, 2, 25000.00, '2024-01-15 13:45:00', 'Operación empresarial', 'transfer'),
            (2, 2, 4, 300.00, '2024-01-14 12:30:00', 'Pago regular', 'transfer'),
            (3, 1, 5, 20.00, '2024-01-13 14:20:00', 'Transferencia pequeña', 'transfer')
        ]
        
        cursor.executemany(
            "INSERT INTO transactions (id, from_account, to_account, amount, transaction_date, description, type) VALUES (?, ?, ?, ?, ?, ?, ?)",
            transactions
        )
        
        failed_attempts = [
            (1, 4, '2024-01-15 06:00:00', False, '172.16.0.10'),
            (2, 4, '2024-01-15 06:05:00', False, '172.16.0.10'),
            (3, 4, '2024-01-15 06:10:00', False, '172.16.0.10')
        ]
        
        cursor.executemany(
            "INSERT INTO access_attempts (id, account_id, attempt_time, success, ip_address) VALUES (?, ?, ?, ?, ?)",
            failed_attempts
        )
    
    def populate_regional_bank_data(self, cursor):
        """Datos para Banco Regional"""
        accounts = [
            (1, 'Alejandro', 'Vega', 55.00, 'checking'),
            (2, 'Mónica', 'Paredes', 18000.00, 'savings'),
            (3, 'Javier', 'Ramos', 75000.00, 'business'),
            (4, 'Elena', 'Soto', 35.00, 'checking'),
            (5, 'Ricardo', 'Flores', 95.00, 'savings')
        ]
        
        cursor.executemany(
            "INSERT INTO accounts (id, first_name, last_name, balance, account_type) VALUES (?, ?, ?, ?, ?)",
            accounts
        )
        
        transactions = [
            (1, 3, 2, 12000.00, '2024-01-15 16:20:00', 'Pago corporativo', 'transfer'),
            (2, 2, 1, 100.00, '2024-01-14 11:40:00', 'Transferencia personal', 'transfer'),
            (3, 5, 4, 60.00, '2024-01-13 13:30:00', 'Pago entre cuentas', 'transfer')
        ]
        
        cursor.executemany(
            "INSERT INTO transactions (id, from_account, to_account, amount, transaction_date, description, type) VALUES (?, ?, ?, ?, ?, ?, ?)",
            transactions
        )
        
        failed_attempts = [
            (1, 1, '2024-01-15 05:30:00', False, '192.168.100.25'),
            (2, 1, '2024-01-15 05:35:00', False, '192.168.100.25'),
            (3, 1, '2024-01-15 05:40:00', False, '192.168.100.25'),
            (4, 4, '2024-01-14 22:00:00', False, '192.168.100.30'),
            (5, 4, '2024-01-14 22:05:00', False, '192.168.100.30')
        ]
        
        cursor.executemany(
            "INSERT INTO access_attempts (id, account_id, attempt_time, success, ip_address) VALUES (?, ?, ?, ?, ?)",
            failed_attempts
        )
    
    def populate_default_data(self, cursor):
        """Datos por defecto para nodos no específicos"""
        accounts = [
            (1, 'Usuario', 'Demo', 80.00, 'checking'),
            (2, 'Cliente', 'Ejemplo', 15000.00, 'savings'),
            (3, 'Empresa', 'Test', 45000.00, 'business')
        ]
        
        cursor.executemany(
            "INSERT INTO accounts (id, first_name, last_name, balance, account_type) VALUES (?, ?, ?, ?, ?)",
            accounts
        )
    
    def detect_critical_conditions(self):
        """Detectar condiciones críticas en la base de datos del nodo"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        alerts = []
        
        # 1. Saldos críticos (< $100)
        cursor.execute("""
            SELECT id, first_name, last_name, balance 
            FROM accounts 
            WHERE balance < 100
        """)
        
        low_balance_accounts = cursor.fetchall()
        for account in low_balance_accounts:
            alerts.append({
                'type': 'low_balance',
                'account_id': account[0],
                'account_name': f"{account[1]} {account[2]}",
                'balance': account[3],
                'message': f"Saldo crítico: {account[1]} {account[2]} tiene ${account[3]:.2f}",
                'severity': 'high',
                'node_id': self.node_id
            })
        
        # 2. Transacciones sospechosas (> $10,000 en las últimas 24 horas)
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute("""
            SELECT t.id, t.amount, a1.first_name, a1.last_name, t.transaction_date
            FROM transactions t
            JOIN accounts a1 ON t.from_account = a1.id
            WHERE t.amount > 10000 AND t.transaction_date > ?
        """, (yesterday,))
        
        suspicious_transactions = cursor.fetchall()
        for transaction in suspicious_transactions:
            alerts.append({
                'type': 'suspicious_activity',
                'transaction_id': transaction[0],
                'amount': transaction[1],
                'account_name': f"{transaction[2]} {transaction[3]}",
                'date': transaction[4],
                'message': f"Transacción sospechosa: ${transaction[1]:,.2f} por {transaction[2]} {transaction[3]}",
                'severity': 'critical',
                'node_id': self.node_id
            })
        
        # 3. Intentos fallidos de acceso (≥ 3 intentos en las últimas 24 horas)
        cursor.execute("""
            SELECT account_id, COUNT(*) as failed_count, a.first_name, a.last_name
            FROM access_attempts aa
            JOIN accounts a ON aa.account_id = a.id
            WHERE aa.success = 0 AND aa.attempt_time > ?
            GROUP BY account_id
            HAVING failed_count >= 3
        """, (yesterday,))
        
        failed_access = cursor.fetchall()
        for access in failed_access:
            alerts.append({
                'type': 'failed_access',
                'account_id': access[0],
                'failed_attempts': access[1],
                'account_name': f"{access[2]} {access[3]}",
                'message': f"Múltiples intentos fallidos: {access[1]} intentos en cuenta de {access[2]} {access[3]}",
                'severity': 'high',
                'node_id': self.node_id
            })
        
        conn.close()
        return alerts
    
    def _save_alert(self, alert):
        """Guardar alerta en la base de datos"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO critical_alerts (account_id, alert_type, message, severity)
            VALUES (?, ?, ?, ?)
        ''', (alert["account_id"], alert["type"], alert["message"], alert["severity"]))
        
        conn.commit()
        conn.close()
    
    def get_account_balance(self, account_name):
        """Consulta de saldo por nombre"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT balance, account_type 
            FROM accounts 
            WHERE LOWER(user_name) LIKE LOWER(?)
        ''', (f'%{account_name}%',))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            balance, account_type = result
            return f"Saldo actual: ${balance:.2f} (Cuenta {account_type})"
        else:
            return "Cuenta no encontrada"
    
    def get_recent_transactions(self, account_name, limit=5):
        """Obtener transacciones recientes"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT t.amount, t.transaction_type, t.description, t.timestamp
            FROM transactions t
            JOIN accounts a ON t.account_id = a.account_id
            WHERE LOWER(a.user_name) LIKE LOWER(?)
            ORDER BY t.timestamp DESC
            LIMIT ?
        ''', (f'%{account_name}%', limit))
        
        transactions = cursor.fetchall()
        conn.close()
        
        if transactions:
            result = "Transacciones recientes:\n"
            for amount, trans_type, description, timestamp in transactions:
                result += f"• ${amount:.2f} - {description} ({timestamp})\n"
            return result
        else:
            return "No se encontraron transacciones"
    
    def get_all_alerts(self):
        """Obtener todas las alertas críticas"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT alert_type, message, severity, timestamp
            FROM critical_alerts
            WHERE resolved = FALSE
            ORDER BY severity DESC, timestamp DESC
        ''')
        
        alerts = cursor.fetchall()
        conn.close()
        
        if alerts:
            result = " ALERTAS CRÍTICAS ACTIVAS:\n"
            for alert_type, message, severity, timestamp in alerts:
                result += f"• {message} (Severidad: {severity})\n"
            return result
        else:
            return "✅ No hay alertas críticas activas"

# Función de prueba
if __name__ == "__main__":
    print("🔧 Inicializando base de datos financiera...")
    db = FinancialDatabase()
    
    print("\n Detectando condiciones críticas...")
    alerts = db.detect_critical_conditions()
    
    for alert in alerts:
        print(f"⚠️ {alert['message']}")
    
    print(f"\n✅ Base de datos configurada con {len(alerts)} alertas críticas")