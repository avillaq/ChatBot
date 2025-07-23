import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.financial_db import FinancialDatabase

def test_financial_database():
    print("🔧 Probando base de datos financiera...")
    
    # Inicializar BD
    db = FinancialDatabase("test_financial.db")
    
    # Probar detección de condiciones críticas
    print("\n Detectando condiciones críticas:")
    alerts = db.detect_critical_conditions()
    
    for alert in alerts:
        print(f"  {alert['message']}")
    
    # Probar consultas
    print("\n💰 Probando consultas de saldo:")
    print(f"  Juan: {db.get_account_balance('Juan')}")
    print(f"  María: {db.get_account_balance('María')}")
    
    print("\n Probando historial de transacciones:")
    print(db.get_recent_transactions('María', 3))
    
    print("\n Probando alertas:")
    print(db.get_all_alerts())
    
    print("\n✅ Pruebas completadas!")

if __name__ == "__main__":
    test_financial_database()