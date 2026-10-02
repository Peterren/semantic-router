package tensorrtllm

import (
	"context"
	"net/http"
	"net/http/httptest"
	"sync/atomic"
	"testing"

	"github.com/vllm-project/semantic-router/src/semantic-router/pkg/backend"
)

func TestCollectPartialCountersAcrossScrapes(t *testing.T) {
	steps := []struct {
		present int
		request float64
		queue   float64
		count   float64
		e2e     *float64
		queued  *float64
	}{
		{requestCountPresent, 0, 0, 10, nil, nil},
		{requestCountPresent, 0, 0, 20, nil, nil},
		{requestDurationPresent | requestCountPresent, 3000000, 0, 30, nil, nil},
		{allCountersPresent, 5000000, 1000000, 40, floatPtr(0.2), nil},
		{allCountersPresent, 7000000, 1500000, 50, floatPtr(0.2), floatPtr(0.05)},
		{queueDurationPresent | requestCountPresent, 0, 2000000, 60, nil, floatPtr(0.05)},
		{allCountersPresent, 9000000, 2500000, 70, nil, floatPtr(0.05)},
		{allCountersPresent, 11000000, 3000000, 80, floatPtr(0.2), floatPtr(0.05)},
	}
	var scrape atomic.Int32
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path != "/private-metrics" {
			http.NotFound(w, r)
			return
		}
		index := int(scrape.Add(1)) - 1
		if index >= len(steps) {
			http.Error(w, "unexpected scrape", http.StatusInternalServerError)
			return
		}
		step := steps[index]
		_, _ = w.Write([]byte(counterMetrics(step.present, step.request, step.queue, step.count)))
	}))
	defer srv.Close()
	target := testTarget()
	target.MetricsEndpoint = srv.URL + "/private-metrics"
	adapter, err := NewAdapter(backend.AdapterConfig{Targets: []backend.AdapterTarget{target}})
	if err != nil {
		t.Fatalf("NewAdapter: %v", err)
	}
	for index, step := range steps {
		samples, err := adapter.Collect(context.Background())
		if err != nil || len(samples) != 1 {
			t.Fatalf("scrape %d: got %d samples, error %v", index, len(samples), err)
		}
		for _, latency := range []struct {
			name string
			got  *float64
			want *float64
		}{
			{"E2E", samples[0].Latency.E2ESeconds.P50Seconds, step.e2e},
			{"queue", samples[0].Latency.QueueSeconds.P50Seconds, step.queued},
		} {
			if latency.want != nil {
				wantFloatPtr(t, latency.name, latency.got, *latency.want)
			} else if latency.got != nil {
				t.Errorf("scrape %d %s = %v, want absent latency", index, latency.name, *latency.got)
			}
		}
	}
}

func floatPtr(value float64) *float64 { return &value }
