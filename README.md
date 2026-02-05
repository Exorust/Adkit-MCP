# Ad Injector

Ad injection system with Qdrant vector storage for semantic ad matching.

## Prerequisites

- Python 3.10
- [uv](https://docs.astral.sh/uv/) - Fast Python package manager
- [Qdrant](https://qdrant.tech/) - Running locally

## Setup

### Install uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or with pip
pip install uv
```

### Start Qdrant Locally

```bash
# Using Docker
docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant

# Or download binary from https://github.com/qdrant/qdrant/releases
```

### Install Dependencies

```bash
# Install all dependencies and create virtual environment
uv sync
```

### Configure Environment (Optional)

```bash
# Copy example env file (defaults work for local Qdrant)
cp .env.example .env
```

## Running with uv

### Run Scripts

```bash
# Run main application
uv run ad-injector

# Manage Qdrant collection
uv run ad-index create          # Create the collection
uv run ad-index seed            # Add sample ads for testing
uv run ad-index info            # Show collection info
uv run ad-index delete          # Delete the collection
```

### Run Python Files Directly

```bash
uv run python -m ad_injector.cli create
uv run python -m ad_injector.cli seed
```

**Note**: The `seed` command adds 5 sample ads to the collection covering different topics (technology, education, e-commerce, fitness, and finance). This is useful for testing and demonstration purposes. Run `create` first to set up the collection, then `seed` to add test data.

### Add Dependencies

```bash
uv add <package-name>           # Add a dependency
uv add --dev <package-name>     # Add a dev dependency
```

## Ad Schema

Each ad stored in Qdrant contains:

| Field | Type | Description |
|-------|------|-------------|
| `ad_id` | string | Unique identifier for the ad |
| `advertiser_id` | string | Identifier for the advertiser |
| `title` | string | Ad headline |
| `body` | string | Ad body text |
| `cta_text` | string | Call-to-action text |
| `landing_url` | string | Redirect URL |
| `targeting.topics` | string[] | Topics to target |
| `targeting.locale` | string[] | Locale codes (e.g., "en-US") |
| `targeting.verticals` | string[] | Industry verticals |
| `targeting.blocked_keywords` | string[] | Keywords to exclude |
| `policy.sensitive` | boolean | Sensitive content flag |
| `policy.age_restricted` | boolean | Age restriction flag |

**Embedding text**: The vector embedding is generated from `title + body + topics`.

## Usage Example

```python
from ad_injector.models import Ad, AdTargeting, AdPolicy
from ad_injector.qdrant_service import create_collection, upsert_ad, query_ads

# Create the collection (once)
create_collection()

# Create an ad
ad = Ad(
    ad_id="ad-001",
    advertiser_id="adv-123",
    title="Learn Python Today",
    body="Master Python programming with our interactive courses.",
    cta_text="Start Learning",
    landing_url="https://example.com/python",
    targeting=AdTargeting(
        topics=["programming", "python", "education"],
        locale=["en-US"],
        verticals=["education", "technology"],
    ),
    policy=AdPolicy(sensitive=False, age_restricted=False),
)

# Generate embedding (using your preferred embedding model)
embedding = your_embedding_function(ad.embedding_text)

# Upsert to Qdrant
upsert_ad(ad, embedding)

# Query similar ads
query_embedding = your_embedding_function("python tutorial")
results = query_ads(query_embedding, top_k=5)
```

## Qdrant Filtering

You can filter queries using Qdrant's filter syntax:

```python
from qdrant_client.models import Filter, FieldCondition, MatchValue

# Filter by advertiser
filter_dict = Filter(
    must=[
        FieldCondition(key="advertiser_id", match=MatchValue(value="adv-123"))
    ]
)

results = query_ads(query_embedding, top_k=5, filter_dict=filter_dict)
```
