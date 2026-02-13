CREATE TABLE employees (
    -- Id = Name der Spalte, UUID = Datentyp, PRIMARY KEY = Constraint, gen_random = Funktion 
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(), 

    auth_user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE, -- References - zegit auf
    -- Cascade löscht auch Child Rows

    email TEXT UNIQUE NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,

    department TEXT,
    position TEXT,
    employee_id TEXT UNIQUE, --Firmen intern, wenn nötig

    employment_status TEXT CHECK (employment_status IN ('active', 'offboarding', 'offboarded', 'archived')),
    offboarding_date TIMESTAMPTZ,
    last_working_day TIMESTAMPTZ,

    created_at TIMESTAMPTZ DEFAULT now(), --Auto Timestamp with creation
    updated_at TIMESTAMPTZ DEFAULT now(),
    
    -- Search
    search_vector tsvector GENERATED ALWAYS AS ( --coalesce: gibt ersten nicht null wert zurück
        to_tsvector('english', coalesce(first_name, '') || ' ' || coalesce(last_name, '') || ' ' || coalesce(email, ''))
    ) STORED
);

-- Indizes
CREATE INDEX idx_employees_auth_user ON employees(auth_user_id); -- wie kapitel im buch idx_{table}_{column}
CREATE INDEX idx_employees_status ON employees(employment_status);
CREATE INDEX idx_employees_search ON employees USING gin(search_vector); -- alle rows die es enthalte

