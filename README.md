# Social Justice Library Backend

## Overview
The Social Justice Library backend service connects current news articles with relevant educational books. It analyzes news content using Claude AI to suggest books that provide deeper context and understanding of social justice issues.

## Features
- Fetches and analyzes social justice news articles
- Suggests relevant books based on article content
- Provides API endpoints for articles, books, and topics
- Automatic content processing with AI analysis

## Getting Started

### Prerequisites
- Python 3.12+
- PostgreSQL
- API keys for:
  - Guardian News API
  - Google Books API
  - Anthropic Claude API

### Installation

1. Clone the repository
```bash
git clone [repository-url]
cd sjl-back-end
```

2. Create and activate a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Set up environment variables
```bash
# Create .env file with:
GUARDIAN_API_KEY=your_key
GUARDIAN_BASE_URL="https://content.guardianapis.com"

GOOGLE_BOOKS_API_KEY=your_key
GOOGLE_BOOKS_BASE_URL="https://www.googleapis.com/books/v1/volumes"

ANTHROPIC_API_KEY=your_key
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/sjl_db
```

5. Initialize the database
```bash
alembic upgrade head
```

6. Run the development server
```bash
uvicorn app.main:app --reload
```

## Project Structure

```
sjl-back-end/
├── alembic/              # Database migrations
├── app/
│   ├── api/             # API routes and endpoints
│   │   ├── system/      # System endpoints (health checks)
│   │   └── v1/         # API version 1 endpoints
│   ├── core/            # Core configurations
│   ├── crud/            # Database operations
│   ├── models/          # SQLAlchemy models
│   ├── schemas/         # Pydantic schemas
│   └── services/        # External services integration
├── tests/               # Test suite
└── requirements.txt     # Project dependencies
```

## Key Components

### Services
- **GuardianNewsService**: Fetches social justice news articles with initial filter words for Social Justice
- **AnthropicService**: Analyzes articles relevance, generates Google Books search keywords, analyzes and determines book relevance to the article
- **GoogleBooksService**: Searches and retrieves book information
- **ContentProcessor**: Orchestrates the content processing workflow

### Database Models
- **Article**: News articles with their metadata
- **Book**: Educational books with descriptions
- **Topic**: Social justice topics for categorization
- **Associations**: Relationships between articles, books, and topics

## API Endpoints

### Articles
- `GET /api/v1/articles` - List articles (with pagination)
- `GET /api/v1/articles/{id}` - Get article details
- `GET /api/v1/articles/{id}/books` - Get related books for an article

### Books
- `GET /api/v1/books` - List books (with pagination)
- `GET /api/v1/books/{id}` - Get book details
- `GET /api/v1/books/isbn/{isbn}` - Get book by ISBN

### Topics
- `GET /api/v1/topics` - List topics
- `GET /api/v1/topics/{id}/articles` - Get articles for a topic

## Development

### Running Tests
```bash
pytest
```

### Database Migrations
```bash
# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
```

## Troubleshooting

### Common Issues

1. Database Connection Issues
   - Check DATABASE_URL in .env
   - Ensure PostgreSQL is running
   - Verify database user permissions

2. API Key Issues
   - Verify all API keys in .env
   - Check API service status
   - Monitor API rate limits

3. Content Processing Issues
   - Check logs for specific error messages
   - Verify article URLs are accessible
   - Monitor external service responses

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Submit a pull request with description

## License
[Your License]
