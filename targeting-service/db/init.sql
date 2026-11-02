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