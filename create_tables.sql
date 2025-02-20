
CREATE TABLE stocks (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10),
    price DECIMAL(10,2),
    timestamp TIMESTAMP DEFAULT NOW()
);

CREATE TABLE alerts (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    threshold DECIMAL(10,2) NOT NULL,
    direction VARCHAR(5) CHECK (direction IN ('up', 'down')),
    notified BOOLEAN DEFAULT FALSE
);
