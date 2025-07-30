# Bookstore Recommendations Demo Plan

## Overview
This document provides supplementary details and tips for running the bookstore recommendations demo. For the complete setup and main demo script, see `README.md`.

## Additional Demo Tips

### Pre-Demo Checklist
- [ ] Aiven PostgreSQL service is running with at least 2 vCPU
- [ ] Slow query logging is configured (`log_min_duration_statement = 10`)
- [ ] Sample data is loaded and vector index is created
- [ ] Streamlit app is tested and working
- [ ] AI Insights tab is accessible in Aiven Console

### Demo Timing Adjustments
- **Short Demo (5 min)**: Skip Steps 4-6, focus on AI Insights and pgvector
- **Full Demo (10 min)**: Include all steps as outlined in README.md
- **Extended Demo (15 min)**: Add troubleshooting scenarios and deep-dive explanations

### Alternative Demo Flows

#### Developer-Focused Demo
1. **Setup & Architecture** (2 min)
   - Show project structure and key files
   - Explain database schema and vector embeddings
   - Demonstrate Makefile automation

2. **AI Insights Deep Dive** (3 min)
   - Show multiple slow queries
   - Compare different optimization strategies
   - Explain the optimization process

3. **pgvector Implementation** (3 min)
   - Show vector similarity calculations
   - Demonstrate different similarity metrics
   - Explain embedding generation process

#### Executive-Focused Demo
1. **Business Value** (2 min)
   - ROI of AI-powered recommendations
   - Cost savings from automated optimization
   - Competitive advantages

2. **Technical Capabilities** (3 min)
   - Zero-downtime operations
   - Disaster recovery capabilities
   - Scalability features

3. **Real-world Applications** (2 min)
   - E-commerce recommendations
   - Content discovery systems
   - Similarity search use cases

### Troubleshooting Scenarios

#### Common Issues & Solutions

**Connection Problems:**
```bash
# Test connection
psql $DATABASE_URL -c "SELECT 1;"

# Check environment variables
echo $DATABASE_URL

# Verify network access
ping bookrec-db-artem-demo.i.aivencloud.com
```

**pgvector Extension Issues:**
```sql
-- Check if extension exists
SELECT * FROM pg_extension WHERE extname = 'vector';

-- Recreate extension if needed
DROP EXTENSION IF EXISTS vector CASCADE;
CREATE EXTENSION vector;
```

**Performance Issues:**
- Check AI Insights for optimization suggestions
- Monitor service metrics in Aiven Console
- Verify indexes are properly created

#### Demo Recovery Strategies

**If AI Insights doesn't show suggestions:**
1. Ensure slow query logging is enabled
2. Run more iterations: `make ai-workload`
3. Check query execution time in logs
4. Verify query complexity triggers optimization

**If vector search fails:**
1. Check pgvector extension status
2. Verify embeddings are properly stored
3. Test with simple vector query
4. Recreate vector index if needed

**If app doesn't start:**
1. Check Python dependencies: `pip install -r requirements.txt`
2. Verify DATABASE_URL environment variable
3. Test database connection separately
4. Check Streamlit installation: `streamlit --version`

### Advanced Demo Features

#### Custom Queries for AI Insights
```sql
-- Alternative slow query for testing
SELECT 
    b.title,
    COUNT(r.rating) as rating_count,
    AVG(r.rating) as avg_rating,
    (SELECT COUNT(*) FROM ratings r2 WHERE r2.book_id = b.id AND r2.rating >= 4) as high_ratings,
    (SELECT COUNT(*) FROM ratings r3 WHERE r3.book_id = b.id AND r3.rating <= 2) as low_ratings,
    (SELECT AVG(r4.rating) FROM ratings r4 WHERE r4.book_id = b.id) as book_avg,
    (SELECT COUNT(*) FROM ratings r5 WHERE r5.book_id = b.id) as total_ratings
FROM books b
LEFT JOIN ratings r ON b.id = r.book_id
WHERE r.rating > 2
AND EXISTS (SELECT 1 FROM ratings r6 WHERE r6.book_id = b.id AND r6.rating >= 4)
AND b.id IN (SELECT DISTINCT book_id FROM ratings WHERE rating > 3)
GROUP BY b.id, b.title
HAVING COUNT(r.rating) >= 1
ORDER BY avg_rating DESC, rating_count DESC
LIMIT 15;
```

#### Vector Similarity Experiments
```sql
-- Test different similarity metrics
SELECT title, 
       embedding <=> '[0.1,0.2,...]'::vector as cosine_distance,
       embedding <-> '[0.1,0.2,...]'::vector as euclidean_distance
FROM books 
ORDER BY embedding <=> '[0.1,0.2,...]'::vector 
LIMIT 5;
```

### Post-Demo Activities

#### Data Analysis
```sql
-- Analyze recommendation quality
SELECT 
    b.title,
    COUNT(r.rating) as num_ratings,
    AVG(r.rating) as avg_rating,
    STDDEV(r.rating) as rating_variance
FROM books b
LEFT JOIN ratings r ON b.id = r.book_id
GROUP BY b.id, b.title
HAVING COUNT(r.rating) >= 5
ORDER BY avg_rating DESC
LIMIT 10;
```

#### Performance Monitoring
- Monitor query execution times
- Track AI Insights optimization frequency
- Analyze vector search performance
- Review service metrics and scaling events

### Success Metrics & KPIs

#### Technical Metrics
- **Query Optimization**: >50% performance improvement
- **Vector Search**: <1 second response time
- **Zero Downtime**: 100% uptime during scaling
- **Recovery Time**: <2 minutes for PITR

#### Business Metrics
- **Developer Productivity**: Reduced DBA overhead
- **Cost Efficiency**: Automated optimization vs manual tuning
- **Reliability**: 99.9%+ uptime with managed service
- **Scalability**: Seamless resource scaling

### Additional Resources

#### Documentation Links
- [Aiven PostgreSQL Documentation](https://docs.aiven.io/docs/products/postgresql)
- [pgvector Documentation](https://github.com/pgvector/pgvector)
- [Streamlit Documentation](https://docs.streamlit.io)
- [AI Insights Guide](https://docs.aiven.io/docs/products/postgresql/concepts/ai-insights)

#### Related Demos
- **Multi-region Replication**: Show cross-region disaster recovery
- **Advanced Monitoring**: Grafana dashboards and alerting
- **Data Pipeline Integration**: Kafka + PostgreSQL streaming
- **Security Features**: Encryption, IAM, and compliance

---

**Note**: This document supplements the main `README.md`. For complete setup and demo instructions, refer to the main documentation. 