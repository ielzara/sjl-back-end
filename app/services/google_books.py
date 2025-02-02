from typing import List
import httpx
import json
import logging
from app.schemas.book import BookCreate
from app.core.config import settings

logger = logging.getLogger(__name__)

# Filter constants
EXCLUDED_TERMS = {
    'sql', 'programming', 'database', 'oracle', 'software', 'computer', 'coding',
    'textbook', 'manual', 'handbook', 'guide to', 'tutorial', 'workbook',
    'certification', 'exam prep', 'dictionary', 'encyclopedia',
}

SUBJECT_FILTERS = [
    'Social Science', 'Political Science', 'History', 'Law', 'Education',
    'Philosophy', 'Sociology', 'Psychology', 'Social Justice', 'Medical', 'Art'
]

class GoogleBooksService:
    def __init__(self):
        self.base_url = settings.GOOGLE_BOOKS_BASE_URL
        self.api_key = settings.GOOGLE_BOOKS_API_KEY
        logger.info(f"Initialized GoogleBooksService with base_url: {self.base_url}")

    async def search_books(self, query: str, final_results: int = 5) -> List[BookCreate]:
        """Search Google Books API"""
        try:
            logger.info(f"Raw query received: {query}")
            
            if not query:
                logger.warning("Empty query received")
                return []

            # Clean and prepare search terms
            search_terms = [query.strip('"')] if isinstance(query, str) else []
            # Remove any search_terms text if it appears literally
            search_terms = [term.replace('search_terms', '').strip() for term in search_terms]
            search_terms = [term for term in search_terms if term]
            
            logger.info(f"Using search terms: {search_terms}")
            
            all_books = []
            
            for term in (search_terms if isinstance(search_terms, list) else [search_terms]):
                if not isinstance(term, str):
                    logger.warning(f"Skipping non-string term: {term}")
                    continue
                    
                clean_term = term.replace(" AND ", " ").strip()
                logger.info(f"Searching for cleaned term: {clean_term}")

                params = {
                    "q": clean_term,
                    "maxResults": 20,  # Increased to get more candidates for analysis
                    "printType": "books",
                    "langRestrict": "en",
                    "orderBy": "relevance",
                    "key": self.api_key
                }
                
                logger.info(f"Making request with params (excluding key)")

                async with httpx.AsyncClient() as client:
                    response = await client.get(self.base_url, params=params)
                    await response.aclose()  # Ensure connection is closed
                    data = response.json()  # This is now synchronous as response.json() returns the parsed data directly

                    total_items = data.get("totalItems", 0)
                    items = data.get("items", [])
                    logger.info(f"Found {total_items} items, processing up to {len(items)}")

                    for item in items:
                        volume_info = item.get("volumeInfo", {})
                        title = volume_info.get("title", "")
                        
                        # Skip books with excluded terms in title
                        if any(term in title.lower() for term in EXCLUDED_TERMS):
                            logger.info(f"Skipping technical/reference book: {title}")
                            continue
                            
                        # Check if book has relevant subjects
                        subjects = volume_info.get("categories", [])
                        if not any(any(subject.lower() in category.lower() for subject in SUBJECT_FILTERS) 
                                 for category in subjects):
                            logger.info(f"Skipping book with non-relevant subjects: {title} - {subjects}")
                            continue

                        # Get publication date and skip if too old
                        published_date = volume_info.get("publishedDate", "")
                        if published_date:
                            try:
                                year = int(published_date[:4])
                                if year < 1990:  # Skip books older than 1990 for now
                                    logger.info(f"Skipping older book: {title} ({year})")
                                    continue
                            except (ValueError, IndexError):
                                pass

                        # Get ISBN
                        isbn = None
                        for identifier in volume_info.get("industryIdentifiers", []):
                            if identifier.get("type") in ["ISBN_10", "ISBN_13"]:
                                isbn = identifier.get("identifier")
                                if len(isbn) == 10:  # Convert ISBN-10 to ISBN-13
                                    isbn = "978" + isbn[:-1]
                                # Pad ISBN if needed
                                if len(isbn) == 11:
                                    isbn = isbn + "00"
                                break

                        if not isbn or len(isbn) not in [10, 13]:
                            logger.info(f"Skipping book with invalid ISBN: {title}")
                            continue

                        try:
                            # Truncate description if needed
                            description = volume_info.get("description", "No description available")
                            if len(description) > 500:
                                description = description[:497] + "..."

                            book = BookCreate(
                                title=title,
                                author=", ".join(volume_info.get("authors", ["Unknown Author"])),
                                description=description,
                                url=volume_info.get("infoLink", ""),
                                cover_url=volume_info.get("imageLinks", {}).get("thumbnail", ""),
                                isbn=isbn
                            )
                            
                            if not any(existing.isbn == book.isbn for existing in all_books):
                                all_books.append(book)
                                logger.info(f"Added book: {book.title}")

                        except Exception as e:
                            logger.error(f"Error creating book {title}: {str(e)}")
                            continue

            logger.info(f"Total books found: {len(all_books)}")
            # Don't slice here - return all books for further analysis
            return all_books

        except Exception as e:
            logger.error(f"Error in search_books: {str(e)}", exc_info=True)
            return []