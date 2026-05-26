CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS products (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT,
    target_audience TEXT,
    selling_points TEXT,
    cautions TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY,
    title TEXT NOT NULL,
    source_type TEXT NOT NULL DEFAULT 'manual',
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS chunks (
    id UUID PRIMARY KEY,
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    product_id UUID REFERENCES products(id) ON DELETE SET NULL,
    content TEXT NOT NULL,
    chunk_index INT NOT NULL,
    embedding vector(1024) NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS chunks_embedding_idx
ON chunks USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

CREATE TABLE IF NOT EXISTS memories (
    id UUID PRIMARY KEY,
    memory_type TEXT NOT NULL,
    content TEXT NOT NULL,
    importance INT NOT NULL DEFAULT 3,
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS viral_cases (
    id UUID PRIMARY KEY,
    platform TEXT,
    product TEXT,
    title TEXT,
    url TEXT,
    author TEXT,
    content TEXT NOT NULL,
    metrics JSONB NOT NULL DEFAULT '{}',
    analysis TEXT,
    tags TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS generation_history (
    id UUID PRIMARY KEY,
    workflow TEXT NOT NULL,
    platform TEXT,
    product TEXT,
    content_module TEXT,
    goal TEXT,
    audience TEXT,
    keywords TEXT,
    input_payload JSONB NOT NULL DEFAULT '{}',
    output_content TEXT NOT NULL,
    source_summary JSONB NOT NULL DEFAULT '{}',
    status TEXT NOT NULL DEFAULT 'draft',
    converted_case_id UUID REFERENCES viral_cases(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
