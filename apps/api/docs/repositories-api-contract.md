# Repositories API Contract

## Overview
This API provides comprehensive access to repository data including repository metadata, analysis results, and generated documents with full pagination support. The API features optimized bulk operations for efficient retrieval of repository analysis and document count data.

**Base URL**: `/repositories`  
**Authentication**: API Key required (via `X-API-Key` header)  
**Content Type**: `application/json`

### Key Features
- **Paginated Repository Listings** with filtering by author, status, and search terms
- **Optional Analysis Inclusion** with document counts and statistics via `include_analysis` parameter
- **Bulk Query Optimization** for efficient data retrieval at scale
- **Document Type Counting** showing total and current document counts per type

---

## Endpoints

### 1. List Repositories
Get a paginated list of repositories with optional filtering and analysis data.

**Endpoint**: `GET /repositories`

**Performance**: When `include_analysis=true`, uses optimized bulk queries (3 total database calls regardless of result size) instead of individual queries per repository.

#### Query Parameters
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `skip` | integer | No | 0 | Number of items to skip (≥ 0) |
| `limit` | integer | No | 10 | Number of items to return (1-100) |
| `author` | string | No | null | Filter by repository author |
| `status` | string | No | null | Filter by processing status |
| `search` | string | No | null | Search repositories by name or URL |
| `include_analysis` | boolean | No | false | Include latest analysis and document counts |
| `include_ai_summary` | boolean | No | false | Include AI summary in analysis data (can be large) |

#### Processing Status Values
- `pending` - Repository added but not processed
- `queued` - Repository queued for processing  
- `processing` - Currently being analyzed
- `analyzed` - Analysis completed
- `docs_generated` - Documents generated
- `completed` - All processing complete
- `failed` - Processing failed

#### Response Format (Basic)
```json
{
  "repositories": [
    {
      "id": "uuid",
      "name": "repository-name",
      "repo_url": "https://github.com/owner/repo",
      "author": "owner",
      "branch": "main",
      "twitter_link": "https://twitter.com/...",
      "processing_status": "completed",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "pagination": {
    "total": 150,
    "page": 1,
    "per_page": 10,
    "has_more": true,
    "total_pages": 15
  },
  "options": {
    "include_analysis": false
  }
}
```

#### Response Format (With Analysis, No AI Summary)
When `include_analysis=true` and `include_ai_summary=false`:
```json
{
  "repositories": [
    {
      "id": "uuid",
      "name": "repository-name",
      "repo_url": "https://github.com/owner/repo",
      "author": "owner",
      "branch": "main",
      "twitter_link": "https://twitter.com/...",
      "processing_status": "completed",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z",
      "analysis": {
        "id": "uuid",
        "repository_id": "uuid",
        "analysis_version": 1,
        "total_files_found": 45,
        "total_directories": 8,
        "files_processed": 42,
        "total_lines": 3540,
        "total_characters": 89432,
        "estimated_tokens": 22358,
        "estimated_size_bytes": 89432,
        "large_files_skipped": 1,
        "binary_files_skipped": 2,
        "encoding_errors": 0,
        "readme_image_src": "https://storage.supabase.co/...",
        "ai_summary": null,
        "description": "A brief description...",
        "forked_repo_url": "https://github.com/fork/repo",
        "twitter_link": "https://twitter.com/status/123"
      }
    }
  ],
  "pagination": { "..." },
  "options": {
    "include_analysis": true
  }
}
```

#### Response Format (With Analysis and AI Summary)
When `include_analysis=true` and `include_ai_summary=true`:
```json
{
  "repositories": [
    {
      "id": "uuid",
      "name": "repository-name",
      "analysis": {
        "id": "uuid",
        "repository_id": "uuid",
        "analysis_version": 1,
        "total_files_found": 45,
        "files_processed": 42,
        "total_lines": 3540,
        "ai_summary": "This repository contains a comprehensive React application with modern tooling...",
        "description": "A brief description...",
        "forked_repo_url": "https://github.com/fork/repo"
      }
    }
  ]
}
```

#### HTTP Status Codes
- `200` - Success
- `400` - Invalid query parameters
- `401` - Unauthorized (missing/invalid API key)
- `500` - Server error

---

### 2. Get Repository
Get detailed information about a specific repository with optional analysis data.

**Endpoint**: `GET /repositories/{repo_id}`

**Performance**: When `include_analysis=true`, fetches analysis and document data efficiently using single queries.

#### Path Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `repo_id` | UUID | Yes | Repository identifier |

#### Query Parameters
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `include_analysis` | boolean | No | false | Include latest analysis and document counts |
| `include_ai_summary` | boolean | No | false | Include AI summary in analysis data (can be large) |

#### Response Format (Basic)
```json
{
  "id": "uuid",
  "name": "repository-name",
  "repo_url": "https://github.com/owner/repo",
  "author": "owner",
  "branch": "main",
  "twitter_link": "https://twitter.com/...",
  "processing_status": "completed",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### Response Format (With Analysis)
When `include_analysis=true`:
```json
{
  "id": "uuid",
  "name": "repository-name",
  "repo_url": "https://github.com/owner/repo",
  "author": "owner",
  "branch": "main",
  "twitter_link": "https://twitter.com/...",
  "processing_status": "completed",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "analysis": {
    "id": "uuid",
    "repository_id": "uuid",
    "analysis_version": 1,
    "total_files_found": 45,
    "total_directories": 8,
    "files_processed": 42,
    "total_lines": 3540,
    "total_characters": 89432,
    "estimated_tokens": 22358,
    "estimated_size_bytes": 89432,
    "large_files_skipped": 1,
    "binary_files_skipped": 2,
    "encoding_errors": 0,
    "readme_image_src": "https://storage.supabase.co/...",
    "ai_summary": "This repository contains...",
    "description": "A brief description...",
    "forked_repo_url": "https://github.com/fork/repo",
    "twitter_link": "https://twitter.com/status/123"
  }
}
```

#### HTTP Status Codes
- `200` - Success
- `401` - Unauthorized
- `404` - Repository not found
- `500` - Server error

---

### 3. Get Repository Analysis
Get analysis data for a repository.

**Endpoint**: `GET /repositories/{repo_id}/analysis`

#### Path Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `repo_id` | UUID | Yes | Repository identifier |

#### Query Parameters
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `version` | integer | No | latest | Specific analysis version |

#### Response Format
```json
{
  "id": "uuid",
  "repository_id": "uuid",
  "analysis_version": 1,
  "total_files_found": 45,
  "total_directories": 8,
  "files_processed": 42,
  "total_lines": 3540,
  "total_characters": 89432,
  "estimated_tokens": 22358,
  "estimated_size_bytes": 89432,
  "large_files_skipped": 1,
  "binary_files_skipped": 2,
  "encoding_errors": 0,
  "readme_image_src": "https://storage.supabase.co/...",
  "ai_summary": "This repository contains...",
  "description": "A brief description...",
  "forked_repo_url": "https://github.com/fork/repo"
}
```

#### HTTP Status Codes
- `200` - Success
- `401` - Unauthorized
- `404` - Repository or analysis not found
- `500` - Server error

---

### 4. Get Repository Documents
Get paginated documents for a repository.

**Endpoint**: `GET /repositories/{repo_id}/documents`

#### Path Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `repo_id` | UUID | Yes | Repository identifier |

#### Query Parameters
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `skip` | integer | No | 0 | Number of items to skip (≥ 0) |
| `limit` | integer | No | 10 | Number of items to return (1-100) |
| `document_type` | string | No | null | Filter by document type |
| `current_only` | boolean | No | false | Only return current version documents |
| `summary_only` | boolean | No | false | Return summaries without content |

#### Common Document Types
- `repository_analysis` - Raw repository analysis
- `technical_overview` - Technical documentation
- `api_documentation` - API reference
- `user_guide` - User documentation
- `architecture_guide` - Architecture documentation
- `deployment_guide` - Deployment instructions

#### Response Format (Full Documents)
```json
{
  "documents": [
    {
      "id": "uuid",
      "repository_analysis_id": "uuid",
      "title": "Technical Overview",
      "content": "# Technical Overview\n\n...",
      "document_type": "technical_overview",
      "description": "Comprehensive technical overview",
      "version": 1,
      "is_current": true
    }
  ],
  "pagination": {
    "total": 12,
    "page": 1,
    "per_page": 10,
    "has_more": true,
    "total_pages": 2
  },
  "filters": {
    "document_type": "technical_overview",
    "current_only": false,
    "summary_only": false
  }
}
```

#### Response Format (Document Summaries)
```json
{
  "documents": [
    {
      "id": "uuid",
      "repository_analysis_id": "uuid",
      "title": "Technical Overview",
      "document_type": "technical_overview",
      "description": "Comprehensive technical overview",
      "version": 1,
      "is_current": true,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "pagination": { "..." },
  "filters": { "..." }
}
```

#### HTTP Status Codes
- `200` - Success
- `400` - Invalid query parameters
- `401` - Unauthorized
- `404` - Repository not found
- `500` - Server error

---

### 5. Get Specific Document
Get a specific document by repository and document ID.

**Endpoint**: `GET /repositories/{repo_id}/documents/{document_id}`

#### Path Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `repo_id` | UUID | Yes | Repository identifier |
| `document_id` | UUID | Yes | Document identifier |

#### Response Format
```json
{
  "id": "uuid",
  "repository_analysis_id": "uuid",
  "title": "Technical Overview",
  "content": "# Technical Overview\n\nThis document provides...",
  "document_type": "technical_overview",
  "description": "Comprehensive technical overview",
  "version": 1,
  "is_current": true
}
```

#### HTTP Status Codes
- `200` - Success
- `401` - Unauthorized
- `404` - Repository or document not found
- `500` - Server error

---

### 6. Get Repository Overview
Get complete repository overview including metadata, analysis, and document summaries.

**Endpoint**: `GET /repositories/{repo_id}/overview`

#### Path Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `repo_id` | UUID | Yes | Repository identifier |

#### Response Format
```json
{
  "repository": {
    "id": "uuid",
    "name": "repository-name",
    "repo_url": "https://github.com/owner/repo",
    "author": "owner",
    "branch": "main",
    "twitter_link": "https://twitter.com/...",
    "processing_status": "completed",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  },
  "analysis": {
    "id": "uuid",
    "repository_id": "uuid",
    "analysis_version": 1,
    "total_files_found": 45,
    "files_processed": 42,
    "ai_summary": "This repository contains...",
    "description": "A brief description..."
  },
  "documents": {
    "current_documents": [
      {
        "id": "uuid",
        "title": "Technical Overview",
        "document_type": "technical_overview",
        "version": 1,
        "is_current": true,
        "created_at": "2024-01-01T00:00:00Z"
      }
    ],
    "total_current": 5,
    "counts_by_type": {
      "technical_overview": 1,
      "api_documentation": 1,
      "user_guide": 1,
      "deployment_guide": 1,
      "repository_analysis": 1
    }
  },
  "stats": {
    "has_analysis": true,
    "has_documents": true,
    "processing_complete": true
  }
}
```

#### HTTP Status Codes
- `200` - Success
- `401` - Unauthorized
- `404` - Repository not found
- `500` - Server error

---

### 7. Get Repository Statistics
Get detailed statistics for a repository.

**Endpoint**: `GET /repositories/{repo_id}/stats`

#### Path Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `repo_id` | UUID | Yes | Repository identifier |

#### Response Format
```json
{
  "total_repositories": 25,
  "unique_authors": 15,
  "total_analyses": 30,
  "aggregate_metrics": {
    "total_files_found": 1200,
    "total_directories": 240,
    "total_lines": 85000,
    "total_characters": 2150000,
    "estimated_tokens": 537500,
    "estimated_size_bytes": 2150000
  },
  "processing_stats": {
    "files_processed": 1150,
    "binary_files_skipped": 25,
    "large_files_skipped": 15,
    "encoding_errors": 3
  },
  "average_metrics": {
    "avg_files_per_repo": 48.0,
    "avg_lines_per_repo": 3400.0,
    "avg_tokens_per_repo": 21500.0,
    "avg_size_bytes_per_repo": 86000.0
  },
  "latest_analysis": {
    "id": "uuid",
    "created_at": "2024-01-01T12:00:00Z",
    "analysis_version": 3
  }
}
```

#### HTTP Status Codes
- `200` - Success
- `401` - Unauthorized
- `404` - Repository not found
- `500` - Server error

---

## Performance Optimization

The API includes several performance optimizations for bulk operations:

### Bulk Query Strategy
When `include_analysis=true` is used:
- **List Repositories**: Uses 3 database queries total regardless of result size
  1. Fetch paginated repositories 
  2. Bulk fetch all latest analyses for returned repositories
  3. Bulk fetch all documents for those analyses
- **Single Repository**: Uses standard individual queries (2-3 queries total)

### Query Complexity
- **Without analysis**: O(1) - Single repository query
- **With analysis (list)**: O(1) - Constant 3 queries via bulk operations  
- **With analysis (single)**: O(1) - 2-3 individual queries

### Benefits
- **Reduced Database Load**: Eliminates N+1 query problems
- **Better Response Times**: Especially noticeable with large result sets
- **Scalable Performance**: Query count doesn't grow with result size

### Performance Considerations
- **Use `include_analysis=false`** for lightweight operations when analysis data isn't needed
- **Use `include_analysis=true`** when you need repository statistics and document counts
- **Pagination** works efficiently with bulk operations - larger `limit` values don't increase query count
- **Memory Usage**: Analysis inclusion adds document count processing but remains efficient

---

## Error Responses

All endpoints return consistent error response format:

```json
{
  "detail": "Error description"
}
```

### Common Error Codes
- `400 Bad Request` - Invalid request parameters
- `401 Unauthorized` - Missing or invalid API key
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server error

---

## Authentication

All endpoints require authentication via API key in the request header:

```http
X-API-Key: your-api-key-here
```

---

## Rate Limits

- **Standard Rate Limit**: 1000 requests per hour per API key
- **Burst Limit**: 100 requests per minute per API key

Rate limit headers are included in all responses:
- `X-RateLimit-Limit`: Requests allowed per hour
- `X-RateLimit-Remaining`: Requests remaining in current window
- `X-RateLimit-Reset`: Time when rate limit resets (Unix timestamp)

---

## Pagination

All paginated endpoints support consistent pagination:

### Request Parameters
- `skip`: Number of items to skip (default: 0, minimum: 0)
- `limit`: Number of items to return (default: 10, range: 1-100)

### Response Format
```json
{
  "pagination": {
    "total": 150,           // Total number of items
    "page": 1,              // Current page number (1-based)
    "per_page": 10,         // Items per page
    "has_more": true,       // Whether more items exist
    "total_pages": 15       // Total number of pages
  }
}
```

---

## Data Types

### UUID Format
All UUIDs follow the standard format: `xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx`

### Datetime Format  
All timestamps are in ISO 8601 format with UTC timezone: `2024-01-01T00:00:00Z`

### Processing Status Enum
Valid values: `pending`, `queued`, `processing`, `analyzed`, `docs_generated`, `completed`, `failed`

---

## Examples

### Get First Page of Repositories
```bash
curl -X GET "https://api.example.com/repositories?limit=10&skip=0" \
  -H "X-API-Key: your-api-key"
```

### Search Repositories by Author
```bash
curl -X GET "https://api.example.com/repositories?author=facebook&limit=20" \
  -H "X-API-Key: your-api-key"
```

### Get Repository Overview
```bash
curl -X GET "https://api.example.com/repositories/123e4567-e89b-12d3-a456-426614174000/overview" \
  -H "X-API-Key: your-api-key"
```

### Get Technical Documentation Only
```bash
curl -X GET "https://api.example.com/repositories/123e4567-e89b-12d3-a456-426614174000/documents?document_type=technical_overview&current_only=true" \
  -H "X-API-Key: your-api-key"
```

### Get Repositories with Analysis and Document Counts
```bash
# Optimized bulk query - fetches analysis + document counts for 5 repositories in 3 total database calls
curl -X GET "https://api.example.com/repositories?include_analysis=true&limit=5" \
  -H "X-API-Key: your-api-key"
```

### Get Single Repository with Complete Analysis Data
```bash
curl -X GET "https://api.example.com/repositories/123e4567-e89b-12d3-a456-426614174000?include_analysis=true" \
  -H "X-API-Key: your-api-key"
```