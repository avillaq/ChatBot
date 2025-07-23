import sqlite3
from datetime import datetime, timedelta

class FinancialDatabase:
    def __init__(self, db_path="financial.db"):
        self.db_path = db_path
        self.init_database()
        self.populate_sample_data()
    
    def init_database(self):
        """Inicializar esquema de base de datos financiera"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabla de cuentas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS accounts (
                account_id INTEGER PRIMARY KEY,
                user_name TEXT NOT NULL,
                balance REAL NOT NULL,
                account_type TEXT NOT NULL,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_access TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                failed_attempts INTEGER DEFAULT 0
            )
        ''')
        
        # Tabla de transacciones
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                transaction_id INTEGER PRIMARY KEY,
                account_id INTEGER,
                amount REAL NOT NULL,
                transaction_type TEXT NOT NULL,
                description TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (account_id) REFERENCES accounts (account_id)
            )
        ''')
        
        # Tabla de alertas críticas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS critical_alerts (
                alert_id INTEGER PRIMARY KEY,
                account_id INTEGER,
                alert_type TEXT NOT NULL,
                message TEXT NOT NULL,
                severity INTEGER NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolved BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (account_id) REFERENCES accounts (account_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def populate_sample_data(self):
        """Poblar con datos de ejemplo"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Verificar si ya hay datos
        cursor.execute("SELECT COUNT(*) FROM accounts")
        if cursor.fetchone()[0] > 0:
            conn.close()
            return
        
        # Crear cuentas de ejemplo
        sample_accounts = [
            ("Juan Pérez", 50.0, "checking"),  # Saldo bajo crítico
            ("Maria Gonzalez", 15000.0, "savings"),
            ("Carlos López", 5.0, "checking"),  # Saldo crítico
            ("Ana Torres", 25000.0, "business")
        ]
        
        cursor.executemany('''
            INSERT INTO accounts (user_name, balance, account_type) 
            VALUES (?, ?, ?)
        ''', sample_accounts)
        
        # Crear transacciones de ejemplo (algunas sospechosas)
        base_time = datetime.now() - timedelta(hours=2)
        sample_transactions = []
        
        for i in range(1, 5):  # Para cada cuenta
            # Transacción normal
            sample_transactions.append((i, -500.0, "withdrawal", "ATM Withdrawal", base_time + timedelta(minutes=i*10)))
            
            # Transacción sospechosa para cuenta 2 (> $10,000 en 24h)
            if i == 2:
                sample_transactions.append((i, -12000.0, "transfer", "Large Transfer", base_time + timedelta(hours=1)))
                sample_transactions.append((i, -8000.0, "withdrawal", "Large Withdrawal", base_time + timedelta(hours=2)))
        
        cursor.executemany('''
            INSERT INTO transactions (account_id, amount, transaction_type, description, timestamp) 
            VALUES (?, ?, ?, ?, ?)
        ''', sample_transactions)
        
        # Simular intentos fallidos de acceso para cuenta 3
        cursor.execute('''
            UPDATE accounts SET failed_attempts = 5 WHERE account_id = 3
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Base de datos inicializada con datos de ejemplo")
    
    def detect_critical_conditions(self):
        """Detectar las 3 condiciones críticas requeridas"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        alerts = []
        
        # 1. CONDICIÓN CRÍTICA: Saldo bajo (< $100)
        cursor.execute('''
            SELECT account_id, user_name, balance 
            FROM accounts 
            WHERE balance < 100
        ''')
        low_balance_accounts = cursor.fetchall()
        
        for account_id, user_name, balance in low_balance_accounts:
            alert = {
                "type": "SALDO_BAJO",
                "account_id": account_id,
                "user_name": user_name,
                "message": f"⚠️ ALERTA CRÍTICA: Saldo bajo para {user_name}: ${balance:.2f}",
                "severity": 8,
                "data": {"balance": balance}
            }
            alerts.append(alert)
            self._save_alert(alert)
        
        # 2. CONDICIÓN CRÍTICA: Transacciones sospechosas (> $10,000 en 24h)
        cursor.execute('''
            SELECT account_id, SUM(ABS(amount)) as total_amount
            FROM transactions 
            WHERE timestamp > datetime('now', '-24 hours')
            AND amount < 0
            GROUP BY account_id
            HAVING total_amount > 10000
        ''')
        suspicious_transactions = cursor.fetchall()
        
        for account_id, total_amount in suspicious_transactions:
            cursor.execute("SELECT user_name FROM accounts WHERE account_id = ?", (account_id,))
            user_name = cursor.fetchone()[0]
            
            alert = {
                "type": "ACTIVIDAD_SOSPECHOSA",
                "account_id": account_id,
                "user_name": user_name,
                "message": f" ALERTA CRÍTICA: Actividad sospechosa para {user_name}: ${total_amount:.2f} en 24h",
                "severity": 9,
                "data": {"total_amount": total_amount}
            }
            alerts.append(alert)
            self._save_alert(alert)
        
        # 3. CONDICIÓN CRÍTICA: Múltiples intentos fallidos (>= 3)
        cursor.execute('''
            SELECT account_id, user_name, failed_attempts 
            FROM accounts 
            WHERE failed_attempts >= 3
        ''')
        failed_attempts = cursor.fetchall()
        
        for account_id, user_name, attempts in failed_attempts:
            alert = {
                "type": "INCIDENTE_DE_SEGURIDAD",
                "account_id": account_id,
                "user_name": user_name,
                "message": f" ALERTA CRÍTICA: {attempts} intentos fallidos para {user_name}",
                "severity": 10,
                "data": {"failed_attempts": attempts}
            }
            alerts.append(alert)
            self._save_alert(alert)
        
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