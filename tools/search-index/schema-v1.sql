PRAGMA application_id = 1145787185;
PRAGMA user_version = 1;
PRAGMA foreign_keys = ON;

CREATE TABLE metadata (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    search_index_id TEXT NOT NULL UNIQUE,
    search_schema_version INTEGER NOT NULL CHECK (search_schema_version = 1),
    search_data_version INTEGER NOT NULL CHECK (search_data_version > 0),
    package_id TEXT NOT NULL,
    west REAL NOT NULL,
    south REAL NOT NULL,
    east REAL NOT NULL,
    north REAL NOT NULL,
    source_url TEXT NOT NULL,
    source_timestamp TEXT NOT NULL,
    source_sha256 TEXT NOT NULL,
    attribution TEXT NOT NULL,
    license_name TEXT NOT NULL,
    license_url TEXT NOT NULL,
    generator_version TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE admin_area (
    admin_id INTEGER PRIMARY KEY,
    parent_admin_id INTEGER REFERENCES admin_area(admin_id),
    level TEXT NOT NULL,
    name TEXT NOT NULL,
    normalized_name TEXT NOT NULL,
    source_type TEXT NOT NULL,
    source_id INTEGER NOT NULL,
    UNIQUE(source_type, source_id)
);

CREATE TABLE category (
    category_id TEXT PRIMARY KEY,
    class TEXT NOT NULL,
    subclass TEXT NOT NULL,
    display_group TEXT NOT NULL,
    display_name TEXT NOT NULL,
    icon_key TEXT NOT NULL,
    default_importance INTEGER NOT NULL CHECK (default_importance BETWEEN 0 AND 100)
);

CREATE TABLE place (
    place_id INTEGER PRIMARY KEY,
    source_type TEXT NOT NULL,
    source_id INTEGER NOT NULL,
    package_id TEXT NOT NULL,
    primary_name TEXT NOT NULL,
    normalized_primary_name TEXT NOT NULL,
    category_id TEXT NOT NULL REFERENCES category(category_id),
    subclass TEXT NOT NULL,
    latitude REAL NOT NULL CHECK (latitude BETWEEN -90.0 AND 90.0),
    longitude REAL NOT NULL CHECK (longitude BETWEEN -180.0 AND 180.0),
    importance INTEGER NOT NULL CHECK (importance BETWEEN 0 AND 100),
    admin_id INTEGER REFERENCES admin_area(admin_id),
    locality TEXT,
    spatial_bucket INTEGER NOT NULL,
    UNIQUE(source_type, source_id)
);

CREATE TABLE place_name (
    name_id INTEGER PRIMARY KEY,
    place_id INTEGER NOT NULL REFERENCES place(place_id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    normalized_name TEXT NOT NULL,
    language TEXT NOT NULL,
    name_kind TEXT NOT NULL,
    field_weight INTEGER NOT NULL CHECK (field_weight BETWEEN 0 AND 100),
    UNIQUE(place_id, name, language, name_kind)
);

CREATE TABLE search_token (
    token TEXT COLLATE BINARY NOT NULL,
    place_id INTEGER NOT NULL REFERENCES place(place_id) ON DELETE CASCADE,
    name_id INTEGER NOT NULL REFERENCES place_name(name_id) ON DELETE CASCADE,
    field_weight INTEGER NOT NULL CHECK (field_weight BETWEEN 0 AND 100),
    PRIMARY KEY(token, place_id, name_id)
) WITHOUT ROWID;

CREATE INDEX idx_search_token_token_place ON search_token(token, place_id);
CREATE INDEX idx_place_category_importance ON place(category_id, subclass, importance DESC);
CREATE INDEX idx_place_spatial ON place(spatial_bucket, latitude, longitude);
CREATE INDEX idx_place_name_exact ON place_name(normalized_name, place_id);
CREATE INDEX idx_place_name_owner ON place_name(place_id, language, name_kind);
