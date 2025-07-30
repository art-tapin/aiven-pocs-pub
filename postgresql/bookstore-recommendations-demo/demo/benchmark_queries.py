#!/usr/bin/env python3
"""
Query Benchmarking Tool for AI Insights Demo
Compares original slow query with AI Insights optimized version
"""

import os
import psycopg2
import time
import statistics
from dotenv import load_dotenv
import argparse

load_dotenv()

class QueryBenchmarker:
    def __init__(self, database_url=None):
        self.database_url = database_url or os.getenv('DATABASE_URL')
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable not set")
        
        self.conn = None
        self.cursor = None
        

        
        # Load queries from files
        self.optimized_query = self.load_optimized_query()
        self.original_query = self.load_slow_query()
    
    def load_optimized_query(self):
        """Load the optimized query from the SQL file"""
        try:
            with open('demo/optimized_query.sql', 'r') as f:
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
            print("❌ demo/optimized_query.sql not found!")
            print("💡 Please paste the AI Insights optimized query into that file first.")
            return None
        except Exception as e:
            print(f"❌ Error loading optimized query: {e}")
            return None
    
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
    
    def connect(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(self.database_url)
            self.cursor = self.conn.cursor()
            print("✅ Connected to PostgreSQL database")
            
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            raise
    
    def run_query_benchmark(self, query, query_name, num_runs=5):
        """Run a query multiple times and collect timing statistics"""
        print(f"\n🔄 Running {query_name} ({num_runs} iterations)...")
        
        execution_times = []
        row_counts = []
        
        for i in range(num_runs):
            try:
                start_time = time.time()
                self.cursor.execute(query)
                results = self.cursor.fetchall()
                execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds
                
                execution_times.append(execution_time)
                row_counts.append(len(results))
                
                print(f"  Run {i+1}: {execution_time:.2f}ms, {len(results)} rows")
                
            except Exception as e:
                print(f"❌ Query execution failed: {e}")
                return None
        
        # Calculate statistics
        stats = {
            'min_time': min(execution_times),
            'max_time': max(execution_times),
            'avg_time': statistics.mean(execution_times),
            'median_time': statistics.median(execution_times),
            'std_dev': statistics.stdev(execution_times) if len(execution_times) > 1 else 0,
            'total_rows': sum(row_counts),
            'avg_rows': statistics.mean(row_counts)
        }
        
        return stats
    
    def benchmark_queries(self, num_runs=5):
        """Benchmark both queries and compare results"""
        if not self.optimized_query:
            print("❌ Cannot run benchmark without optimized query!")
            return
        
        if not self.original_query:
            print("❌ Cannot run benchmark without slow query!")
            return
        
        print("=" * 60)
        print("🏁 QUERY BENCHMARKING")
        print("=" * 60)
        
        # Benchmark original query
        original_stats = self.run_query_benchmark(self.original_query, "Original Query", num_runs)
        
        # Benchmark optimized query
        optimized_stats = self.run_query_benchmark(self.optimized_query, "Optimized Query", num_runs)
        
        if not original_stats or not optimized_stats:
            print("❌ Benchmark failed!")
            return
        
        # Compare results
        print("\n" + "=" * 60)
        print("📊 BENCHMARK RESULTS")
        print("=" * 60)
        
        print(f"{'Metric':<20} {'Original':<15} {'Optimized':<15} {'Improvement':<15}")
        print("-" * 65)
        
        # Average execution time
        avg_improvement = ((original_stats['avg_time'] - optimized_stats['avg_time']) / original_stats['avg_time']) * 100
        print(f"{'Avg Time (ms)':<20} {original_stats['avg_time']:<15.2f} {optimized_stats['avg_time']:<15.2f} {avg_improvement:>+14.1f}%")
        
        # Median execution time
        median_improvement = ((original_stats['median_time'] - optimized_stats['median_time']) / original_stats['median_time']) * 100
        print(f"{'Median Time (ms)':<20} {original_stats['median_time']:<15.2f} {optimized_stats['median_time']:<15.2f} {median_improvement:>+14.1f}%")
        
        # Min execution time
        min_improvement = ((original_stats['min_time'] - optimized_stats['min_time']) / original_stats['min_time']) * 100
        print(f"{'Min Time (ms)':<20} {original_stats['min_time']:<15.2f} {optimized_stats['min_time']:<15.2f} {min_improvement:>+14.1f}%")
        
        # Max execution time
        max_improvement = ((original_stats['max_time'] - optimized_stats['max_time']) / original_stats['max_time']) * 100
        print(f"{'Max Time (ms)':<20} {original_stats['max_time']:<15.2f} {optimized_stats['max_time']:<15.2f} {max_improvement:>+14.1f}%")
        
        # Standard deviation
        print(f"{'Std Dev (ms)':<20} {original_stats['std_dev']:<15.2f} {optimized_stats['std_dev']:<15.2f} {'N/A':>15}")
        
        # Row count consistency
        print(f"{'Avg Rows':<20} {original_stats['avg_rows']:<15.1f} {optimized_stats['avg_rows']:<15.1f} {'N/A':>15}")
        
        print("\n" + "=" * 60)
        print("🎯 SUMMARY")
        print("=" * 60)
        
        if avg_improvement > 0:
            print(f"✅ AI Insights optimization improved performance by {avg_improvement:.1f}%")
            print(f"⏱️  Average time reduced from {original_stats['avg_time']:.2f}ms to {optimized_stats['avg_time']:.2f}ms")
        else:
            print(f"⚠️  AI Insights optimization did not improve performance")
            print(f"⏱️  Average time increased from {original_stats['avg_time']:.2f}ms to {optimized_stats['avg_time']:.2f}ms")
        
        print(f"📊 Results are based on {num_runs} runs each")
        print("=" * 60)
    
    def cleanup(self):
        """Clean up database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("🧹 Database connection closed")

def main():
    parser = argparse.ArgumentParser(description='Benchmark original vs optimized queries')
    parser.add_argument('--runs', type=int, default=5, help='Number of benchmark runs per query')
    
    args = parser.parse_args()
    
    benchmarker = QueryBenchmarker()
    
    try:
        benchmarker.connect()
        benchmarker.benchmark_queries(args.runs)
        
    except Exception as e:
        print(f"❌ Benchmark failed: {e}")
        return 1
    finally:
        benchmarker.cleanup()
    
    return 0

if __name__ == "__main__":
    exit(main()) 