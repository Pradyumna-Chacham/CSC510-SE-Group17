import sqlite3
import os
import json
from datetime import datetime
from typing import List, Dict, Optional

def get_db_path():
    return os.path.join(os.path.dirname(__file__), "requirements.db")

def init_db():
    """Initialize database with use_cases, sessions, and conversation_history tables"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Original use_cases table with session_id
    c.execute("""
        CREATE TABLE IF NOT EXISTS use_cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            title TEXT NOT NULL,
            preconditions TEXT,
            main_flow TEXT,
            sub_flows TEXT,
            alternate_flows TEXT,
            outcomes TEXT,
            stakeholders TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Sessions table - tracks each chat window/session
    c.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            project_context TEXT,
            domain TEXT,
            user_preferences TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Conversation history table - stores all interactions
    c.execute("""
        CREATE TABLE IF NOT EXISTS conversation_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            metadata TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions(session_id)
        )
    """)
    
    # Session summaries - periodic summaries of long conversations
    c.execute("""
        CREATE TABLE IF NOT EXISTS session_summaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            summary TEXT NOT NULL,
            key_concepts TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions(session_id)
        )
    """)
    
    conn.commit()
    conn.close()

def create_session(session_id: str, project_context: str = "", domain: str = ""):
    """Create a new session or update existing one"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    c.execute("""
        INSERT INTO sessions (session_id, project_context, domain, user_preferences)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(session_id) DO UPDATE SET
            last_active = CURRENT_TIMESTAMP
    """, (session_id, project_context, domain, json.dumps({})))
    
    conn.commit()
    conn.close()

def update_session_context(session_id: str, project_context: str = None, domain: str = None, preferences: dict = None):
    """Update session context as conversation progresses"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    updates = []
    params = []
    
    if project_context is not None:
        updates.append("project_context = ?")
        params.append(project_context)
    if domain is not None:
        updates.append("domain = ?")
        params.append(domain)
    if preferences is not None:
        updates.append("user_preferences = ?")
        params.append(json.dumps(preferences))
    
    if updates:
        updates.append("last_active = CURRENT_TIMESTAMP")
        params.append(session_id)
        
        query = f"UPDATE sessions SET {', '.join(updates)} WHERE session_id = ?"
        c.execute(query, params)
        conn.commit()
    
    conn.close()

def add_conversation_message(session_id: str, role: str, content: str, metadata: dict = None):
    """Add a message to conversation history"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    c.execute("""
        INSERT INTO conversation_history (session_id, role, content, metadata)
        VALUES (?, ?, ?, ?)
    """, (session_id, role, content, json.dumps(metadata or {})))
    
    # Update session last_active
    c.execute("""
        UPDATE sessions SET last_active = CURRENT_TIMESTAMP WHERE session_id = ?
    """, (session_id,))
    
    conn.commit()
    conn.close()

def get_conversation_history(session_id: str, limit: int = 10) -> List[Dict]:
    """Retrieve recent conversation history for a session"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    c.execute("""
        SELECT role, content, metadata, timestamp
        FROM conversation_history
        WHERE session_id = ?
        ORDER BY timestamp DESC
        LIMIT ?
    """, (session_id, limit))
    
    rows = c.fetchall()
    conn.close()
    
    # Return in chronological order (oldest first)
    return [{
        "role": row[0],
        "content": row[1],
        "metadata": json.loads(row[2]) if row[2] else {},
        "timestamp": row[3]
    } for row in reversed(rows)]

def get_session_context(session_id: str) -> Optional[Dict]:
    """Get accumulated context for a session"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    c.execute("""
        SELECT project_context, domain, user_preferences
        FROM sessions
        WHERE session_id = ?
    """, (session_id,))
    
    row = c.fetchone()
    conn.close()
    
    if row:
        return {
            "project_context": row[0] or "",
            "domain": row[1] or "",
            "user_preferences": json.loads(row[2]) if row[2] else {}
        }
    return None

def get_session_use_cases(session_id: str) -> List[Dict]:
    """Get all use cases generated in this session"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    c.execute("""
        SELECT id, title, preconditions, main_flow, sub_flows, 
               alternate_flows, outcomes, stakeholders
        FROM use_cases
        WHERE session_id = ?
        ORDER BY created_at DESC
    """, (session_id,))
    
    rows = c.fetchall()
    conn.close()
    
    return [{
        "id": row[0],
        "title": row[1],
        "preconditions": json.loads(row[2]) if row[2] else [],
        "main_flow": json.loads(row[3]) if row[3] else [],
        "sub_flows": json.loads(row[4]) if row[4] else [],
        "alternate_flows": json.loads(row[5]) if row[5] else [],
        "outcomes": json.loads(row[6]) if row[6] else [],
        "stakeholders": json.loads(row[7]) if row[7] else []
    } for row in rows]

def get_use_case_by_id(use_case_id: int) -> Optional[Dict]:
    """Get a specific use case by ID"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    c.execute("""
        SELECT id, session_id, title, preconditions, main_flow, sub_flows,
               alternate_flows, outcomes, stakeholders
        FROM use_cases
        WHERE id = ?
    """, (use_case_id,))
    
    row = c.fetchone()
    conn.close()
    
    if row:
        return {
            "id": row[0],
            "session_id": row[1],
            "title": row[2],
            "preconditions": json.loads(row[3]) if row[3] else [],
            "main_flow": json.loads(row[4]) if row[4] else [],
            "sub_flows": json.loads(row[5]) if row[5] else [],
            "alternate_flows": json.loads(row[6]) if row[6] else [],
            "outcomes": json.loads(row[7]) if row[7] else [],
            "stakeholders": json.loads(row[8]) if row[8] else []
        }
    return None


def update_use_case(use_case_id: int, updated_data: Dict) -> bool:
    """Update a use case with new data"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    try:
        c.execute("""
            UPDATE use_cases
            SET title = ?,
                preconditions = ?,
                main_flow = ?,
                sub_flows = ?,
                alternate_flows = ?,
                outcomes = ?,
                stakeholders = ?
            WHERE id = ?
        """, (
            updated_data.get('title', ''),
            json.dumps(updated_data.get('preconditions', [])),
            json.dumps(updated_data.get('main_flow', [])),
            json.dumps(updated_data.get('sub_flows', [])),
            json.dumps(updated_data.get('alternate_flows', [])),
            json.dumps(updated_data.get('outcomes', [])),
            json.dumps(updated_data.get('stakeholders', [])),
            use_case_id
        ))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        conn.close()
        print(f"Error updating use case: {e}")
        return False


def add_session_summary(session_id: str, summary: str, key_concepts: List[str]):
    """Add a summary of conversation progress"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    c.execute("""
        INSERT INTO session_summaries (session_id, summary, key_concepts)
        VALUES (?, ?, ?)
    """, (session_id, summary, json.dumps(key_concepts)))
    
    conn.commit()
    conn.close()

def get_latest_summary(session_id: str) -> Optional[Dict]:
    """Get the most recent summary for a session"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    c.execute("""
        SELECT summary, key_concepts, created_at
        FROM session_summaries
        WHERE session_id = ?
        ORDER BY created_at DESC
        LIMIT 1
    """, (session_id,))
    
    row = c.fetchone()
    conn.close()
    
    if row:
        return {
            "summary": row[0],
            "key_concepts": json.loads(row[1]) if row[1] else [],
            "created_at": row[2]
        }
    return None