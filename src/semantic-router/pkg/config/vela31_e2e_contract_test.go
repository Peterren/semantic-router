package config

import (
	"bytes"
	"os"
	"reflect"
	"testing"

	"gopkg.in/yaml.v3"
)

func TestVela31E2EQuestionUsesCanonicalRouterFields(t *testing.T) {
	data, err := os.ReadFile("../../../../e2e/profiles/model-runtime/values.yaml")
	if err != nil {
		t.Fatal(err)
	}
	var values struct {
		Config struct {
			Recipes []struct {
				Signals struct {
					SystemOne []struct {
						Name     string    `yaml:"name"`
						Question yaml.Node `yaml:"question"`
					} `yaml:"systemone"`
				} `yaml:"signals"`
			} `yaml:"recipes"`
		} `yaml:"config"`
	}
	if err := yaml.Unmarshal(data, &values); err != nil {
		t.Fatal(err)
	}
	for _, recipe := range values.Config.Recipes {
		for _, signal := range recipe.Signals.SystemOne {
			if signal.Name != "vela31_described" {
				continue
			}
			encoded, err := yaml.Marshal(signal.Question)
			if err != nil {
				t.Fatal(err)
			}
			decoder := yaml.NewDecoder(bytes.NewReader(encoded))
			decoder.KnownFields(true)
			var question SystemOneQuestion
			if err := decoder.Decode(&question); err != nil {
				t.Fatalf("deployed Vela 3.1 question violates the Router config contract: %v", err)
			}
			want := []SystemOneOption{
				{Key: "false", Description: "can wait"},
				{Key: "true", Description: "needs immediate action"},
			}
			if question.Type != SystemOneQuestionNoul || !reflect.DeepEqual(question.Choices, want) {
				t.Fatalf("deployed Noul must retain both outcome descriptions: %+v", question)
			}
			return
		}
	}
	t.Fatal("model-runtime profile is missing vela31_described")
}
