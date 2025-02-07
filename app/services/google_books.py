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
    'Philosophy', 'Sociology', 'Psychology', 'Social Justice', 'Medical', 'Art', 'Business & Economics'
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
                    "maxResults": 20,  # Max results per query
                    "printType": "books",
                    "langRestrict": "en",
                    "orderBy": "relevance",
                    "key": self.api_key
                }
                
                logger.info("Making request with params (excluding key)")

                async with httpx.AsyncClient() as client:
                    response = await client.get(self.base_url, params=params)
                    await response.aclose()  # Ensure connection is closed
                    data = response.json() # Parse JSON response

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
                            
                        # # Check if book has relevant subjects
                        # subjects = volume_info.get("categories", [])
                        # if not any(any(subject.lower() in category.lower() for subject in SUBJECT_FILTERS) 
                        #          for category in subjects):
                        #     logger.info(f"Skipping book with non-relevant subjects: {title} - {subjects}")
                        #     continue

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

                        # Skip books without covers
                        if not volume_info.get("imageLinks", {}).get("thumbnail"):
                            logger.info(f"Skipping book without cover: {title}")
                            continue

                        # Get ISBN
                        isbn = None
                        for identifier in volume_info.get("industryIdentifiers", []):
                            if identifier.get("type") in ["ISBN_10", "ISBN_13"]:
                                isbn = identifier.get("identifier")
                                break
                                

                        # Create a unique identifier based on multiple factors
                        unique_id = None
                        if isbn:
                            unique_id = isbn
                            logger.info(f"Using ISBN as unique identifier for '{title}'")
                        else:
                            # Use Google Books info_link as unique identifier
                            info_link = volume_info.get("infoLink", "")
                            if info_link:
                                unique_id = info_link.split('?')[0]  # Remove query parameters
                                logger.info(f"Using Google Books link as unique identifier for '{title}'")
                            else:
                                # Fallback: combine title and author
                                authors = ", ".join(volume_info.get("authors", ["Unknown Author"]))
                                unique_id = f"{title}|{authors}"
                                logger.info(f"Using title+author as unique identifier for '{title}' by {authors}")

                        try:
                            # Truncate description if needed
                            description = volume_info.get("description", "No description available")

                            book = BookCreate(
                                title=title,
                                author=", ".join(volume_info.get("authors", ["Unknown Author"])),
                                description=description,
                                url=volume_info.get("infoLink", ""),
                                cover_url=volume_info.get("imageLinks", {}).get("thumbnail", ""),
                                isbn=isbn or "",
                                unique_id=unique_id
                            )
                            
                            if not any(existing.unique_id == book.unique_id for existing in all_books):
                                all_books.append(book)
                                logger.info(f"Added book: {book.title}")
                            else:
                                logger.info(f"Skipping duplicate book: {book.title} (duplicate unique_id: {unique_id})")

                        except Exception as e:
                            logger.error(f"Error creating book {title}: {str(e)}")
                            continue

            logger.info(f"Total books found: {len(all_books)}")
            return all_books

        except Exception as e:
            logger.error(f"Error in search_books: {str(e)}", exc_info=True)
            return []