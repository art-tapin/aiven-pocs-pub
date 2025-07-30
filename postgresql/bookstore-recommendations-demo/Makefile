.PHONY: help create-schema seed-data run-app teardown install-deps

help:
	@echo "Available targets:"
	@echo "  install-deps  - Install Python dependencies"
	@echo "  create-schema - Create database schema"
	@echo "  drop-schema   - Drop all tables and extensions (WARNING: Destructive!)"
	@echo "  seed-data     - Populate database with sample data"
	@echo "  reset-data    - Reset and reseed database with proper vector embeddings"
	@echo "  run-app       - Start the Streamlit application"
	@echo "  ai-workload   - Run AI Insights workload (1000 queries)"
	@echo "  ai-workload-quick - Run quick AI Insights workload (100 queries)"
	@echo "  ai-setup-guide - Show AI Insights configuration guide"
	@echo "  benchmark-queries - Compare original vs optimized queries"
	@echo "  benchmark-queries-quick - Quick benchmark (3 runs each)"
	@echo "  pgvector-demo - Show pgvector demo commands"
	@echo "  teardown      - Remove all demo data"
	@echo "  help          - Show this help message"

install-deps:
	pip install -r requirements.txt

create-schema:
	@echo "Creating database schema..."
	psql $(DATABASE_URL) -f sql/schema.sql

drop-schema:
	@echo "WARNING: This will drop ALL tables and extensions!"
	@echo "This action is destructive and cannot be undone."
	@read -p "Are you sure you want to continue? (y/N): " confirm && [ "$$confirm" = "y" ] || exit 1
	@echo "Dropping all tables and extensions..."
	psql $(DATABASE_URL) -c "DROP TABLE IF EXISTS ratings CASCADE;"
	psql $(DATABASE_URL) -c "DROP TABLE IF EXISTS books CASCADE;"
	psql $(DATABASE_URL) -c "DROP EXTENSION IF EXISTS vector CASCADE;"
	@echo "Schema dropped successfully!"

seed-data:
	@echo "Seeding database with sample data..."
	python sql/seed.py
	@echo "Recreating vector index for optimal performance..."
	psql $(DATABASE_URL) -c "DROP INDEX IF EXISTS idx_books_embedding;"
	psql $(DATABASE_URL) -c "CREATE INDEX idx_books_embedding ON books USING ivfflat (embedding vector_cosine_ops);"

reset-data:
	@echo "Resetting and reseeding database with proper vector embeddings..."
	psql $(DATABASE_URL) -f sql/teardown.sql
	python sql/seed.py
	@echo "Recreating vector index for optimal performance..."
	psql $(DATABASE_URL) -c "DROP INDEX IF EXISTS idx_books_embedding;"
	psql $(DATABASE_URL) -c "CREATE INDEX idx_books_embedding ON books USING ivfflat (embedding vector_cosine_ops);"

run-app:
	@echo "Starting Streamlit application..."
	streamlit run app/app.py

teardown:
	@echo "Removing demo data..."
	psql $(DATABASE_URL) -f sql/teardown.sql

ai-workload:
	@echo "Running AI Insights workload..."
	python demo/query_runner.py --iterations 1000 --delay 0.1

ai-workload-quick:
	@echo "Running quick AI Insights workload..."
	python demo/query_runner.py --iterations 100 --delay 0.05

ai-setup-guide:
	@echo "Showing AI Insights setup guide..."
	python demo/query_runner.py --setup-guide

benchmark-queries:
	@echo "Benchmarking original vs optimized queries..."
	python demo/benchmark_queries.py

benchmark-queries-quick:
	@echo "Quick benchmarking (3 runs each)..."
	python demo/benchmark_queries.py --runs 3

pgvector-demo:
	@echo "pgvector Demo Commands:"
	@echo "1. Check if pgvector is enabled (should show it's active):"
	@echo "   psql \$$DATABASE_URL -c \"SELECT * FROM pg_extension WHERE extname = 'vector';\""
	@echo ""
	@echo "2. Show working app:"
	@echo "   make run-app"
	@echo ""
	@echo "3. WARNING: Disabling pgvector would remove all vector data!"
	@echo "   Demonstration command (DO NOT RUN):"
	@echo "   psql \$$DATABASE_URL -c \"DROP EXTENSION vector CASCADE;\""
	@echo ""
	@echo "4. Explain what would happen if extension was disabled:"
	@echo "   - App would show error: 'operator does not exist: vector <-> numeric[]'"
	@echo "   - Vector similarity search would fail"
	@echo ""
	@echo "5. Re-enable pgvector (if we had disabled it):"
	@echo "   psql \$$DATABASE_URL -c \"CREATE EXTENSION IF NOT EXISTS vector;\""
	@echo ""
	@echo "6. Show app working again:"
	@echo "   make run-app" 