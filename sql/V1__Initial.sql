create table clients (
    id SERIAL PRIMARY KEY,
    username VARCHAR(32) UNIQUE,
    -- might have less length but I haven't got much time to check max hash len
    -- provided by passlib.
    pwd_hash VARCHAR(256),
    balance NUMERIC(10, 2) DEFAULT 0 CHECK(balance >= 0),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX clients_username_index ON clients (username);

create table transfers (
    id SERIAL PRIMARY KEY,
    amount NUMERIC(10, 2),
    -- if from_id is NULL - then it's topup transfer from external source
    from_id INTEGER REFERENCES clients (id) NULL,
    to_id INTEGER REFERENCES clients (id) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
