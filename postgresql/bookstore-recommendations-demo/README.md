## Bookstore Recommendations Demo

A demo of a PostgreSQL-based recommendation system using Aiven PostgreSQL, pgvector for vector similarity search, and AI Insights for query optimization.

---

### Overview

* Content-based book recommendations via pgvector
* Automated query optimization with AI Insights
* Streamlit web interface for real‑time analytics
* Automated setup, data seeding, benchmarking, and teardown

---

### Architecture

```
Streamlit Web App ↔ Aiven PostgreSQL ↔ pgvector Extension
                                  ↓
                           AI Insights
```

---

### Prerequisites

* Aiven PostgreSQL
* Python 3.8+ and pip
* Git
* Environment variable `DATABASE_URL` set or located in .env file

---

### Quick Start

1. **Clone and install**

   ```bash
   git clone <repo-url>
   cd bookstore-recommendations-demo
   make install-deps
   export DATABASE_URL="postgresql://user:pass@host:port/db"
   ```

2. **Database setup**

   ```bash
   make create-schema   # creates tables and extensions
   make seed-data       # loads sample data and embeddings
   ```

3. **Run app**

   ```bash
   make run-app         # starts Streamlit at http://localhost:8501
   ```

---

### Commands

* **Dependencies & schema**

  ```bash
  make install-deps      # install Python packages
  make create-schema     # create tables and pgvector
  make seed-data         # seed sample data
  make reset-data        # drop and reseed data
  make teardown          # remove demo data
  ```

* **Application**

  ```bash
  make run-app           # launch Streamlit dashboard
  ```

* **AI Insights**

  ```bash
  make ai-setup-guide    # show configuration steps
  make ai-workload       # run 1000-query workload
  make ai-workload-quick # run 100-query workload
  ```

* **Benchmarking**

  ```bash
  make benchmark-queries       # full benchmark
  make benchmark-queries-quick # 3 runs per query
  ```

* **pgvector**

  ```bash
  make pgvector-demo      # demo pgvector commands
  ```

---

### Demo Scenarios

1. **Vector Similarity**

   * Select a book
   * Retrieve similar titles via cosine similarity

2. **AI Insights**

   * Run `make ai-workload`
   * Review optimization suggestions in Aiven Console

3. **Analytics**

   * View rating distributions and recommendation metrics
   * Monitor query performance in real time

---

### Database Schema

**books**

```sql
CREATE TABLE books (
  id SERIAL PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  author VARCHAR(255),
  genre VARCHAR(100),
  embedding vector(384)
);
```

**ratings**

```sql
CREATE TABLE ratings (
  id SERIAL PRIMARY KEY,
  book_id INTEGER REFERENCES books(id),
  user_id INTEGER,
  rating INTEGER CHECK (rating BETWEEN 1 AND 5),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

### Configuration

* **AI Insights**

  1. Enable slow query logging
  2. Set `log_min_duration_statement = 10` ms
  3. Execute workload to collect data

* **pgvector**

  * Vector dimension: 384
  * Index: IVFFlat with cosine similarity
  * Embeddings: generated in seed script

---

### Performance & Operations

* Automatic setup and teardown
* Data seeding with embeddings
* Real‑time recommendation and analytics
* AI-driven query optimization and alerts
* Benchmarking tools for performance comparison

---

### Security & Best Practices

* Use environment variables for credentials
* Enable connection pooling
* Validate inputs and handle errors
* Configure backups and monitoring

---

### Resources

* Aiven PostgreSQL: [https://docs.aiven.io/docs/products/postgresql](https://docs.aiven.io/docs/products/postgresql)
* pgvector: [https://github.com/pgvector/pgvector](https://github.com/pgvector/pgvector)
* Streamlit: [https://docs.streamlit.io](https://docs.streamlit.io)
* AI Insights: [https://docs.aiven.io/docs/products/postgresql/concepts/ai-insights](https://docs.aiven.io/docs/products/postgresql/concepts/ai-insights)

---

### License

Demo code only. Refer to component-specific licenses for production use.
