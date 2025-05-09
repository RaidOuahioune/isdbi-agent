-- Main Standards Collection
CREATE TABLE standards (
    standard_id VARCHAR(50) PRIMARY KEY,  -- e.g., "FAS_4", "FAS_7"
    standard_name VARCHAR(255) NOT NULL,  -- e.g., "Murabaha and Other Deferred Payment Sales"
    version VARCHAR(50) NOT NULL,         -- e.g., "2019"
    effective_date DATE NOT NULL,
    supersedes VARCHAR(50),               -- references previous version if any
    summary TEXT NOT NULL,
    scope TEXT NOT NULL,
    embedding VECTOR(1536) NOT NULL,      -- full document embedding
    metadata JSONB                        -- additional metadata
);

-- Standard Sections Collection
CREATE TABLE standard_sections (
    section_id VARCHAR(100) PRIMARY KEY,
    standard_id VARCHAR(50) REFERENCES standards(standard_id),
    section_number VARCHAR(50) NOT NULL,  -- e.g., "4.1", "4.1.1"
    section_title VARCHAR(255) NOT NULL,
    section_text TEXT NOT NULL,
    embedding VECTOR(1536) NOT NULL,      -- section-level embedding
    importance_score FLOAT NOT NULL,      -- calculated importance in standard context
    INDEX idx_section_embedding USING HNSW (embedding vector_cosine_ops)
);

-- Accounting Rules Collection
CREATE TABLE accounting_rules (
    rule_id VARCHAR(100) PRIMARY KEY,
    standard_id VARCHAR(50) REFERENCES standards(standard_id),
    section_id VARCHAR(100) REFERENCES standard_sections(section_id),
    rule_type VARCHAR(50) NOT NULL,       -- e.g., "Recognition", "Measurement", "Disclosure"
    rule_text TEXT NOT NULL,
    examples JSONB,                        -- array of example applications
    embedding VECTOR(1536) NOT NULL,
    INDEX idx_rule_embedding USING HNSW (embedding vector_cosine_ops)
);

-- Financial Products Collection
CREATE TABLE financial_products (
    product_id VARCHAR(100) PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,   -- e.g., "Murabaha", "Ijarah", "Musharakah"
    product_category VARCHAR(100) NOT NULL,
    product_description TEXT NOT NULL,
    applicable_standards JSONB NOT NULL,  -- array of applicable standard_ids
    shariah_principles JSONB NOT NULL,    -- array of applicable principles
    embedding VECTOR(1536) NOT NULL,
    INDEX idx_product_embedding USING HNSW (embedding vector_cosine_ops)
);

-- Use Cases Collection
CREATE TABLE use_cases (
    use_case_id VARCHAR(100) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    scenario TEXT NOT NULL,
    financial_product_id VARCHAR(100) REFERENCES financial_products(product_id),
    applicable_standards JSONB NOT NULL,  -- array of applicable standard_ids
    accounting_entries JSONB NOT NULL,    -- structured journal entries
    reasoning TEXT NOT NULL,
    embedding VECTOR(1536) NOT NULL,
    INDEX idx_use_case_embedding USING HNSW (embedding vector_cosine_ops)
);

-- Shariah Principles Collection
CREATE TABLE shariah_principles (
    principle_id VARCHAR(100) PRIMARY KEY,
    principle_name VARCHAR(255) NOT NULL, -- e.g., "Riba prohibition", "Gharar prohibition"
    principle_description TEXT NOT NULL,
    related_standards JSONB NOT NULL,     -- array of related standard_ids
    embedding VECTOR(1536) NOT NULL,
    INDEX idx_principle_embedding USING HNSW (embedding vector_cosine_ops)
);

-- Jurisdictional Variations Collection
CREATE TABLE jurisdictional_variations (
    variation_id VARCHAR(100) PRIMARY KEY,
    standard_id VARCHAR(50) REFERENCES standards(standard_id),
    jurisdiction VARCHAR(100) NOT NULL,   -- e.g., "Malaysia", "Bahrain", "UAE"
    regulatory_body VARCHAR(255) NOT NULL,
    variation_details TEXT NOT NULL,
    effective_date DATE NOT NULL,
    embedding VECTOR(1536) NOT NULL,
    INDEX idx_variation_embedding USING HNSW (embedding vector_cosine_ops)
);

-- Standard Relationships Collection
CREATE TABLE standard_relationships (
    relationship_id VARCHAR(100) PRIMARY KEY,
    from_standard_id VARCHAR(50) REFERENCES standards(standard_id),
    to_standard_id VARCHAR(50) REFERENCES standards(standard_id),
    relationship_type VARCHAR(50) NOT NULL, -- e.g., "references", "supersedes", "complements"
    description TEXT NOT NULL,
    embedding VECTOR(1536) NOT NULL,
    INDEX idx_relationship_embedding USING HNSW (embedding vector_cosine_ops)
);

-- Proposed Enhancements Collection
CREATE TABLE proposed_enhancements (
    enhancement_id VARCHAR(100) PRIMARY KEY,
    standard_id VARCHAR(50) REFERENCES standards(standard_id),
    section_id VARCHAR(100) REFERENCES standard_sections(section_id),
    enhancement_type VARCHAR(50) NOT NULL, -- e.g., "Clarification", "Addition", "Modification"
    current_text TEXT NOT NULL,
    proposed_text TEXT NOT NULL,
    justification TEXT NOT NULL,
    shariah_compliance_analysis TEXT NOT NULL,
    proposing_agent VARCHAR(100) NOT NULL,
    validation_status VARCHAR(50) NOT NULL, -- e.g., "Pending", "Approved", "Rejected"
    validation_comments TEXT,
    embedding VECTOR(1536) NOT NULL,
    INDEX idx_enhancement_embedding USING HNSW (embedding vector_cosine_ops)
);

-- Agent Actions Log
CREATE TABLE agent_actions (
    action_id VARCHAR(100) PRIMARY KEY,
    agent_id VARCHAR(100) NOT NULL,
    action_type VARCHAR(50) NOT NULL,
    action_timestamp TIMESTAMP NOT NULL,
    query_text TEXT NOT NULL,
    response_text TEXT NOT NULL,
    standards_referenced JSONB,           -- array of referenced standard_ids
    reasoning TEXT NOT NULL,
    confidence_score FLOAT NOT NULL,
    embedding VECTOR(1536) NOT NULL,
    INDEX idx_action_embedding USING HNSW (embedding vector_cosine_ops)
);