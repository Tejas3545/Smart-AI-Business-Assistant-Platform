"""Generate a schema SQL file from SQLAlchemy models.

Run from the repo root (in a virtualenv with requirements installed):

    python backend/scripts/generate_schema_sql.py

This writes `backend/schema.sql` containing CREATE TABLE statements for all models.
"""
from sqlalchemy.schema import CreateTable
from sqlalchemy.dialects import postgresql

from app.db.base import Base
import app.models  # ensure models are imported and registered on Base.metadata


def main():
    out_path = "backend/schema.sql"
    with open(out_path, "w", encoding="utf-8") as f:
        for table in Base.metadata.sorted_tables:
            ddl = CreateTable(table).compile(dialect=postgresql.dialect())
            f.write(str(ddl).rstrip())
            f.write(";\n\n")

    print(f"Wrote SQL schema to {out_path}")


if __name__ == "__main__":
    main()
