#!/usr/bin/env python3
"""
Bookstore Recommendations Demo - Streamlit Application
Demonstrates pgvector similarity search and rating analytics
"""

import streamlit as st
import psycopg2
import pandas as pd
import numpy as np
import os
from dotenv import load_dotenv
import plotly.express as px
import plotly.graph_objects as go

load_dotenv()

# Page configuration
st.set_page_config(
    page_title="📚 Bookstore Recommendations",
    page_icon="📚",
    layout="wide"
)

def get_database_connection():
    """Create database connection"""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        st.error("❌ DATABASE_URL environment variable not set")
        st.stop()
    
    try:
        conn = psycopg2.connect(database_url)
        return conn
    except Exception as e:
        st.error(f"❌ Database connection failed: {e}")
        st.stop()

def get_all_books(conn):
    """Get all books for the dropdown selection"""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, title
            FROM books
            ORDER BY title
        """)
        
        results = cursor.fetchall()
        cursor.close()
        
        return [{'id': row[0], 'title': row[1]} for row in results]
    except Exception as e:
        st.error(f"❌ Error getting books: {e}")
        return []

def get_book_rating(conn, book_id):
    """Get the average rating for a specific book"""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT AVG(rating), COUNT(rating)
            FROM ratings
            WHERE book_id = %s
        """, (book_id,))
        
        result = cursor.fetchone()
        cursor.close()
        
        if result and result[0]:
            avg_rating = float(result[0])
            num_ratings = result[1]
            return avg_rating, num_ratings
        return None, 0
    except Exception as e:
        return None, 0

def get_book_embedding(conn, book_id):
    """Get the embedding for a specific book"""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT embedding
            FROM books
            WHERE id = %s AND embedding IS NOT NULL
        """, (book_id,))
        
        result = cursor.fetchone()
        cursor.close()
        
        if result and result[0]:
            embedding = result[0]
            # Handle different embedding formats
            if isinstance(embedding, str):
                # Parse string embedding (old format)
                embedding_str = embedding.strip('[]')
                embedding_list = [float(x.strip()) for x in embedding_str.split(',') if x.strip()]
                return embedding_list
            elif hasattr(embedding, '__iter__') and not isinstance(embedding, str):
                # Handle array/list type embeddings (new format)
                embedding_list = list(embedding)
                return embedding_list
            else:
                # Fallback for other types
                return embedding
        return None
    except Exception as e:
        st.error(f"❌ Error getting book embedding: {e}")
        return None

def get_book_recommendations(conn, reference_book_id, limit=10, exclude_book_id=None):
    """Get book recommendations using pgvector similarity search"""
    try:
        cursor = conn.cursor()
        
        if exclude_book_id:
            query = """
                SELECT b.id, b.title, b.embedding <=> (SELECT embedding FROM books WHERE id = %s) as distance,
                       AVG(r.rating) as avg_rating, COUNT(r.rating) as num_ratings
                FROM books b
                LEFT JOIN ratings r ON b.id = r.book_id
                WHERE b.embedding IS NOT NULL AND b.id != %s
                AND b.embedding <=> (SELECT embedding FROM books WHERE id = %s) < 2.0
                GROUP BY b.id, b.title, b.embedding
                LIMIT %s
            """
            
            cursor.execute(query, (reference_book_id, exclude_book_id, reference_book_id, limit))
        else:
            # This case shouldn't happen since we always exclude the selected book
            cursor.execute("""
                SELECT id, title, embedding <=> (SELECT embedding FROM books WHERE id = %s) as distance
                FROM books
                WHERE embedding IS NOT NULL
                ORDER BY embedding <=> (SELECT embedding FROM books WHERE id = %s)
                LIMIT %s
            """, (reference_book_id, reference_book_id, limit))
        
        results = cursor.fetchall()
        cursor.close()
        
        recommendations = [
            {
                'id': row[0],
                'title': row[1],
                'similarity_score': max(0, 1 - row[2]),  # Convert cosine distance to similarity
                'avg_rating': float(row[3]) if row[3] else None,
                'num_ratings': row[4] if row[4] else 0
            }
            for row in results
        ]
        
        # Sort by similarity score (highest first)
        recommendations.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        return recommendations
    except Exception as e:
        st.error(f"❌ Error getting recommendations: {e}")
        return []

def get_rating_analytics(conn):
    """Get rating analytics for visualization"""
    try:
        cursor = conn.cursor()
        
        # Average rating over time
        cursor.execute("""
            SELECT 
                DATE(ts) as date,
                AVG(rating) as avg_rating,
                COUNT(*) as num_ratings
            FROM ratings
            WHERE ts >= NOW() - INTERVAL '30 days'
            GROUP BY DATE(ts)
            ORDER BY date
        """)
        
        rating_trend = cursor.fetchall()
        
        # Top rated books
        cursor.execute("""
            SELECT 
                b.title,
                AVG(r.rating) as avg_rating,
                COUNT(r.rating) as num_ratings
            FROM books b
            JOIN ratings r ON b.id = r.book_id
            GROUP BY b.id, b.title
            HAVING COUNT(r.rating) >= 3
            ORDER BY avg_rating DESC, num_ratings DESC
            LIMIT 10
        """)
        
        top_books = cursor.fetchall()
        
        cursor.close()
        
        return rating_trend, top_books
    except Exception as e:
        st.error(f"❌ Error getting analytics: {e}")
        return [], []

def main():
    """Main application function"""
    st.title("📚 Bookstore Recommendations Demo")
    st.markdown("---")
    
    # Sidebar for controls
    st.sidebar.header("🎛️ Controls")
    
    # Database connection
    conn = get_database_connection()
    st.sidebar.success("✅ Connected to Aiven PostgreSQL")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("🔍 Book Recommendations")
        st.markdown("**Step 1:** Select a book you love from the dropdown below. **Step 2:** Get AI-powered recommendations for similar books using vector similarity search.")
        
        # Get all books for selection
        all_books = get_all_books(conn)
        
        if all_books:
            # Book selection
            st.subheader("📚 Select a Book You Love")
            
            # Create a searchable dropdown
            book_options = {f"{book['title']} (ID: {book['id']})": book['id'] for book in all_books}
            selected_book_display = st.selectbox(
                "Choose a book to get similar recommendations:",
                options=list(book_options.keys()),
                index=0,
                help="Select a book you enjoy to find similar books you might love"
            )
            
            selected_book_id = book_options[selected_book_display]
            selected_book_title = selected_book_display.split(" (ID:")[0]
            
            # Get selected book rating
            selected_avg_rating, selected_num_ratings = get_book_rating(conn, selected_book_id)
            
            # Show selected book info with rating
            if selected_avg_rating:
                st.info(f"🎯 Selected: **{selected_book_title}** (⭐ {selected_avg_rating:.1f} from {selected_num_ratings} ratings)")
            else:
                st.info(f"🎯 Selected: **{selected_book_title}** (No ratings yet)")
            
            # Recommendation controls
            st.subheader("⚙️ Recommendation Settings")
            num_recommendations = st.slider("Number of recommendations", 5, 20, 10)
            
            if st.button("🎯 Get Similar Books", type="primary"):
                with st.spinner(f"Finding books similar to '{selected_book_title}'..."):
                    # Get the embedding for the selected book
                    book_embedding = get_book_embedding(conn, selected_book_id)
                    
                    if book_embedding:
                        # Get recommendations based on the selected book's ID
                        recommendations = get_book_recommendations(
                            conn, 
                            selected_book_id, 
                            num_recommendations, 
                            exclude_book_id=selected_book_id
                        )
                        
                        if recommendations:
                            st.success(f"✨ Found {len(recommendations)} books similar to '{selected_book_title}'!")
                            
                            # Display recommendations in a table
                            df_recommendations = pd.DataFrame(recommendations)
                            df_recommendations['similarity_score'] = df_recommendations['similarity_score'].round(3)
                            # Convert to intuitive 0-100% scale where 100% = perfect match
                            df_recommendations['similarity_percentage'] = (df_recommendations['similarity_score'] * 100).round(0).astype(int)
                            # Ensure percentages are within 0-100 range
                            df_recommendations['similarity_percentage'] = df_recommendations['similarity_percentage'].clip(0, 100)
                            
                            # Add rating column
                            df_recommendations['rating_display'] = df_recommendations.apply(
                                lambda row: f"⭐ {row['avg_rating']:.1f} ({row['num_ratings']})" if row['avg_rating'] else "No ratings",
                                axis=1
                            )
                            
                            st.dataframe(
                                df_recommendations[['title', 'rating_display', 'similarity_percentage', 'similarity_score']],
                                column_config={
                                    'title': '📖 Similar Book Title',
                                    'rating_display': '⭐ Rating',
                                    'similarity_percentage': st.column_config.NumberColumn(
                                        '🎯 Similarity %',
                                        format="%d%%",
                                        help="How similar this book is to your selection (0-100%)"
                                    ),
                                    'similarity_score': st.column_config.NumberColumn(
                                        '📊 Raw Score',
                                        format="%.3f",
                                        help="Raw similarity score (0-1 scale)"
                                    )
                                },
                                hide_index=True
                            )
                            
                            # Show explanation
                            st.markdown("""
                            **How it works:**
                            
                            **📚 What are Embeddings?**
                            - Each book gets converted into a **vector** (a list of numbers) that represents its content
                            - This vector captures the book's themes, style, and characteristics
                            - Think of it as a unique "fingerprint" for each book
                            
                            **🔍 Finding Similar Books:**
                            - We compare your selected book's vector with all other book vectors
                            - Books with similar content have similar vectors
                            - **Higher percentages** mean more similar books
                            
                            **⚡ The Magic:**
                            - AI understands what books are about at a deep level
                            - This finds books that are conceptually similar, not just keyword matches
                            - Same technology used by Netflix, Amazon, and Spotify for recommendations!
                            """)
                        else:
                            st.warning("No similar books found. Try selecting a different book.")
                    else:
                        st.error("Could not get embedding for the selected book. Try another book.")
        else:
            st.warning("No books found in the database. Please run 'make seed-data' first.")
    
    with col2:
        st.header("📊 Quick Stats")
        
        try:
            cursor = conn.cursor()
            
            # Get basic stats
            cursor.execute("SELECT COUNT(*) FROM books")
            book_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM ratings")
            rating_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT AVG(rating) FROM ratings")
            avg_rating = cursor.fetchone()[0]
            
            cursor.close()
            
            # Display stats
            st.metric("📚 Total Books", book_count)
            st.metric("⭐ Total Ratings", rating_count)
            # Convert decimal.Decimal to float for display
            avg_rating_float = float(avg_rating) if avg_rating else None
            st.metric("📈 Average Rating", f"{avg_rating_float:.2f}" if avg_rating_float else "N/A")
            
        except Exception as e:
            st.error(f"Error getting stats: {e}")
    
    # Analytics section
    st.markdown("---")
    st.header("📈 Rating Analytics")
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("📊 Rating Trends (Last 30 Days)")
        
        rating_trend, top_books = get_rating_analytics(conn)
        
        if rating_trend:
            df_trend = pd.DataFrame(rating_trend, columns=['date', 'avg_rating', 'num_ratings'])
            
            fig = px.line(
                df_trend, 
                x='date', 
                y='avg_rating',
                title='Average Rating Over Time',
                labels={'avg_rating': 'Average Rating', 'date': 'Date'}
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No rating data available for the last 30 days.")
    
    with col4:
        st.subheader("🏆 Top Rated Books")
        
        if top_books:
            df_top = pd.DataFrame(top_books, columns=['title', 'avg_rating', 'num_ratings'])
            # Convert decimal.Decimal to float before rounding
            df_top['avg_rating'] = df_top['avg_rating'].astype(float).round(2)
            
            # Truncate long titles for display
            df_top['title_short'] = df_top['title'].apply(
                lambda x: x[:40] + "..." if len(x) > 40 else x
            )
            
            fig = px.bar(
                df_top.head(8),
                x='avg_rating',
                y='title_short',
                orientation='h',
                title='Top Rated Books (min 3 ratings)',
                labels={'avg_rating': 'Average Rating', 'title_short': 'Book Title'}
            )
            fig.update_layout(height=400, yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No top rated books available.")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>🚀 Powered by Aiven PostgreSQL with pgvector | 
        <a href='https://aiven.io' target='_blank'>Learn More</a></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 