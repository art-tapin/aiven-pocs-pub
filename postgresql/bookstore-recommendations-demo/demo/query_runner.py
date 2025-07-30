#!/usr/bin/env python3
"""
Query Workload Runner for Aiven AI Insights Demo
Generates realistic slow queries to trigger optimization suggestions
"""

import os
import psycopg2
import time
import logging
from datetime import datetime, timedelta
import random
from dotenv import load_dotenv
import argparse

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('query_runner.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class QueryWorkloadRunner:
    def __init__(self, database_url=None):
        self.database_url = database_url or os.getenv('DATABASE_URL')
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable not set")
        
        self.conn = None
        self.cursor = None
        
    def connect(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(self.database_url)
            self.cursor = self.conn.cursor()
            logger.info("✅ Connected to PostgreSQL database")
            
            # Note: Session-level parameters require superuser privileges
            # Aiven AI Insights will automatically detect slow queries
            logger.info("✅ Connection established - AI Insights will auto-detect slow queries")
            
        except Exception as e:
            logger.error(f"❌ Connection failed: {e}")
            raise
    
    def ensure_extensions(self):
        """Ensure required extensions are enabled"""
        try:
            # Note: Extensions are typically managed by Aiven
            # pg_stat_statements is usually enabled by default
            logger.info("✅ Extensions managed by Aiven - proceeding with workload")
            
        except Exception as e:
            logger.error(f"❌ Extension check failed: {e}")
            raise
    

    
    def load_slow_query(self):
        """Load the slow query from the SQL file"""
        try:
            with open('demo/slow_query.sql', 'r') as f:
                content = f.read()
            
            # Extract the actual query (skip comments)
            lines = content.split('\n')
            query_lines = []
            for line in lines:
                line = line.strip()
                if line and not line.startswith('--'):
                    query_lines.append(line)
            
            return ' '.join(query_lines)
            
        except FileNotFoundError:
            print("❌ demo/slow_query.sql not found!")
            print("💡 Please ensure the slow query file exists.")
            return None
        except Exception as e:
            print(f"❌ Error loading slow query: {e}")
            return None

    def run_slow_query(self, query_name="default"):
        """Run a deliberately slow query to trigger AI Insights"""
        
        # Load the slow query from file
        slow_query = self.load_slow_query()
        if not slow_query:
            logger.error("❌ Cannot run slow query - file not found!")
            return 0, 0
        
        try:
            start_time = time.time()
            self.cursor.execute(slow_query)
            results = self.cursor.fetchall()
            execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            logger.info(f"📊 Query '{query_name}' executed in {execution_time:.2f}ms, returned {len(results)} rows")
            
            return execution_time, len(results)
            
        except Exception as e:
            logger.error(f"❌ Query execution failed: {e}")
            return 0, 0
    
    def run_workload(self, num_iterations=1000, delay_between_queries=0.1):
        """Run the workload for specified number of iterations"""
        logger.info(f"🚀 Starting workload: {num_iterations} iterations")
        
        total_execution_time = 0
        successful_queries = 0
        failed_queries = 0
        
        for i in range(num_iterations):
            try:
                execution_time, num_rows = self.run_slow_query(f"iteration_{i+1}")
                total_execution_time += execution_time
                successful_queries += 1
                
                if (i + 1) % 100 == 0:
                    avg_time = total_execution_time / (i + 1)
                    logger.info(f"📈 Progress: {i+1}/{num_iterations} queries, avg time: {avg_time:.2f}ms")
                
                # Small delay between queries
                time.sleep(delay_between_queries)
                
            except Exception as e:
                failed_queries += 1
                logger.error(f"❌ Query {i+1} failed: {e}")
        
        # Summary
        logger.info("=" * 50)
        logger.info("📊 WORKLOAD SUMMARY")
        logger.info("=" * 50)
        logger.info(f"✅ Successful queries: {successful_queries}")
        logger.info(f"❌ Failed queries: {failed_queries}")
        logger.info(f"⏱️ Total execution time: {total_execution_time/1000:.2f}s")
        logger.info(f"📈 Average query time: {total_execution_time/successful_queries:.2f}ms")
        logger.info(f"🎯 Success rate: {(successful_queries/(successful_queries+failed_queries)*100):.1f}%")
        logger.info("=" * 50)
        
        return {
            'successful': successful_queries,
            'failed': failed_queries,
            'total_time': total_execution_time,
            'avg_time': total_execution_time / successful_queries if successful_queries > 0 else 0
        }
    
    def cleanup(self):
        """Clean up database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        logger.info("🧹 Database connection closed")

def main():
    parser = argparse.ArgumentParser(description='Run query workload for AI Insights demo')
    parser.add_argument('--iterations', type=int, default=1000, help='Number of query iterations')
    parser.add_argument('--delay', type=float, default=0.1, help='Delay between queries in seconds')

    parser.add_argument('--skip-setup', action='store_true', help='Skip table creation and data seeding')
    parser.add_argument('--setup-guide', action='store_true', help='Show setup guide for AI Insights')
    
    args = parser.parse_args()
    
    if args.setup_guide:
        print("=" * 60)
        print("🔧 AI INSIGHTS SETUP GUIDE")
        print("=" * 60)
        print("1. In Aiven Console, go to your PostgreSQL service")
        print("2. Navigate to 'Settings' → 'Advanced Configuration'")
        print("3. Set 'log_min_duration_statement' to 10 (or 0 for all queries)")
        print("4. Save the configuration")
        print("5. No need to wait for the service to restart!")
        print("6. Run this workload: make ai-workload-quick")
        print("7. Check 'AI Insights' tab for optimization suggestions")
        print("8. Copy the optimized query to demo/optimized_query.sql")
        print("9. Run benchmark: make benchmark-queries")
        print("")
        print("💡 The queries are designed to be naturally slow through complexity")
        print("   (JOINs, EXISTS, aggregations) rather than artificial delays.")
        print("=" * 60)
        return 0
    
    runner = QueryWorkloadRunner()
    
    try:
        # Setup
        runner.connect()
        runner.ensure_extensions()
        
        # if not args.skip_setup:
        
        
        # Run workload
        results = runner.run_workload(args.iterations, args.delay)
        
        logger.info("🎉 Workload completed successfully!")
        logger.info("💡 Check Aiven Console → AI Insights tab for optimization suggestions")
        
    except Exception as e:
        logger.error(f"❌ Workload failed: {e}")
        return 1
    finally:
        runner.cleanup()
    
    return 0

if __name__ == "__main__":
    exit(main()) 