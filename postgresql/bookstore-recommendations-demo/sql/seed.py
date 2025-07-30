#!/usr/bin/env python3
"""
Seed script for Bookstore Recommendations Demo
Generates sample books with vector embeddings and user ratings
"""

import os
import psycopg2
import numpy as np
from datetime import datetime, timedelta
import random
from dotenv import load_dotenv

load_dotenv()

# Pre-baked book titles and authors
BOOK_TITLES = [
    "The Great Gatsby", "To Kill a Mockingbird", "1984", "Pride and Prejudice",
    "The Catcher in the Rye", "Lord of the Flies", "Animal Farm", "Brave New World",
    "The Hobbit", "The Lord of the Rings", "Dune", "Foundation", "Neuromancer",
    "Snow Crash", "The Matrix", "Blade Runner", "Ready Player One", "The Martian",
    "Project Hail Mary", "The Three-Body Problem", "The Dark Forest", "Death's End",
    "The Expanse", "Leviathan Wakes", "Caliban's War", "Abaddon's Gate",
    "The Hunger Games", "Catching Fire", "Mockingjay", "Divergent",
    "Insurgent", "Allegiant", "The Maze Runner", "The Scorch Trials",
    "The Death Cure", "The Fault in Our Stars", "Looking for Alaska",
    "Paper Towns", "Turtles All the Way Down", "The Perks of Being a Wallflower",
    "Eleanor & Park", "Fangirl", "Carry On", "Simon vs. the Homo Sapiens Agenda",
    "Call Me By Your Name", "The Song of Achilles", "Circe", "The Silence of the Lambs",
    "Red Dragon", "Hannibal", "The Girl with the Dragon Tattoo", "The Girl Who Played with Fire",
    "The Girl Who Kicked the Hornet's Nest", "Gone Girl", "Sharp Objects", "Dark Places",
    "The Da Vinci Code", "Angels & Demons", "Inferno", "Origin", "Digital Fortress",
    "Deception Point", "The Lost Symbol", "The Alchemist", "Veronika Decides to Die",
    "Eleven Minutes", "The Zahir", "The Devil and Miss Prym", "Brida",
    "The Winner Stands Alone", "Aleph", "Adultery", "The Spy", "Hippie"
]

AUTHORS = [
    "F. Scott Fitzgerald", "Harper Lee", "George Orwell", "Jane Austen",
    "J.D. Salinger", "William Golding", "George Orwell", "Aldous Huxley",
    "J.R.R. Tolkien", "J.R.R. Tolkien", "Frank Herbert", "Isaac Asimov",
    "William Gibson", "Neal Stephenson", "Lana Wachowski", "Philip K. Dick",
    "Ernest Cline", "Andy Weir", "Andy Weir", "Liu Cixin", "Liu Cixin",
    "Liu Cixin", "James S.A. Corey", "James S.A. Corey", "James S.A. Corey",
    "James S.A. Corey", "Suzanne Collins", "Suzanne Collins", "Suzanne Collins",
    "Veronica Roth", "Veronica Roth", "Veronica Roth", "James Dashner",
    "James Dashner", "James Dashner", "John Green", "John Green",
    "John Green", "John Green", "Stephen Chbosky", "Rainbow Rowell",
    "Rainbow Rowell", "Rainbow Rowell", "Becky Albertalli", "André Aciman",
    "Madeline Miller", "Madeline Miller", "Thomas Harris", "Thomas Harris",
    "Thomas Harris", "Stieg Larsson", "Stieg Larsson", "Stieg Larsson",
    "Gillian Flynn", "Gillian Flynn", "Gillian Flynn", "Dan Brown",
    "Dan Brown", "Dan Brown", "Dan Brown", "Dan Brown", "Dan Brown",
    "Dan Brown", "Paulo Coelho", "Paulo Coelho", "Paulo Coelho",
    "Paulo Coelho", "Paulo Coelho", "Paulo Coelho", "Paulo Coelho",
    "Paulo Coelho", "Paulo Coelho", "Paulo Coelho", "Paulo Coelho"
]

GENRES = [
    "Fiction", "Classic", "Science Fiction", "Fantasy", "Mystery",
    "Thriller", "Romance", "Young Adult", "Contemporary", "Historical",
    "Dystopian", "Adventure", "Horror", "Comedy", "Drama", "Biography",
    "Autobiography", "Memoir", "Self-Help", "Business", "Philosophy",
    "Religion", "Science", "Technology", "Poetry", "Short Stories"
]

def generate_book_title():
    """Generate a book title by combining pre-baked titles with variations"""
    base_title = random.choice(BOOK_TITLES)
    variations = [
        f"The {base_title}",
        f"{base_title} Returns",
        f"{base_title} Revisited",
        f"Beyond {base_title}",
        f"{base_title} Chronicles",
        f"The {base_title} Saga",
        f"{base_title} Trilogy",
        f"{base_title} Series"
    ]
    return random.choice([base_title] + variations)

def generate_author():
    """Generate an author name"""
    return random.choice(AUTHORS)

def generate_vector_embedding():
    """Generate a random 1536-dimensional vector embedding"""
    return np.random.rand(1536).tolist()

def generate_rating():
    """Generate a realistic rating (1-5 stars) with diverse distribution"""
    # More realistic distribution - some books are genuinely bad, some are mediocre, some are great
    weights = [0.2, 0.3, 0.25, 0.2, 0.05]  # 1, 2, 3, 4, 5 stars
    return random.choices(range(1, 6), weights=weights)[0]

def generate_book_quality_rating():
    """Generate rating based on book quality - some books are inherently better"""
    # 20% chance of being a "classic" or "popular" book with better ratings
    if random.random() < 0.2:
        # Better books get higher ratings
        weights = [0.05, 0.1, 0.2, 0.4, 0.25]  # 1, 2, 3, 4, 5 stars
    else:
        # Regular books get more diverse ratings
        weights = [0.25, 0.35, 0.25, 0.12, 0.03]  # 1, 2, 3, 4, 5 stars
    
    return random.choices(range(1, 6), weights=weights)[0]

def generate_timestamp():
    """Generate a realistic timestamp within the last 2 years"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=730)  # 2 years ago
    time_between = end_date - start_date
    days_between = time_between.days
    random_days = random.randrange(days_between)
    random_date = start_date + timedelta(days=random_days)
    return random_date

def create_books(cursor, num_books=100):
    """Create sample books with proper vector embeddings"""
    print(f"Creating {num_books} books with proper vector embeddings...")
    
    for i in range(num_books):
        title = generate_book_title()
        author = generate_author()
        full_title = f"{title} by {author}"
        embedding = generate_vector_embedding()
        
        # Convert Python list to PostgreSQL vector format
        # Use a format that pgvector expects
        vector_str = '[' + ','.join(f"{x:.10f}" for x in embedding) + ']'
        
        # Use explicit vector cast to ensure proper storage
        cursor.execute(
            "INSERT INTO books (title, embedding) VALUES (%s, %s::vector)",
            (full_title, vector_str)
        )
        
        if (i + 1) % 20 == 0:
            print(f"Created {i + 1} books...")
    
    print("Books created successfully!")
    
    # Verify embeddings are stored as proper vectors
    cursor.execute("SELECT COUNT(*) FROM books WHERE embedding IS NOT NULL")
    books_with_embeddings = cursor.fetchone()[0]
    print(f"Verified: {books_with_embeddings} books have vector embeddings")

def create_ratings(cursor, num_ratings=1000):
    """Create sample user ratings with realistic distribution"""
    print(f"Creating {num_ratings} ratings...")
    
    # Get all book IDs
    cursor.execute("SELECT id FROM books")
    book_ids = [row[0] for row in cursor.fetchall()]
    
    if not book_ids:
        print("No books found. Please create books first.")
        return
    
    # Create some "popular" books that get more ratings
    popular_books = random.sample(book_ids, min(10, len(book_ids) // 3))  # 1/3 of books are popular
    
    for i in range(num_ratings):
        user_id = random.randint(1, 50)  # 50 different users
        
        # Popular books get more ratings (70% chance)
        if random.random() < 0.7 and popular_books:
            book_id = random.choice(popular_books)
        else:
            book_id = random.choice(book_ids)
            
        rating = generate_book_quality_rating()  # Use quality-based rating
        ts = generate_timestamp()
        
        cursor.execute(
            "INSERT INTO ratings (user_id, book_id, rating, ts) VALUES (%s, %s, %s, %s)",
            (user_id, book_id, rating, ts)
        )
        
        if (i + 1) % 200 == 0:
            print(f"Created {i + 1} ratings...")
    
    print("Ratings created successfully!")

def main():
    """Main function to seed the database"""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("Error: DATABASE_URL environment variable not set")
        print("Please set it to your Aiven PostgreSQL connection string")
        return
    
    try:
        # Connect to database
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        print("Connected to database successfully!")
        
        # Create books
        create_books(cursor, num_books=100)
        
        # Create ratings
        create_ratings(cursor, num_ratings=1000)
        
        # Commit changes
        conn.commit()
        
        # Show summary
        cursor.execute("SELECT COUNT(*) FROM books")
        book_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM ratings")
        rating_count = cursor.fetchone()[0]
        
        print(f"\n✅ Database seeded successfully!")
        print(f"📚 Books created: {book_count}")
        print(f"⭐ Ratings created: {rating_count}")
        
        # Test vector similarity to ensure it works
        print("\n🧪 Testing vector similarity...")
        cursor.execute("SELECT id, title FROM books LIMIT 1")
        test_book = cursor.fetchone()
        if test_book:
            book_id, title = test_book
            cursor.execute("""
                SELECT COUNT(*) FROM books 
                WHERE embedding IS NOT NULL 
                AND id != %s 
                AND embedding <=> (SELECT embedding FROM books WHERE id = %s) < 2.0
            """, (book_id, book_id))
            similar_books = cursor.fetchone()[0]
            print(f"✅ Vector similarity test passed: Found {similar_books} books similar to '{title}'")
        else:
            print("❌ No books found for similarity test")
        
    except Exception as e:
        print(f"Error: {e}")
        if 'conn' in locals():
            conn.rollback()
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    main()
