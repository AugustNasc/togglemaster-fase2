CREATE USER flags_user WITH PASSWORD 'flags_local';
CREATE DATABASE flags_db OWNER flags_user;
CREATE USER targeting_user WITH PASSWORD 'targeting_local';
CREATE DATABASE targeting_db OWNER targeting_user;
\connect flags_db
SET ROLE flags_user;
CREATE TABLE IF NOT EXISTS flags (
    id SERIAL PRIMARY KEY,

    -- 'name' � a chave de neg�cio �nica (ex: 'enable-new-checkout')
    name VARCHAR(100) UNIQUE NOT NULL, 
    
    description TEXT,
    
    -- Este � o 'kill switch' global. Se for false, a flag est� desativada para todos.
    is_enabled BOOLEAN NOT NULL DEFAULT false,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Opcional, mas boa pr�tica: Trigger para atualizar 'updated_at' automaticamente
CREATE OR REPLACE FUNCTION trigger_set_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Remove o trigger se j� existir, para evitar erro na recria��o
DROP TRIGGER IF EXISTS set_timestamp ON flags;

CREATE TRIGGER set_timestamp
BEFORE UPDATE ON flags
FOR EACH ROW
EXECUTE PROCEDURE trigger_set_timestamp();
RESET ROLE;
\connect targeting_db
SET ROLE targeting_user;
CREATE TABLE IF NOT EXISTS targeting_rules (
    id SERIAL PRIMARY KEY,

    -- 'flag_name' � a chave de neg�cio �nica. 
    -- Cada flag pode ter no m�ximo UMA regra de segmenta��o.
    flag_name VARCHAR(100) UNIQUE NOT NULL,
    
    -- Se a regra de segmenta��o em si est� ativa ou n�o
    is_enabled BOOLEAN NOT NULL DEFAULT true,
    
    -- Armazena a l�gica da regra como um JSON.
    -- Ex: {"type": "PERCENTAGE", "value": 50}
    -- Ex: {"type": "USER_LIST", "values": ["u1", "u2"]}
    rules JSONB NOT NULL,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Trigger para atualizar 'updated_at' automaticamente (igual ao do flag-service)
CREATE OR REPLACE FUNCTION trigger_set_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS set_timestamp ON targeting_rules;

CREATE TRIGGER set_timestamp
BEFORE UPDATE ON targeting_rules
FOR EACH ROW
EXECUTE PROCEDURE trigger_set_timestamp();

