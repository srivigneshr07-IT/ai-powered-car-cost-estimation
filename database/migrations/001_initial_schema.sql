-- ============================================================================
-- AI-Powered Dynamic Used Car Valuation System
-- PostgreSQL Database Schema
-- Version: 1.0
-- ============================================================================

-- Table 1: market_prices (Raw Scraped Listings)
-- ============================================================================
CREATE TABLE IF NOT EXISTS market_prices (
    id SERIAL PRIMARY KEY,
    
    -- Source Information
    source VARCHAR(50) NOT NULL,
    listing_id VARCHAR(100),
    listing_url TEXT,
    
    -- Vehicle Details (Normalized)
    brand VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL,
    variant VARCHAR(200),
    year INTEGER NOT NULL,
    
    -- Specifications
    fuel VARCHAR(50),
    transmission VARCHAR(50),
    body_type VARCHAR(50),
    owner_type VARCHAR(50),
    
    -- Pricing & Condition
    price INTEGER NOT NULL,
    kilometers INTEGER,
    
    -- Location
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100),
    
    -- Metadata
    scraped_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Deduplication
    listing_hash VARCHAR(64) UNIQUE
);

-- Indexes for market_prices
CREATE INDEX idx_mp_source ON market_prices(source);
CREATE INDEX idx_mp_brand ON market_prices(brand);
CREATE INDEX idx_mp_model ON market_prices(model);
CREATE INDEX idx_mp_year ON market_prices(year);
CREATE INDEX idx_mp_city ON market_prices(city);
CREATE INDEX idx_mp_price ON market_prices(price);
CREATE INDEX idx_mp_scraped_at ON market_prices(scraped_at);
CREATE INDEX idx_mp_is_active ON market_prices(is_active);
CREATE INDEX idx_mp_listing_hash ON market_prices(listing_hash);
CREATE INDEX idx_mp_brand_model_year_city ON market_prices(brand, model, year, city);
CREATE INDEX idx_mp_brand_model_city ON market_prices(brand, model, city);
CREATE INDEX idx_mp_price_year ON market_prices(price, year);


-- Table 2: market_statistics (Aggregated Intelligence)
-- ============================================================================
CREATE TABLE IF NOT EXISTS market_statistics (
    id SERIAL PRIMARY KEY,
    
    -- Grouping Dimensions
    brand VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL,
    year INTEGER,
    city VARCHAR(100),
    fuel VARCHAR(50),
    transmission VARCHAR(50),
    
    -- Statistical Metrics
    avg_price INTEGER,
    median_price INTEGER,
    min_price INTEGER,
    max_price INTEGER,
    std_dev FLOAT,
    
    -- Sample Information
    listing_count INTEGER,
    
    -- Temporal Metadata
    calculated_at TIMESTAMP DEFAULT NOW(),
    data_start_date TIMESTAMP,
    data_end_date TIMESTAMP,
    
    -- Composite unique constraint
    CONSTRAINT uq_market_stats UNIQUE (brand, model, year, city, fuel, transmission)
);

-- Indexes for market_statistics
CREATE INDEX idx_ms_brand ON market_statistics(brand);
CREATE INDEX idx_ms_model ON market_statistics(model);
CREATE INDEX idx_ms_year ON market_statistics(year);
CREATE INDEX idx_ms_city ON market_statistics(city);
CREATE INDEX idx_ms_calculated_at ON market_statistics(calculated_at);
CREATE INDEX idx_ms_stats_lookup ON market_statistics(brand, model, year, city);


-- Table 3: prediction_logs (Audit Trail)
-- ============================================================================
CREATE TABLE IF NOT EXISTS prediction_logs (
    id SERIAL PRIMARY KEY,
    
    -- Input Features
    brand VARCHAR(100),
    model VARCHAR(100),
    variant VARCHAR(200),
    year INTEGER,
    kilometers INTEGER,
    fuel VARCHAR(50),
    transmission VARCHAR(50),
    body_type VARCHAR(50),
    owner_type VARCHAR(50),
    city VARCHAR(100),
    state VARCHAR(100),
    car_age INTEGER,
    premium_brand INTEGER,
    transaction_mode VARCHAR(50),
    
    -- Predictions
    ml_base_price INTEGER,
    market_average INTEGER,
    market_median INTEGER,
    final_price INTEGER,
    
    -- Calculation Details
    ml_weight FLOAT,
    market_avg_weight FLOAT,
    market_median_weight FLOAT,
    
    -- Metadata
    confidence_score INTEGER,
    listings_used INTEGER,
    market_data_age_hours INTEGER,
    
    -- Audit
    predicted_at TIMESTAMP DEFAULT NOW(),
    user_id VARCHAR(100),
    session_id VARCHAR(100)
);

-- Indexes for prediction_logs
CREATE INDEX idx_pl_brand_model ON prediction_logs(brand, model);
CREATE INDEX idx_pl_predicted_at ON prediction_logs(predicted_at);


-- Table 4: market_sources (Data Provenance)
-- ============================================================================
CREATE TABLE IF NOT EXISTS market_sources (
    id SERIAL PRIMARY KEY,
    source_name VARCHAR(50) UNIQUE NOT NULL,
    base_url TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    last_scraped_at TIMESTAMP,
    total_listings_scraped INTEGER DEFAULT 0,
    success_rate FLOAT,
    avg_response_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);


-- Table 5: pipeline_logs (ETL Execution History)
-- ============================================================================
CREATE TABLE IF NOT EXISTS pipeline_logs (
    id SERIAL PRIMARY KEY,
    pipeline_run_id VARCHAR(100) UNIQUE NOT NULL,
    
    -- Execution Details
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    duration_seconds INTEGER,
    status VARCHAR(50),
    
    -- Metrics
    listings_extracted INTEGER,
    listings_transformed INTEGER,
    listings_loaded INTEGER,
    duplicates_found INTEGER,
    validation_failures INTEGER,
    
    -- Error Tracking
    error_message TEXT,
    error_stacktrace TEXT,
    
    -- Metadata
    executed_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Index for pipeline_logs
CREATE INDEX idx_plg_created_at ON pipeline_logs(created_at);


-- ============================================================================
-- Initial Data: Market Sources
-- ============================================================================
INSERT INTO market_sources (source_name, base_url, is_active) VALUES
    ('cardekho', 'https://www.cardekho.com', TRUE),
    ('olx', 'https://www.olx.in', TRUE),
    ('cars24', 'https://www.cars24.com', TRUE)
ON CONFLICT (source_name) DO NOTHING;


-- ============================================================================
-- Verification Queries
-- ============================================================================
-- SELECT COUNT(*) FROM market_prices;
-- SELECT COUNT(*) FROM market_statistics;
-- SELECT COUNT(*) FROM prediction_logs;
-- SELECT * FROM market_sources;
-- SELECT * FROM pipeline_logs ORDER BY created_at DESC LIMIT 10;
