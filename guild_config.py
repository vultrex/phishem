import sqlite3
import threading
from typing import Dict, Any

_DB_PATH = 'guild_config.db'
_DB_LOCK = threading.Lock()

"""
SQL Databases can suck my fat cock
"""

def _get_conn():
    conn = sqlite3.connect(_DB_PATH)
    # Create table with all columns
    conn.execute('''CREATE TABLE IF NOT EXISTS guild_config (
        guild_id TEXT PRIMARY KEY,
        action TEXT NOT NULL DEFAULT 'delete',
        log_channel_id TEXT,
        timeout_duration INTEGER DEFAULT 5,
        anti_phish_enabled BOOLEAN DEFAULT 1,
        anti_malware_enabled BOOLEAN DEFAULT 1,
        anti_piracy_enabled BOOLEAN DEFAULT 0
    )''')
    
    # Ensure all columns exist (for database migration)
    _ensure_columns_exist(conn)
    return conn

def _ensure_columns_exist(conn):
    """Ensure all required columns exist in the database"""
    cursor = conn.cursor()
    
    # Get current columns
    cursor.execute("PRAGMA table_info(guild_config)")
    existing_columns = {row[1] for row in cursor.fetchall()}
    
    # Add missing columns
    required_columns = {
        'timeout_duration': 'INTEGER DEFAULT 5',
        'anti_phish_enabled': 'BOOLEAN DEFAULT 1',
        'anti_malware_enabled': 'BOOLEAN DEFAULT 1',
        'anti_piracy_enabled': 'BOOLEAN DEFAULT 0',
        'bypass_role_ids': 'TEXT DEFAULT ""',
        'max_attempts': 'INTEGER DEFAULT 3',
        'autoresponder_use_embeds': 'BOOLEAN DEFAULT 0',
        'autoresponder_use_reply': 'BOOLEAN DEFAULT 0',
        'autoresponder_embed_title': 'TEXT DEFAULT ""',
        'autoresponder_embed_color': 'TEXT DEFAULT ""',
        'autoresponder_show_rule_name': 'BOOLEAN DEFAULT 1',
        'autoresponder_custom_footer': 'TEXT DEFAULT ""'
    }
    
    for column, definition in required_columns.items():
        if column not in existing_columns:
            try:
                conn.execute(f'ALTER TABLE guild_config ADD COLUMN {column} {definition}')
                print(f"Added missing column: {column}")
            except sqlite3.OperationalError as e:
                if "duplicate column name" not in str(e):
                    print(f"Error adding column {column}: {e}")
    
    conn.commit()

def set_guild_action(guild_id: int, action: str):
    with _DB_LOCK:
        conn = _get_conn()
        conn.execute('REPLACE INTO guild_config (guild_id, action) VALUES (?, ?)', (str(guild_id), action))
        conn.commit()
        conn.close()

def get_guild_action(guild_id: int) -> str:
    with _DB_LOCK:
        conn = _get_conn()
        cur = conn.execute('SELECT action FROM guild_config WHERE guild_id = ?', (str(guild_id),))
        row = cur.fetchone()
        conn.close()
        if row:
            return row[0]
        return 'delete'  # Default action

def set_guild_log_channel(guild_id: int, channel_id: int):
    with _DB_LOCK:
        conn = _get_conn()
        conn.execute('UPDATE guild_config SET log_channel_id = ? WHERE guild_id = ?', (str(channel_id), str(guild_id)))
        if conn.total_changes == 0:
            conn.execute('INSERT INTO guild_config (guild_id, action, log_channel_id) VALUES (?, ?, ?)', (str(guild_id), 'delete', str(channel_id)))
        conn.commit()
        conn.close()

def get_guild_log_channel(guild_id: int) -> int | None:
    with _DB_LOCK:
        conn = _get_conn()
        cur = conn.execute('SELECT log_channel_id FROM guild_config WHERE guild_id = ?', (str(guild_id),))
        row = cur.fetchone()
        conn.close()
        if row and row[0]:
            return int(row[0])
        return None

def set_guild_timeout_duration(guild_id: int, duration_minutes: int):
    with _DB_LOCK:
        conn = _get_conn()
        conn.execute('UPDATE guild_config SET timeout_duration = ? WHERE guild_id = ?', (duration_minutes, str(guild_id)))
        if conn.total_changes == 0:
            conn.execute('INSERT INTO guild_config (guild_id, action, timeout_duration) VALUES (?, ?, ?)', (str(guild_id), 'delete', duration_minutes))
        conn.commit()
        conn.close()

def get_guild_timeout_duration(guild_id: int) -> int:
    with _DB_LOCK:
        conn = _get_conn()
        cur = conn.execute('SELECT timeout_duration FROM guild_config WHERE guild_id = ?', (str(guild_id),))
        row = cur.fetchone()
        conn.close()
        if row and row[0]:
            return int(row[0])
        return 5  # Default: 5 minutes timeout

def set_guild_anti_phish_enabled(guild_id: int, enabled: bool):
    with _DB_LOCK:
        conn = _get_conn()
        conn.execute('UPDATE guild_config SET anti_phish_enabled = ? WHERE guild_id = ?', (enabled, str(guild_id)))
        if conn.total_changes == 0:
            conn.execute('INSERT INTO guild_config (guild_id, action, anti_phish_enabled) VALUES (?, ?, ?)', (str(guild_id), 'delete', enabled))
        conn.commit()
        conn.close()

def get_guild_anti_phish_enabled(guild_id: int) -> bool:
    with _DB_LOCK:
        conn = _get_conn()
        cur = conn.execute('SELECT anti_phish_enabled FROM guild_config WHERE guild_id = ?', (str(guild_id),))
        row = cur.fetchone()
        conn.close()
        if row and row[0] is not None:
            return bool(row[0])
        return True  # Default: enabled

def set_guild_anti_malware_enabled(guild_id: int, enabled: bool):
    with _DB_LOCK:
        conn = _get_conn()
        conn.execute('UPDATE guild_config SET anti_malware_enabled = ? WHERE guild_id = ?', (enabled, str(guild_id)))
        if conn.total_changes == 0:
            conn.execute('INSERT INTO guild_config (guild_id, action, anti_malware_enabled) VALUES (?, ?, ?)', (str(guild_id), 'delete', enabled))
        conn.commit()
        conn.close()

def get_guild_anti_malware_enabled(guild_id: int) -> bool:
    with _DB_LOCK:
        conn = _get_conn()
        cur = conn.execute('SELECT anti_malware_enabled FROM guild_config WHERE guild_id = ?', (str(guild_id),))
        row = cur.fetchone()
        conn.close()
        if row and row[0] is not None:
            return bool(row[0])
        return True  # Default: enabled

def set_guild_anti_piracy_enabled(guild_id: int, enabled: bool):
    with _DB_LOCK:
        conn = _get_conn()
        conn.execute('UPDATE guild_config SET anti_piracy_enabled = ? WHERE guild_id = ?', (enabled, str(guild_id)))
        if conn.total_changes == 0:
            conn.execute('INSERT INTO guild_config (guild_id, action, anti_piracy_enabled) VALUES (?, ?, ?)', (str(guild_id), 'delete', enabled))
        conn.commit()
        conn.close()

def get_guild_anti_piracy_enabled(guild_id: int) -> bool:
    with _DB_LOCK:
        conn = _get_conn()
        cur = conn.execute('SELECT anti_piracy_enabled FROM guild_config WHERE guild_id = ?', (str(guild_id),))
        row = cur.fetchone()
        conn.close()
        if row and row[0] is not None:
            return bool(row[0])
        return False  # Default: disabled

def get_guild_full_config(guild_id: int) -> dict:
    """Get all configuration for a guild"""
    with _DB_LOCK:
        conn = _get_conn()
        cur = conn.execute('''SELECT action, log_channel_id, timeout_duration, anti_phish_enabled, anti_malware_enabled, anti_piracy_enabled, bypass_role_ids, max_attempts, autoresponder_use_embeds, autoresponder_use_reply, autoresponder_embed_title, autoresponder_embed_color, autoresponder_show_rule_name, autoresponder_custom_footer
                             FROM guild_config WHERE guild_id = ?''', (str(guild_id),))
        row = cur.fetchone()
        conn.close()
        if row:
            return {
                'action': row[0] or 'delete',
                'log_channel_id': int(row[1]) if row[1] else None,
                'timeout_duration': int(row[2]) if row[2] else 0,
                'anti_phish_enabled': bool(row[3]) if row[3] is not None else True,
                'anti_malware_enabled': bool(row[4]) if row[4] is not None else True,
                'anti_piracy_enabled': bool(row[5]) if row[5] is not None else False,
                'bypass_role_ids': [int(r) for r in (row[6] or '').split(',') if r.strip().isdigit()],
                'max_attempts': int(row[7]) if row[7] is not None else 3,
                'autoresponder_use_embeds': bool(row[8]) if row[8] is not None else False,
                'autoresponder_use_reply': bool(row[9]) if row[9] is not None else False,
                'autoresponder_embed_title': row[10] or "",
                'autoresponder_embed_color': row[11] or "",
                'autoresponder_show_rule_name': bool(row[12]) if row[12] is not None else True,
                'autoresponder_custom_footer': row[13] or ""
            }
        else:
            return {
                'action': 'delete',
                'log_channel_id': None,
                'timeout_duration': 0,
                'anti_phish_enabled': True,
                'anti_malware_enabled': True,
                'anti_piracy_enabled': False,
                'bypass_role_ids': [],
                'max_attempts': 3,
                'autoresponder_use_embeds': False,
                'autoresponder_use_reply': False,
                'autoresponder_embed_title': "",
                'autoresponder_embed_color': "",
                'autoresponder_show_rule_name': True,
                'autoresponder_custom_footer': ""
            }

# New: Set/get bypass roles
def set_guild_bypass_roles(guild_id: int, role_ids: list[int]):
    with _DB_LOCK:
        conn = _get_conn()
        role_ids_str = ','.join(str(r) for r in role_ids)
        conn.execute('UPDATE guild_config SET bypass_role_ids = ? WHERE guild_id = ?', (role_ids_str, str(guild_id)))
        if conn.total_changes == 0:
            conn.execute('INSERT INTO guild_config (guild_id, action, bypass_role_ids) VALUES (?, ?, ?)', (str(guild_id), 'delete', role_ids_str))
        conn.commit()
        conn.close()

def get_guild_bypass_roles(guild_id: int) -> list[int]:
    with _DB_LOCK:
        conn = _get_conn()
        cur = conn.execute('SELECT bypass_role_ids FROM guild_config WHERE guild_id = ?', (str(guild_id),))
        row = cur.fetchone()
        conn.close()
        if row and row[0]:
            return [int(r) for r in row[0].split(',') if r.strip().isdigit()]
        return []

# New: Set/get max attempts
def set_guild_max_attempts(guild_id: int, max_attempts: int):
    with _DB_LOCK:
        conn = _get_conn()
        conn.execute('UPDATE guild_config SET max_attempts = ? WHERE guild_id = ?', (max_attempts, str(guild_id)))
        if conn.total_changes == 0:
            conn.execute('INSERT INTO guild_config (guild_id, action, max_attempts) VALUES (?, ?, ?)', (str(guild_id), 'delete', max_attempts))
        conn.commit()
        conn.close()

def get_guild_max_attempts(guild_id: int) -> int:
    with _DB_LOCK:
        conn = _get_conn()
        cur = conn.execute('SELECT max_attempts FROM guild_config WHERE guild_id = ?', (str(guild_id),))
        row = cur.fetchone()
        conn.close()
        if row and row[0]:
            return int(row[0])
        return 3


# New: Autoresponder format settings
def set_guild_autoresponder_use_embeds(guild_id: int, use_embeds: bool):
    with _DB_LOCK:
        conn = _get_conn()
        conn.execute('UPDATE guild_config SET autoresponder_use_embeds = ? WHERE guild_id = ?', (use_embeds, str(guild_id)))
        if conn.total_changes == 0:
            conn.execute('INSERT INTO guild_config (guild_id, action, autoresponder_use_embeds) VALUES (?, ?, ?)', (str(guild_id), 'delete', use_embeds))
        conn.commit()
        conn.close()

def get_guild_autoresponder_use_embeds(guild_id: int) -> bool:
    with _DB_LOCK:
        conn = _get_conn()
        cur = conn.execute('SELECT autoresponder_use_embeds FROM guild_config WHERE guild_id = ?', (str(guild_id),))
        row = cur.fetchone()
        conn.close()
        if row and row[0] is not None:
            return bool(row[0])
        return False  # Default: plain text

def set_guild_autoresponder_use_reply(guild_id: int, use_reply: bool):
    with _DB_LOCK:
        conn = _get_conn()
        conn.execute('UPDATE guild_config SET autoresponder_use_reply = ? WHERE guild_id = ?', (use_reply, str(guild_id)))
        if conn.total_changes == 0:
            conn.execute('INSERT INTO guild_config (guild_id, action, autoresponder_use_reply) VALUES (?, ?, ?)', (str(guild_id), 'delete', use_reply))
        conn.commit()
        conn.close()

def get_guild_autoresponder_use_reply(guild_id: int) -> bool:
    with _DB_LOCK:
        conn = _get_conn()
        cur = conn.execute('SELECT autoresponder_use_reply FROM guild_config WHERE guild_id = ?', (str(guild_id),))
        row = cur.fetchone()
        conn.close()
        if row and row[0] is not None:
            return bool(row[0])
        return False  # Default: no reply


# Autoresponder embed configuration
def set_guild_autoresponder_embed_config(guild_id: int, title: str = "", color: str = "", show_rule_name: bool = True, custom_footer: str = ""):
    with _DB_LOCK:
        conn = _get_conn()
        conn.execute('''UPDATE guild_config SET 
                       autoresponder_embed_title = ?, 
                       autoresponder_embed_color = ?, 
                       autoresponder_show_rule_name = ?, 
                       autoresponder_custom_footer = ? 
                       WHERE guild_id = ?''', 
                    (title, color, show_rule_name, custom_footer, str(guild_id)))
        if conn.total_changes == 0:
            conn.execute('''INSERT INTO guild_config 
                           (guild_id, action, autoresponder_embed_title, autoresponder_embed_color, autoresponder_show_rule_name, autoresponder_custom_footer) 
                           VALUES (?, ?, ?, ?, ?, ?)''', 
                        (str(guild_id), 'delete', title, color, show_rule_name, custom_footer))
        conn.commit()
        conn.close()

def get_guild_autoresponder_embed_config(guild_id: int) -> Dict[str, Any]:
    with _DB_LOCK:
        conn = _get_conn()
        cur = conn.execute('''SELECT autoresponder_embed_title, autoresponder_embed_color, 
                             autoresponder_show_rule_name, autoresponder_custom_footer 
                             FROM guild_config WHERE guild_id = ?''', (str(guild_id),))
        row = cur.fetchone()
        conn.close()
        if row:
            return {
                'title': row[0] or "",
                'color': row[1] or "",
                'show_rule_name': bool(row[2]) if row[2] is not None else True,
                'custom_footer': row[3] or ""
            }
        return {
            'title': "",
            'color': "",
            'show_rule_name': True,
            'custom_footer': ""
        }


# Autoresponder functionality
def _get_autoresponder_conn():
    """Get database connection for autoresponder rules"""
    conn = sqlite3.connect(_DB_PATH)
    # Create autoresponder rules table (now supports multiple triggers as comma-separated string)
    conn.execute('''CREATE TABLE IF NOT EXISTS autoresponder_rules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        guild_id TEXT NOT NULL,
        rule_name TEXT NOT NULL,
        trigger_patterns TEXT NOT NULL,  -- comma-separated triggers
        response_message TEXT NOT NULL,
        is_regex BOOLEAN DEFAULT 0,
        is_enabled BOOLEAN DEFAULT 1,
        case_sensitive BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(guild_id, rule_name)
    )''')
    
    # Migrate existing autoresponder rules if needed
    _migrate_autoresponder_schema(conn)
    
    # Create autoresponder cooldowns table
    conn.execute('''CREATE TABLE IF NOT EXISTS autoresponder_cooldowns (
        guild_id TEXT NOT NULL,
        user_id TEXT NOT NULL,
        rule_id INTEGER NOT NULL,
        last_triggered TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (guild_id, user_id, rule_id)
    )''')
    
    return conn

def _migrate_autoresponder_schema(conn):
    """Migrate autoresponder schema from old to new format"""
    try:
        # Check if old column exists
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(autoresponder_rules)")
        columns = {row[1] for row in cursor.fetchall()}
        
        if 'trigger_pattern' in columns and 'trigger_patterns' not in columns:
            print("Migrating autoresponder schema from trigger_pattern to trigger_patterns...")
            # Rename the old column to the new column name
            conn.execute('ALTER TABLE autoresponder_rules RENAME COLUMN trigger_pattern TO trigger_patterns')
            conn.commit()
            print("Schema migration completed successfully.")
    except Exception as e:
        print(f"Schema migration failed or not needed: {e}")

def add_autoresponder_rule(guild_id: int, rule_name: str, trigger_pattern: str, 
                          response_message: str, is_regex: bool = False, 
                          case_sensitive: bool = False) -> bool:
    """Add a new autoresponder rule for a guild. Accepts trigger_pattern as a string or list of strings."""
    with _DB_LOCK:
        try:
            conn = _get_autoresponder_conn()
            # Support both string and list for trigger_pattern
            if isinstance(trigger_pattern, list):
                trigger_patterns = ','.join(trigger_pattern)
            else:
                trigger_patterns = trigger_pattern
            conn.execute('''INSERT INTO autoresponder_rules 
                           (guild_id, rule_name, trigger_patterns, response_message, is_regex, case_sensitive)
                           VALUES (?, ?, ?, ?, ?, ?)''',
                        (str(guild_id), rule_name, trigger_patterns, response_message, is_regex, case_sensitive))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            conn.close()
            return False  # Rule name already exists

def remove_autoresponder_rule(guild_id: int, rule_name: str) -> bool:
    """Remove an autoresponder rule from a guild"""
    with _DB_LOCK:
        conn = _get_autoresponder_conn()
        cursor = conn.execute('DELETE FROM autoresponder_rules WHERE guild_id = ? AND rule_name = ?',
                             (str(guild_id), rule_name))
        changes = cursor.rowcount
        conn.commit()
        conn.close()
        return changes > 0

def get_autoresponder_rules(guild_id: int) -> list[dict]:
    """Get all autoresponder rules for a guild"""
    with _DB_LOCK:
        conn = _get_autoresponder_conn()
        cursor = conn.execute('''SELECT id, rule_name, trigger_patterns, response_message, 
                                is_regex, is_enabled, case_sensitive, created_at
                                FROM autoresponder_rules 
                                WHERE guild_id = ? AND is_enabled = 1
                                ORDER BY rule_name''', (str(guild_id),))
        rows = cursor.fetchall()
        conn.close()
        rules = []
        for row in rows:
            triggers = [t.strip() for t in row[2].split(',') if t.strip()]
            rules.append({
                'id': row[0],
                'rule_name': row[1],
                'trigger_patterns': triggers,
                'response_message': row[3],
                'is_regex': bool(row[4]),
                'is_enabled': bool(row[5]),
                'case_sensitive': bool(row[6]),
                'created_at': row[7]
            })
        return rules

def toggle_autoresponder_rule(guild_id: int, rule_name: str, enabled: bool) -> bool:
    """Enable or disable an autoresponder rule"""
    with _DB_LOCK:
        conn = _get_autoresponder_conn()
        cursor = conn.execute('UPDATE autoresponder_rules SET is_enabled = ? WHERE guild_id = ? AND rule_name = ?',
                             (enabled, str(guild_id), rule_name))
        changes = cursor.rowcount
        conn.commit()
        conn.close()
        return changes > 0

def get_autoresponder_rule_count(guild_id: int) -> int:
    """Get the number of autoresponder rules for a guild"""
    with _DB_LOCK:
        conn = _get_autoresponder_conn()
        cursor = conn.execute('SELECT COUNT(*) FROM autoresponder_rules WHERE guild_id = ?', (str(guild_id),))
        count = cursor.fetchone()[0]
        conn.close()
        return count

def check_autoresponder_cooldown(guild_id: int, user_id: int, rule_id: int, cooldown_seconds: int = 5) -> bool:
    """Check if user is on cooldown for a specific rule"""
    with _DB_LOCK:
        conn = _get_autoresponder_conn()
        cursor = conn.execute('''SELECT last_triggered FROM autoresponder_cooldowns 
                                WHERE guild_id = ? AND user_id = ? AND rule_id = ?''',
                             (str(guild_id), str(user_id), rule_id))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return False  # No cooldown record, not on cooldown
        
        from datetime import datetime, timedelta
        last_triggered = datetime.fromisoformat(row[0])
        now = datetime.now()
        conn.close()
        
        return (now - last_triggered).total_seconds() < cooldown_seconds

def set_autoresponder_cooldown(guild_id: int, user_id: int, rule_id: int):
    """Set cooldown for a user and rule"""
    with _DB_LOCK:
        conn = _get_autoresponder_conn()
        conn.execute('''INSERT OR REPLACE INTO autoresponder_cooldowns 
                       (guild_id, user_id, rule_id, last_triggered)
                       VALUES (?, ?, ?, CURRENT_TIMESTAMP)''',
                    (str(guild_id), str(user_id), rule_id))
        conn.commit()
        conn.close()

def edit_autoresponder_rule(guild_id: int, rule_name: str, new_trigger_pattern: str | None = None, 
                          new_response_message: str | None = None, new_is_regex: bool | None = None, 
                          new_case_sensitive: bool | None = None, new_trigger_patterns: list[str] | None = None) -> bool:
    """Edit an existing autoresponder rule for a guild. Accepts new_trigger_pattern (str), or new_trigger_patterns (list of str)."""
    with _DB_LOCK:
        try:
            conn = _get_autoresponder_conn()
            # Build dynamic update query based on provided parameters
            update_fields = []
            update_values = []
            # Support both new_trigger_pattern (str) and new_trigger_patterns (list)
            if new_trigger_patterns is not None:
                triggers = ','.join(new_trigger_patterns)
                update_fields.append("trigger_patterns = ?")
                update_values.append(triggers)
            elif new_trigger_pattern is not None:
                update_fields.append("trigger_patterns = ?")
                update_values.append(new_trigger_pattern)
            if new_response_message is not None:
                update_fields.append("response_message = ?")
                update_values.append(new_response_message)
            if new_is_regex is not None:
                update_fields.append("is_regex = ?")
                update_values.append(new_is_regex)
            if new_case_sensitive is not None:
                update_fields.append("case_sensitive = ?")
                update_values.append(new_case_sensitive)
            if not update_fields:
                conn.close()
                return False  # Nothing to update
            # Add WHERE conditions
            update_values.extend([str(guild_id), rule_name])
            query = f"UPDATE autoresponder_rules SET {', '.join(update_fields)} WHERE guild_id = ? AND rule_name = ?"
            cursor = conn.execute(query, update_values)
            changes = cursor.rowcount
            conn.commit()
            conn.close()
            return changes > 0
        except Exception:
            conn.close()
            return False
