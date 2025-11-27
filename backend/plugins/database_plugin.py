"""
Database Plugin for ArbiterAI
Executes SQL queries on SQLite databases.
"""

import sqlite3
from pathlib import Path
from typing import Any, Dict
import sys
sys.path.append(str(Path(__file__).parent.parent))

from plugin_interface import (
    ArbiterPlugin,
    PluginMetadata,
    PluginResult,
    PluginPermission
)


class DatabasePlugin(ArbiterPlugin):
    """
    Execute SQL queries on SQLite databases.
    
    Features:
    - Execute SELECT queries
    - Execute INSERT/UPDATE/DELETE
    - Create tables
    - List tables
    - Describe table schema
    """
    
    def __init__(self):
        self.workspace_path = None
        self.db_path = None
    
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="database",
            version="1.0.0",
            author="ArbiterAI",
            description="Execute SQL queries on SQLite databases",
            dependencies=["sqlite3"],
            permissions=[PluginPermission.FILESYSTEM, PluginPermission.DATABASE]
        )
    
    def initialize(self, workspace: str) -> bool:
        """Initialize with workspace."""
        self.workspace_path = Path(workspace)
        self.db_path = self.workspace_path / "database.db"
        return True
    
    def execute(self, 
                query: str,
                database: str = "database.db",
                **kwargs) -> PluginResult:
        """
        Execute SQL query.
        
        Args:
            query: SQL query to execute
            database: Database filename (default: database.db)
            
        Returns:
            PluginResult with query results
        """
        try:
            # Resolve database path
            db_path = self.workspace_path / database
            
            # Connect to database
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Execute query
            cursor.execute(query)
            
            # Get results
            if query.strip().upper().startswith("SELECT"):
                results = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                
                # Format results
                output = self._format_results(columns, results)
                data = {
                    "columns": columns,
                    "rows": results,
                    "row_count": len(results)
                }
            else:
                # INSERT/UPDATE/DELETE
                conn.commit()
                output = f"Query executed successfully. Rows affected: {cursor.rowcount}"
                data = {
                    "rows_affected": cursor.rowcount
                }
            
            conn.close()
            
            return PluginResult(
                success=True,
                output=output,
                data=data
            )
            
        except sqlite3.Error as e:
            return PluginResult(
                success=False,
                error=f"Database error: {str(e)}"
            )
        except Exception as e:
            return PluginResult(
                success=False,
                error=f"Execution error: {str(e)}"
            )
    
    def _format_results(self, columns, rows) -> str:
        """Format query results as table."""
        if not rows:
            return "No results found."
        
        # Calculate column widths
        widths = [len(col) for col in columns]
        for row in rows:
            for i, val in enumerate(row):
                widths[i] = max(widths[i], len(str(val)))
        
        # Build table
        lines = []
        
        # Header
        header = " | ".join(col.ljust(widths[i]) for i, col in enumerate(columns))
        lines.append(header)
        lines.append("-" * len(header))
        
        # Rows (limit to 10 for display)
        for row in rows[:10]:
            line = " | ".join(str(val).ljust(widths[i]) for i, val in enumerate(row))
            lines.append(line)
        
        if len(rows) > 10:
            lines.append(f"... ({len(rows) - 10} more rows)")
        
        return "\n".join(lines)
    
    def validate_input(self, **kwargs) -> tuple[bool, str]:
        """Validate SQL query input."""
        if "query" not in kwargs:
            return False, "Parameter 'query' is required"
        
        query = kwargs["query"].strip()
        if not query:
            return False, "Query cannot be empty"
        
        # Basic SQL injection prevention
        dangerous_keywords = ["DROP DATABASE", "DROP SCHEMA", "--", ";--"]
        query_upper = query.upper()
        for keyword in dangerous_keywords:
            if keyword in query_upper:
                return False, f"Potentially dangerous query: contains '{keyword}'"
        
        return True, ""
    
    def describe(self) -> Dict[str, Any]:
        return {
            "name": "database",
            "description": "Execute SQL queries on SQLite databases in the workspace",
            "parameters": {
                "query": "SQL query to execute (string)",
                "database": "Database filename (optional, default: database.db)"
            },
            "examples": [
                "Create a users table with id, name, and email columns",
                "Insert a user with name 'John' and email 'john@example.com'",
                "Select all users from the users table",
                "Update user email where name is 'John'",
                "Count the number of users in the database"
            ]
        }


# Test the plugin
if __name__ == "__main__":
    import tempfile
    import shutil
    
    # Create temp workspace
    workspace = tempfile.mkdtemp()
    
    try:
        plugin = DatabasePlugin()
        plugin.initialize(workspace)
        
        print("=== Database Plugin Test ===\n")
        
        # Test 1: Create table
        print("Test 1: Create table")
        result = plugin.execute(query="CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT)")
        print(f"Success: {result.success}")
        print(f"Output: {result.output}\n")
        
        # Test 2: Insert data
        print("Test 2: Insert data")
        result = plugin.execute(query="INSERT INTO users (name, email) VALUES ('Alice', 'alice@example.com')")
        print(f"Success: {result.success}")
        print(f"Output: {result.output}\n")
        
        result = plugin.execute(query="INSERT INTO users (name, email) VALUES ('Bob', 'bob@example.com')")
        print(f"Success: {result.success}")
        print(f"Output: {result.output}\n")
        
        # Test 3: Select data
        print("Test 3: Select data")
        result = plugin.execute(query="SELECT * FROM users")
        print(f"Success: {result.success}")
        print(f"Output:\n{result.output}\n")
        print(f"Data: {result.data}\n")
        
        # Test 4: Validation error
        print("Test 4: Validation (should fail)")
        result = plugin.execute(query="DROP DATABASE; --")
        print(f"Success: {result.success}")
        print(f"Error: {result.error}\n")
        
    finally:
        # Cleanup
        shutil.rmtree(workspace)
        print("Workspace cleaned up")
