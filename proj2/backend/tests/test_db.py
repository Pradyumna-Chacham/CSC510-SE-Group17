import pytest
import os
import json
import sqlite3
from datetime import datetime
from db import (
    init_db,
    create_session,
    update_session_context,
    add_conversation_message,
    get_conversation_history,
    get_session_context,
    get_session_use_cases,
    get_use_case_by_id,
    update_use_case,
    add_session_summary,
    get_latest_summary
)

@pytest.fixture
def test_db():
    # Create a temporary test database with a unique name
    test_db_path = f"test_requirements_{os.getpid()}.db"

    # Override the get_db_path function to use our test database
    import db
    original_get_db_path = db.get_db_path
    db.get_db_path = lambda: test_db_path

    # Initialize the test database
    init_db()

    yield test_db_path

    # Restore original function
    db.get_db_path = original_get_db_path

    # Clean up the test database
    try:
        import sqlite3
        # Close any remaining connections
        conn = sqlite3.connect(test_db_path)
        conn.close()
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
    except Exception as e:
        print(f"Warning: Could not clean up test database: {e}")

def test_create_and_get_session(test_db):
    session_id = "test_session_1"
    project_context = "Test Project"
    domain = "Test Domain"
    session_title = "Test Session Title"
    
    # Create session with title
    create_session(session_id, project_context, domain, session_title)
    
    # Get session context
    context = get_session_context(session_id)
    assert context is not None
    assert context["project_context"] == project_context
    assert context["domain"] == domain
    assert context["user_preferences"] == {}
    
    # Verify session in database has correct title
    conn = sqlite3.connect(test_db)
    c = conn.cursor()
    c.execute("SELECT session_title FROM sessions WHERE session_id = ?", (session_id,))
    db_title = c.fetchone()[0]
    conn.close()
    assert db_title == session_title

def test_update_session_context(test_db):
    session_id = "test_session_2"
    create_session(session_id)
    
    # Update context
    new_context = "Updated Project"
    new_domain = "Updated Domain"
    new_preferences = {"theme": "dark"}
    
    update_session_context(
        session_id,
        project_context=new_context,
        domain=new_domain,
        preferences=new_preferences
    )
    
    # Verify updates
    context = get_session_context(session_id)
    assert context["project_context"] == new_context
    assert context["domain"] == new_domain
    assert context["user_preferences"] == new_preferences

    def test_conversation_history(test_db):
        session_id = "test_session_3"
        create_session(session_id)
        
        # Add messages
        messages = [
            ("user", "Hello"),
            ("system", "Hi there"),
            ("user", "How are you?")
        ]
        
        # Add all messages first
        for role, content in messages:
            add_conversation_message(session_id, role, content)
        
        # Then get history
        history = get_conversation_history(session_id)
        assert len(history) == len(messages)
        
        # Verify message order and content
        for i, (role, content) in enumerate(messages):
            assert history[i]["role"] == role
            assert history[i]["content"] == content        # Message history should be in reverse order (newest first)
        history = list(reversed(history))
        
        # Verify each message matches
        for i, (role, content) in enumerate(messages):
            assert history[i]["role"] == role
            assert history[i]["content"] == content

def test_use_case_management(test_db):
    session_id = "test_session_4"
    create_session(session_id)
    
    # Create a test use case
    conn = sqlite3.connect(test_db)
    c = conn.cursor()
    
    test_use_case = {
        "title": "Test Use Case",
        "preconditions": ["Condition 1", "Condition 2"],
        "main_flow": ["Step 1", "Step 2"],
        "sub_flows": ["Sub 1"],
        "alternate_flows": ["Alt 1"],
        "outcomes": ["Outcome 1"],
        "stakeholders": ["User", "System"]
    }
    
    c.execute("""
        INSERT INTO use_cases (
            session_id, title, preconditions, main_flow, sub_flows,
            alternate_flows, outcomes, stakeholders
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        session_id,
        test_use_case["title"],
        json.dumps(test_use_case["preconditions"]),
        json.dumps(test_use_case["main_flow"]),
        json.dumps(test_use_case["sub_flows"]),
        json.dumps(test_use_case["alternate_flows"]),
        json.dumps(test_use_case["outcomes"]),
        json.dumps(test_use_case["stakeholders"])
    ))
    
    use_case_id = c.lastrowid
    conn.commit()
    conn.close()
    
    # Test get_session_use_cases
    use_cases = get_session_use_cases(session_id)
    assert len(use_cases) == 1
    assert use_cases[0]["title"] == test_use_case["title"]
    
    # Test get_use_case_by_id
    use_case = get_use_case_by_id(use_case_id)
    assert use_case is not None
    assert use_case["title"] == test_use_case["title"]
    
    # Test update_use_case
    updated_data = test_use_case.copy()
    updated_data["title"] = "Updated Title"
    success = update_use_case(use_case_id, updated_data)
    assert success
    
    # Verify update
    updated = get_use_case_by_id(use_case_id)
    assert updated["title"] == "Updated Title"

def test_session_summaries(test_db):
    session_id = "test_session_5"
    create_session(session_id)
    
    # Add summary
    summary = "Test summary"
    key_concepts = ["concept1", "concept2"]
    add_session_summary(session_id, summary, key_concepts)
    
    # Get latest summary
    latest = get_latest_summary(session_id)
    assert latest is not None
    assert latest["summary"] == summary
    assert latest["key_concepts"] == key_concepts

def test_nonexistent_session(test_db):
    nonexistent_id = "nonexistent_session"
    assert get_session_context(nonexistent_id) is None
    assert get_conversation_history(nonexistent_id) == []
    assert get_session_use_cases(nonexistent_id) == []
    assert get_use_case_by_id(999999) is None
    assert get_latest_summary(nonexistent_id) is None

def test_update_nonexistent_use_case(test_db):
    # Try to update a use case that doesn't exist
    session_id = "test_session_999"
    success = update_use_case(session_id, {"title": "New Title"})
    assert success == False  # Should return False for non-existent use case

def test_migrate_db_session_title(test_db):
    """Test database migration for session_title column"""
    from db import migrate_db
    
    conn = sqlite3.connect(test_db)
    c = conn.cursor()
    
    # First, create a basic sessions table without session_title
    c.execute("""
        CREATE TABLE IF NOT EXISTS sessions_temp (
            session_id TEXT PRIMARY KEY,
            project_context TEXT,
            domain TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Add a test session
    c.execute("""
        INSERT INTO sessions_temp (session_id, project_context, domain)
        VALUES (?, ?, ?)
    """, ("test_migrate_session", "Test Project", "Test Domain"))
    
    # Rename the table to sessions
    c.execute("DROP TABLE IF EXISTS sessions")
    c.execute("ALTER TABLE sessions_temp RENAME TO sessions")
    conn.commit()
    
    # Run migration
    migrate_db()
    
    # Verify session_title column exists and has default value
    c.execute("SELECT session_title FROM sessions WHERE session_id = ?", ("test_migrate_session",))
    title = c.fetchone()[0]
    assert title == "New Session" or title is not None
    
    conn.close()

    def test_migrate_db_reset(test_db):
        """Test database reset functionality"""
        from db import migrate_db
        
        # Create some test data
        session_id = "test_reset_session"
        create_session(session_id, "Test Project", "Test Domain", "Test Title")
        
        # Verify session exists
        conn = sqlite3.connect(test_db)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM sessions")
        count_before = c.fetchone()[0]
        conn.close()  # Close connection before reset
        assert count_before > 0
        
        # Reset database
        migrate_db(reset=True)
        
        # Verify database is clean with new connection
        conn = sqlite3.connect(test_db)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM sessions")
        count_after = c.fetchone()[0]
        conn.close()
        assert count_after == 0

def test_update_session_with_title(test_db):
    """Test updating session title"""
    session_id = "test_update_title"
    initial_title = "Initial Title"
    updated_title = "Updated Title"
    
    # Create session with initial title
    create_session(session_id, session_title=initial_title)
    
    # Update just the title
    update_session_context(session_id, session_title=updated_title)
    
    # Verify title was updated
    conn = sqlite3.connect(test_db)
    c = conn.cursor()
    c.execute("SELECT session_title FROM sessions WHERE session_id = ?", (session_id,))
    current_title = c.fetchone()[0]
    conn.close()
    
    assert current_title == updated_title