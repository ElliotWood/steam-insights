"""List all genres and tags to verify cleanup"""
from src.database.connection import SessionLocal
from sqlalchemy import text

s = SessionLocal()

print("=== ALL GENRES ===")
genres = s.execute(text("SELECT name FROM genres ORDER BY name")).fetchall()
for g in genres:
    print(f"  {g[0]}")
print(f"\nTotal genres: {len(genres)}")

print("\n=== SAMPLE TAGS (first 50) ===")
tags = s.execute(text("SELECT name FROM tags ORDER BY name LIMIT 50")).fetchall()
for t in tags:
    print(f"  {t[0]}")
print(f"\nShowing first 50 tags")

print("\n=== CHECKING FOR NON-ASCII ===")
non_ascii_genres = s.execute(text("SELECT name FROM genres WHERE name ~ '[^\\x00-\\x7F]'")).fetchall()
print(f"Non-ASCII genres: {len(non_ascii_genres)}")
for g in non_ascii_genres[:10]:
    print(f"  {g[0]}")

non_ascii_tags = s.execute(text("SELECT name FROM tags WHERE name ~ '[^\\x00-\\x7F]' LIMIT 20")).fetchall()
print(f"\nNon-ASCII tags: {len(non_ascii_tags)}")
for t in non_ascii_tags[:10]:
    print(f"  {t[0]}")

s.close()
