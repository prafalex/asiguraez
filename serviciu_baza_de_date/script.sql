CREATE TABLE Users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
);

alter table users add column "role" varchar(50);
ALTER TABLE asiguraez.users ADD is_active boolean DEFAULT True;


CREATE TABLE Insured (
    insured_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES Users(user_id) UNIQUE,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    date_of_birth DATE NOT NULL,
    gender VARCHAR(10) NOT NULL, -- e.g., Male, Female, Other
    occupation VARCHAR(100),
    marital_status VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE Policies (
    policy_id SERIAL PRIMARY KEY,
    policy_name VARCHAR(255) NOT NULL,
    description TEXT,
    coverage_amount NUMERIC(15, 2) NOT NULL,
    premium_amount NUMERIC(15, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE PolicyTypes (
    type_id SERIAL PRIMARY KEY,
    type_name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE Claims (
    claim_id SERIAL PRIMARY KEY,
    policy_id INT REFERENCES Policies(policy_id),
    claim_date DATE NOT NULL,
    claim_amount NUMERIC(15, 2) NOT NULL,
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Payments (
    payment_id SERIAL PRIMARY KEY,
    policy_id INT REFERENCES Policies(policy_id),
    payment_date DATE NOT NULL,
    amount NUMERIC(15, 2) NOT NULL,
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Beneficiaries (
    beneficiary_id SERIAL PRIMARY KEY,
    policy_id INT REFERENCES Policies(policy_id),
    beneficiary_name VARCHAR(100) NOT NULL,
    relationship VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Addresses (
	address_id SERIAL PRIMARY KEY,
	insured_id INT REFERENCES Insured(insured_id),
	address_type varchar(50) NOT NULL,
	street_address varchar(255) NOT NULL,
	city varchar(100) NOT NULL,
	state varchar(100) NOT NULL,
	zip_code varchar(20) NOT NULL,
	created_at timestamp NULL DEFAULT CURRENT_TIMESTAMP,

);

CREATE TABLE Contacts (
    contact_id SERIAL PRIMARY KEY,
    insured_id INT REFERENCES Insured(insured_id),
    contact_name VARCHAR(100) NOT NULL,
    relationship VARCHAR(100) NOT NULL,
    phone_number VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE CoverageTypes (
    coverage_id SERIAL PRIMARY KEY,
    coverage_name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE Documents (
    document_id SERIAL PRIMARY KEY,
    policy_id INT REFERENCES Policies(policy_id),
    document_type VARCHAR(100) NOT NULL,
    file_path TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE PremiumRates (
    rate_id SERIAL PRIMARY KEY,
    policy_id INT REFERENCES Policies(policy_id),
    coverage_id INT REFERENCES CoverageTypes(coverage_id),
    age_range VARCHAR(50) NOT NULL, 
    rate_amount NUMERIC(15, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Log (
    log_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES Users(user_id),
    activity_type VARCHAR(100) NOT NULL,
    activity_description TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE SupportTickets (
    ticket_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES Users(user_id),
    subject VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    status VARCHAR(50) NOT NULL,
    priority VARCHAR(50),
    assigned_to INT REFERENCES Users(user_id),
    resolution TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE Policies
ADD COLUMN policy_type_id INT REFERENCES PolicyTypes(type_id);


ALTER TABLE Policies
ADD COLUMN insured_id INT REFERENCES Insured(insured_id);

alter table policies add constraint policy_name_key unique(policy_name);

ALTER TABLE asiguraez.policies ALTER COLUMN policy_type_id SET NOT NULL;
ALTER TABLE asiguraez.policies ALTER COLUMN insured_id SET NOT NULL;

ALTER TABLE Policies
ADD COLUMN duration INT NOT NULL DEFAULT 0;

CREATE TABLE InsuranceRequests (
    request_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES Users(user_id),
    policy_type_id INT REFERENCES PolicyTypes(type_id),
    coverage_amount NUMERIC(15, 2) NOT NULL,
    additional_information TEXT,
    request_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) NOT NULL, 
    policy_id INT REFERENCES Policies(policy_id) 
);

CREATE TABLE InsuranceProposals (
    proposal_id SERIAL PRIMARY KEY,
    employee_id INT REFERENCES Users(user_id),
    insured_id INT REFERENCES Insured(insured_id),
    policy_type_id INT REFERENCES PolicyTypes(type_id),
    coverage_amount NUMERIC(15, 2) NOT NULL,
    premium_amount NUMERIC(15, 2) NOT NULL,
    additional_information TEXT,
    proposal_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) NOT NULL, 
    policy_id INT REFERENCES Policies(policy_id) 
);


CREATE INDEX idx_users_email ON Users (email);
CREATE INDEX idx_users_username ON Users (username);

CREATE INDEX idx_insured_user_id ON Insured (user_id);
CREATE INDEX idx_insured_last_name ON Insured (last_name);

CREATE INDEX idx_policies_policy_name ON Policies (policy_name);
CREATE INDEX idx_policies_policy_type_id ON Policies (policy_type_id);

CREATE INDEX idx_policy_types_type_name ON PolicyTypes (type_name);

CREATE INDEX idx_claims_policy_id ON Claims (policy_id);

CREATE INDEX idx_payments_policy_id ON Payments (policy_id);

CREATE INDEX idx_beneficiaries_policy_id ON Beneficiaries (policy_id);

CREATE INDEX idx_addresses_insured_id ON Addresses (insured_id);

CREATE INDEX idx_contacts_insured_id ON Contacts (insured_id);

CREATE INDEX idx_coverage_types_coverage_name ON CoverageTypes (coverage_name);

CREATE INDEX idx_documents_policy_id ON Documents (policy_id);

CREATE INDEX idx_premium_rates_policy_id ON PremiumRates (policy_id);

CREATE INDEX idx_log_user_id ON Log (user_id);

CREATE INDEX idx_support_tickets_user_id ON SupportTickets (user_id);

CREATE INDEX idx_insurance_requests_user_id ON InsuranceRequests (user_id);

CREATE INDEX idx_insurance_proposals_insured_id ON InsuranceProposals (insured_id);



CREATE OR REPLACE FUNCTION log_database_operation()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO Log (user_id, activity_type, activity_description)
    VALUES (0, TG_OP, current_query());
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER log_users_trigger
AFTER INSERT OR UPDATE OR DELETE ON Users
FOR EACH STATEMENT
EXECUTE FUNCTION log_database_operation();

CREATE TRIGGER log_insured_trigger
AFTER INSERT OR UPDATE OR DELETE ON Insured
FOR EACH STATEMENT
EXECUTE FUNCTION log_database_operation();

CREATE TRIGGER log_policies_trigger
AFTER INSERT OR UPDATE OR DELETE ON Policies
FOR EACH STATEMENT
EXECUTE FUNCTION log_database_operation();

CREATE TRIGGER log_policytypes_trigger
AFTER INSERT OR UPDATE OR DELETE ON PolicyTypes
FOR EACH STATEMENT
EXECUTE FUNCTION log_database_operation();

CREATE TRIGGER log_claims_trigger
AFTER INSERT OR UPDATE OR DELETE ON Claims
FOR EACH STATEMENT
EXECUTE FUNCTION log_database_operation();

CREATE TRIGGER log_payments_trigger
AFTER INSERT OR UPDATE OR DELETE ON Payments
FOR EACH STATEMENT
EXECUTE FUNCTION log_database_operation();

CREATE TRIGGER log_beneficiaries_trigger
AFTER INSERT OR UPDATE OR DELETE ON Beneficiaries
FOR EACH STATEMENT
EXECUTE FUNCTION log_database_operation();

CREATE TRIGGER log_addresses_trigger
AFTER INSERT OR UPDATE OR DELETE ON Addresses
FOR EACH STATEMENT
EXECUTE FUNCTION log_database_operation();

CREATE TRIGGER log_contacts_trigger
AFTER INSERT OR UPDATE OR DELETE ON Contacts
FOR EACH STATEMENT
EXECUTE FUNCTION log_database_operation();

CREATE TRIGGER log_coveragetypes_trigger
AFTER INSERT OR UPDATE OR DELETE ON CoverageTypes
FOR EACH STATEMENT
EXECUTE FUNCTION log_database_operation();

CREATE TRIGGER log_documents_trigger
AFTER INSERT OR UPDATE OR DELETE ON Documents
FOR EACH STATEMENT
EXECUTE FUNCTION log_database_operation();

CREATE TRIGGER log_premiumrates_trigger
AFTER INSERT OR UPDATE OR DELETE ON PremiumRates
FOR EACH STATEMENT
EXECUTE FUNCTION log_database_operation();

CREATE TRIGGER log_supporttickets_trigger
AFTER INSERT OR UPDATE OR DELETE ON SupportTickets
FOR EACH STATEMENT
EXECUTE FUNCTION log_database_operation();

CREATE TRIGGER log_insurancerequests_trigger
AFTER INSERT OR UPDATE OR DELETE ON InsuranceRequests
FOR EACH STATEMENT
EXECUTE FUNCTION log_database_operation();

CREATE TRIGGER log_insuranceproposals_trigger
AFTER INSERT OR UPDATE OR DELETE ON InsuranceProposals
FOR EACH STATEMENT
EXECUTE FUNCTION log_database_operation();


-- adding updated_at column to main tables
ALTER TABLE Users ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE Insured ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE Policies ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE Addresses ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE Payments ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON Users
FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_insured_updated_at BEFORE UPDATE ON Insured
FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_policies_updated_at BEFORE UPDATE ON Policies
FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_addresses_updated_at BEFORE UPDATE ON Addresses
FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_payments_updated_at BEFORE UPDATE ON Payments
FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_support_tickets_updated_at BEFORE UPDATE ON SupportTickets
FOR EACH ROW EXECUTE FUNCTION update_updated_at();