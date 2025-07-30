# 📚 Bookstore Recommendations Demo

A comprehensive demonstration of PostgreSQL-powered recommendation systems using **Aiven PostgreSQL** with **pgvector** for vector similarity search and **AI Insights** for automated query optimization.

## 🎯 Project Overview

This demo showcases a modern bookstore recommendation system that combines:
- **Vector similarity search** using pgvector for content-based recommendations
- **AI-powered query optimization** with Aiven's AI Insights
- **Real-time analytics** with Streamlit web interface
- **Automated performance monitoring** and optimization

## ✨ Key Features

### 🔍 Vector Similarity Search
- Content-based book recommendations using pgvector
- Cosine similarity calculations for finding similar books
- Real-time recommendation engine

### 🤖 AI Insights Integration
- Automated query performance analysis
- Intelligent optimization suggestions
- Performance monitoring and alerting

### 📊 Interactive Analytics Dashboard
- Book rating analytics and visualizations
- Recommendation quality metrics
- Real-time performance monitoring

### 🚀 Automated Operations
- One-command setup and teardown
- Automated data seeding with vector embeddings
- Performance benchmarking tools

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Streamlit     │    │   Aiven          │    │   pgvector      │
│   Web App       │◄──►│   PostgreSQL     │◄──►│   Extensions    │
│                 │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │   AI Insights    │
                       │   (Automated     │
                       │   Optimization)  │
                       └──────────────────┘
```

## 🛠️ Prerequisites

- **Aiven PostgreSQL** service (2+ vCPU recommended)
- **Python 3.8+** with pip
- **Git** for cloning the repository
- **Environment variables** configured

## 🚀 Quick Start

### 1. Environment Setup

```bash
# Clone the repository
git clone <repository-url>
cd postgresql/bookstore-recommendations-demo

# Install dependencies
make install-deps

# Set your database URL
export DATABASE_URL="postgresql://username:password@host:port/database"
```

### 2. Database Setup

```bash
# Create schema and extensions
make create-schema

# Seed with sample data and vector embeddings
make seed-data
```

### 3. Run the Application

```bash
# Start the Streamlit web app
make run-app
```

The application will be available at `http://localhost:8501`

## 📋 Available Commands

### Setup & Data Management
```bash
make install-deps          # Install Python dependencies
make create-schema         # Create database schema
make seed-data            # Populate with sample data
make reset-data           # Reset and reseed database
make teardown             # Remove all demo data
```

### Application
```bash
make run-app              # Start Streamlit application
```

### AI Insights Demo
```bash
make ai-workload          # Run AI Insights workload (1000 queries)
make ai-workload-quick    # Quick workload (100 queries)
make ai-setup-guide       # Show AI Insights configuration
```

### Performance Testing
```bash
make benchmark-queries           # Compare original vs optimized queries
make benchmark-queries-quick     # Quick benchmark (3 runs each)
```

### pgvector Demo
```bash
make pgvector-demo        # Show pgvector demo commands
```

## 🎮 Demo Scenarios

### 1. Vector Similarity Search
- Select a book from the dropdown
- View similar book recommendations
- Explore recommendation quality metrics

### 2. AI Insights Optimization
- Run performance workload: `make ai-workload`
- Check Aiven Console for optimization suggestions
- Compare before/after performance

### 3. Real-time Analytics
- View book rating distributions
- Analyze recommendation patterns
- Monitor system performance

## 📊 Database Schema

### Books Table
```sql
CREATE TABLE books (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(255),
    genre VARCHAR(100),
    embedding vector(384)  -- pgvector embedding
);
```

### Ratings Table
```sql
CREATE TABLE ratings (
    id SERIAL PRIMARY KEY,
    book_id INTEGER REFERENCES books(id),
    user_id INTEGER,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🔧 Configuration

### AI Insights Setup
1. Enable slow query logging in Aiven Console
2. Set `log_min_duration_statement = 10`
3. Run workload to generate optimization suggestions

### pgvector Configuration
- Vector dimension: 384
- Index type: IVFFlat with cosine similarity
- Embedding generation: Simulated for demo purposes

## 📈 Performance Features

### Automated Optimization
- AI Insights analyzes slow queries
- Provides optimization recommendations
- Monitors performance improvements

### Vector Search Performance
- Optimized IVFFlat indexes
- Cosine similarity calculations
- Real-time recommendation generation

### Scalability
- Horizontal scaling with Aiven
- Zero-downtime operations
- Automated backup and recovery

## 🛡️ Security & Best Practices

- Environment variable configuration
- Connection pooling
- Input validation and sanitization
- Error handling and logging

## 📚 Additional Resources

- [Aiven PostgreSQL Documentation](https://docs.aiven.io/docs/products/postgresql)
- [pgvector Documentation](https://github.com/pgvector/pgvector)
- [Streamlit Documentation](https://docs.streamlit.io)
- [AI Insights Guide](https://docs.aiven.io/docs/products/postgresql/concepts/ai-insights)

## 🤝 Contributing

This is a demonstration project. For production use, consider:
- Implementing proper authentication
- Adding comprehensive error handling
- Setting up monitoring and alerting
- Implementing proper security measures

## 📄 License

This project is for demonstration purposes. Please refer to individual component licenses for production use.

---

**Note**: This demo requires an active Aiven PostgreSQL service. For detailed demo instructions and troubleshooting, see `docs/DEMO_PLAN.md`. 