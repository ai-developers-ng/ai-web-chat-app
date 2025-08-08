#!/usr/bin/env python3

import sqlite3
import sys
from datetime import datetime

def query_database(db_path="instance/ai_web_app.db"):
    """Query the ai_web_app.db database"""
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=" * 60)
        print("AI WEB APP DATABASE QUERY TOOL")
        print("=" * 60)
        
        # Show all tables
        print("\n📋 TABLES:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        for table in tables:
            print(f"  • {table[0]}")
        
        # Query users
        print("\n👥 USERS:")
        cursor.execute("""
            SELECT id, username, email, is_admin, is_active, created_at, last_login 
            FROM users ORDER BY created_at DESC
        """)
        users = cursor.fetchall()
        
        print(f"{'ID':<3} {'Username':<15} {'Email':<25} {'Admin':<6} {'Active':<6} {'Created':<20} {'Last Login':<20}")
        print("-" * 100)
        
        for user in users:
            admin_status = "✅ Yes" if user[3] else "❌ No"
            active_status = "✅ Yes" if user[4] else "❌ No"
            created = user[5][:19] if user[5] else "N/A"
            last_login = user[6][:19] if user[6] else "Never"
            
            print(f"{user[0]:<3} {user[1]:<15} {user[2]:<25} {admin_status:<6} {active_status:<6} {created:<20} {last_login:<20}")
        
        # Query signup codes
        print("\n🔑 SIGNUP CODES:")
        cursor.execute("""
            SELECT code, expires_at, used_by_user_id, created_at 
            FROM signup_codes ORDER BY created_at DESC LIMIT 5
        """)
        codes = cursor.fetchall()
        
        print(f"{'Code':<35} {'Expires':<20} {'Used By':<8} {'Created':<20}")
        print("-" * 85)
        
        for code in codes:
            expires = code[1][:19] if code[1] else "N/A"
            used_by = str(code[2]) if code[2] else "Unused"
            created = code[3][:19] if code[3] else "N/A"
            
            print(f"{code[0]:<35} {expires:<20} {used_by:<8} {created:<20}")
        
        # Query recent login logs
        print("\n🔐 RECENT LOGIN LOGS:")
        cursor.execute("""
            SELECT username_attempted, success, ip_address, login_time, failure_reason 
            FROM login_logs ORDER BY login_time DESC LIMIT 5
        """)
        logs = cursor.fetchall()
        
        print(f"{'Username':<15} {'Success':<8} {'IP Address':<15} {'Login Time':<20} {'Failure Reason':<15}")
        print("-" * 80)
        
        for log in logs:
            success = "✅ Yes" if log[1] else "❌ No"
            login_time = log[3][:19] if log[3] else "N/A"
            failure = log[4] if log[4] else "N/A"
            
            print(f"{log[0]:<15} {success:<8} {log[2]:<15} {login_time:<20} {failure:<15}")
        
        # Query recent user actions
        print("\n📊 RECENT USER ACTIONS:")
        cursor.execute("""
            SELECT u.username, ua.action_type, ua.ip_address, ua.timestamp 
            FROM user_actions ua 
            JOIN users u ON ua.user_id = u.id 
            ORDER BY ua.timestamp DESC LIMIT 5
        """)
        actions = cursor.fetchall()
        
        print(f"{'Username':<15} {'Action':<20} {'IP Address':<15} {'Timestamp':<20}")
        print("-" * 75)
        
        for action in actions:
            timestamp = action[3][:19] if action[3] else "N/A"
            print(f"{action[0]:<15} {action[1]:<20} {action[2]:<15} {timestamp:<20}")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

def custom_query(query, db_path="instance/ai_web_app.db"):
    """Execute a custom SQL query"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        print(f"\n📝 Query: {query}")
        print("Results:")
        for row in results:
            print(row)
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Custom query mode
        query = " ".join(sys.argv[1:])
        custom_query(query)
    else:
        # Default overview mode
        query_database()
