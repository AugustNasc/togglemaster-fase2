package main

import "fmt"

// --- Estruturas de Dados ---

// Flag espelha a resposta do flag-service
type Flag struct {
	ID          int    `json:"id"`
	Name        string `json:"name"`
	Description string `json:"description"`
	IsEnabled   bool   `json:"is_enabled"`
}

// TargetingRule espelha a resposta do targeting-service
type TargetingRule struct {
	ID         int    `json:"id"`
	FlagName   string `json:"flag_name"`
	IsEnabled  bool   `json:"is_enabled"`
	Rules      Rule   `json:"rules"` // O objeto JSONB
}

// Rule � o objeto JSONB aninhado
type Rule struct {
	Type  string      `json:"type"`  // ex: "PERCENTAGE"
	Value interface{} `json:"value"` // ex: 50
}

// CombinedFlagInfo � a estrutura que salvamos no cache
type CombinedFlagInfo struct {
	Flag *Flag
	Rule *TargetingRule
}

// NotFoundError � um erro customizado
type NotFoundError struct {
	FlagName string
}
func (e *NotFoundError) Error() string {
	return fmt.Sprintf("flag ou regra '%s' n�o encontrada", e.FlagName)
}