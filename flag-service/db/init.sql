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