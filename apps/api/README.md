# Git Search API

API service for analyzing GitHub repositories and generating documentation.

## Features
- Analyze GitHub repositories using repo2text
- Generate AI summaries using Google Gemini
- Create various documentation formats (README, documentation, social media posts)
- Batch process multiple repositories
- Website scraping to extract repository URLs
- Twitter/X posting of repository information

## Prerequisites
- Python 3.12
- Supabase account and project
- Google AI API key
- Firecrawl API key (for website scraping)
- Twitter/X API credentials (for posting tweets)

## Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd apps/api
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Install Playwright browsers:
   ```bash
   playwright install chromium
   ```

5. Create a `.env` file based on `.env.example` and fill in your credentials.

6. Run the application:
   ```bash
   uvicorn main:app --reload
   ```

## Docker Setup

You can also run the application using Docker:

1. Build the Docker image:
   ```bash
   docker build -t git-search-api .
   ```

2. Run the container:
   ```bash
   docker run -p 8000:8000 --env-file .env git-search-api
   ```

### Production Mode
Using docker-compose:
   ```bash
   docker-compose up
   ```

### Development Mode (with hot reloading)
Using docker-compose.dev.yml:
   ```bash
   docker-compose -f docker-compose.dev.yml up
   ```

This development setup includes:
- Hot reloading enabled (`--reload` flag)
- Volume mounting for live file watching
- Development port mapping (8000:8000)

## API Documentation

Once the server is running, you can access the API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Environment Variables

Refer to `.env.example` for all required environment variables.

## Endpoints

- `POST /api/analyze` - Start repository analysis
- `GET /api/tasks/{task_id}` - Get task status
- `GET /api/tasks/{task_id}/result` - Get analysis result
- `POST /api/batch/process` - Start batch processing
- `POST /api/scrape/website` - Scrape website for repositories
- `POST /api/twitter/post` - Post repository tweets
- `POST /api/convert-readme-to-image` - Convert README to image and save to Supabase Storage

## Development

For development with hot reloading:
```bash
uvicorn main:app --reload
```

## License

MIT

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your actual values
```

4. Start Redis (required for background tasks):
```bash
# Using Docker
docker run -d -p 6379:6379 redis:alpine

# Or install Redis locally and start it
redis-server
```

5. Run the development server:
```bash
npm run dev
# or
uvicorn main:app --reload
```

6. Start the background worker (in a separate terminal):
```bash
npm run worker
# or
python start_worker.py
```

The API will be available at http://localhost:8000

## API Documentation

- Interactive API docs: http://localhost:8000/docs
- ReDoc documentation: http://localhost:8000/redoc

## Endpoints

### Core API
- `GET /` - Root endpoint with API information
- `GET /health` - Health check

### Repository Analysis
- `POST /api/analysis/analyze` - Start repository analysis
- `GET /api/analysis/tasks/{task_id}` - Get task status
- `GET /api/analysis/tasks/{task_id}/result` - Get analysis result
- `GET /api/analysis/repositories/{repo_id}` - Get repository details
- `GET /api/analysis/repositories/{repo_id}/analysis` - Get repository analysis
- `GET /api/analysis/repositories/{repo_id}/documents` - Get repository documents
- `GET /api/analysis/repositories` - List all repositories
- `DELETE /api/analysis/repositories/{repo_id}` - Delete repository (not implemented)

### Background Tasks
- `GET /api/tasks/` - List active tasks
- `GET /api/tasks/{task_id}` - Get specific task status
- `DELETE /api/tasks/{task_id}` - Cancel task
- `GET /api/tasks/stats/summary` - Get task statistics
- `POST /api/tasks/cleanup` - Clean up completed tasks

## Background Task Processing

The API uses Celery with Redis for background task processing. Repository analysis tasks are processed asynchronously:

1. **Submit Analysis**: `POST /api/analysis/analyze` with GitHub URL
2. **Monitor Progress**: `GET /api/analysis/tasks/{task_id}` 
3. **Get Results**: `GET /api/analysis/tasks/{task_id}/result`

### Task Flow

1. User submits GitHub URL
2. Task is queued for background processing
3. Worker clones repository using repo2text library
4. Repository is analyzed and content extracted
5. Results are saved to Supabase database
6. User can retrieve results via API

### Required Services

- **Redis**: Message broker and result backend
- **Celery Worker**: Background task processor  
- **Supabase**: Database for storing results

## Example Usage

### Start Repository Analysis

```bash
curl -X POST "http://localhost:8000/api/analysis/analyze" \
     -H "Content-Type: application/json" \
     -d '{
       "github_url": "https://github.com/owner/repository",
       "user_id": "optional_user_id"
     }'
```

Response:
```json
{
  "task_id": "abc123-def456-ghi789",
  "status": "pending",
  "message": "Repository analysis started for https://github.com/owner/repository",
  "created_at": "2024-01-01T12:00:00Z"
}
```

### Check Task Status

```bash
curl "http://localhost:8000/api/analysis/tasks/abc123-def456-ghi789"
```

Response:
```json
{
  "task_id": "abc123-def456-ghi789",
  "status": "started",
  "message": "Analyzing repository structure",
  "progress": 70,
  "repo_id": "repo-uuid-here"
}
```

### Get Analysis Results

```bash
curl "http://localhost:8000/api/analysis/tasks/abc123-def456-ghi789/result"
```

This returns the complete repository analysis including:
- Repository metadata
- Analysis statistics (files, lines, tokens, etc.)
- Generated documents with full repository content
- Processing information