"""
Database indexes to optimize frequently queried columns.
Run these migrations to improve query performance.
"""

# Indexes for users table
INDEXES = {
    "users": [
        "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);",
        "CREATE INDEX IF NOT EXISTS idx_users_workspace_id ON users(workspace_id);",
        "CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);",
    ],
    "audit_logs": [
        "CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);",
        "CREATE INDEX IF NOT EXISTS idx_audit_logs_event_type ON audit_logs(event_type);",
        "CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at DESC);",
    ],
    "conversations": [
        "CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);",
        "CREATE INDEX IF NOT EXISTS idx_conversations_created_at ON conversations(created_at DESC);",
    ],
    "documents": [
        "CREATE INDEX IF NOT EXISTS idx_documents_user_id ON documents(user_id);",
        "CREATE INDEX IF NOT EXISTS idx_documents_source ON documents(source);",
    ],
    "leads": [
        "CREATE INDEX IF NOT EXISTS idx_leads_user_id ON leads(user_id);",
        "CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);",
        "CREATE INDEX IF NOT EXISTS idx_leads_email ON leads(email);",
    ],
    "messages": [
        "CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);",
        "CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at DESC);",
    ],
    "workflows": [
        "CREATE INDEX IF NOT EXISTS idx_workflows_workspace_id ON workflows(workspace_id);",
        "CREATE INDEX IF NOT EXISTS idx_workflows_is_active ON workflows(is_active);",
    ],
    "automation_tasks": [
        "CREATE INDEX IF NOT EXISTS idx_automation_tasks_workspace_id ON automation_tasks(workspace_id);",
        "CREATE INDEX IF NOT EXISTS idx_automation_tasks_workflow_id ON automation_tasks(workflow_id);",
        "CREATE INDEX IF NOT EXISTS idx_automation_tasks_status ON automation_tasks(status);",
        "CREATE INDEX IF NOT EXISTS idx_automation_tasks_next_run_at ON automation_tasks(next_run_at);",
    ],
    "workspaces": [
        "CREATE INDEX IF NOT EXISTS idx_workspaces_owner_id ON workspaces(owner_id);",
        "CREATE INDEX IF NOT EXISTS idx_workspaces_is_active ON workspaces(is_active);",
    ],
}

async def run_index_migrations(db_connection):
    """
    Run all index migrations.
    
    Usage in main.py:
    ```
    from app.db.indexes import run_index_migrations
    
    @app.on_event("startup")
    async def startup():
        async with engine.begin() as conn:
            await run_index_migrations(conn)
    ```
    """
    for table_name, index_statements in INDEXES.items():
        for statement in index_statements:
            try:
                await db_connection.execute(statement)
                print(f"✓ Created index: {statement.split('ON')[1].split('(')[0].strip()}")
            except Exception as e:
                print(f"⚠ Index creation skipped: {e}")
