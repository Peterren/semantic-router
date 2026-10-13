package tensorrtllm

import (
	"fmt"
	"strings"
	"testing"
	"time"
)

const (
	requestDurationPresent = 1 << iota
	queueDurationPresent
	requestCountPresent
	allCountersPresent = requestDurationPresent | queueDurationPresent | requestCountPresent
)

func counterMetrics(present int, requestDuration, queueDuration, count float64) string {
	var text strings.Builder
	for _, metric := range []struct {
		bit   int
		name  string
		value float64
	}{
		{requestDurationPresent, MetricRequestDurationUs, requestDuration},
		{queueDurationPresent, MetricQueueDurationUs, queueDuration},
		{requestCountPresent, MetricRequestSuccess, count},
	} {
		if present&metric.bit != 0 {
			fmt.Fprintf(&text, "# TYPE %s counter\n%s{model=\"tensorrt_llm\",version=\"1\"} %g\n", metric.name, metric.name, metric.value)
		}
	}
	return text.String()
}

func wantCounterLatency(t *testing.T, name string, got *float64, present bool, want float64) {
	t.Helper()
	if present {
		wantFloatPtr(t, name, got, want)
	} else if got != nil {
		t.Errorf("%s = %v, want absent latency for incomplete counter pair", name, *got)
	}
}

func TestCounterLatencyRequiresMatchingInputsInBothScrapes(t *testing.T) {
	// Exercise every presence combination, including count-only scrapes and
	// durations disappearing or reappearing between scrapes.
	for previous := 0; previous <= allCountersPresent; previous++ {
		for current := 0; current <= allCountersPresent; current++ {
			t.Run(fmt.Sprintf("previous_%03b/current_%03b", previous, current), func(t *testing.T) {
				prev := readCounters(parseFixture(t, counterMetrics(previous, 1000000, 250000, 50)))
				families := parseFixture(t, counterMetrics(current, 2000000, 500000, 100))
				sample, _, recognized := normalizeTarget(testTarget(), families, prev, 5*time.Second, time.Unix(1000, 0))
				if recognized != (current != 0) {
					t.Errorf("recognized = %v, want %v", recognized, current != 0)
				}

				observed := previous & current
				requestPair := requestDurationPresent | requestCountPresent
				queuePair := queueDurationPresent | requestCountPresent
				wantCounterLatency(t, "E2E", sample.Latency.E2ESeconds.P50Seconds, observed&requestPair == requestPair, 0.02)
				wantCounterLatency(t, "queue", sample.Latency.QueueSeconds.P50Seconds, observed&queuePair == queuePair, 0.005)
			})
		}
	}
}

func TestCounterLatencyZeroAndReset(t *testing.T) {
	for _, tc := range []struct {
		name     string
		duration float64
		count    float64
		wantZero bool
	}{
		{"observed zero duration delta", 1000000, 100, true},
		{"no new requests", 2000000, 50, false},
		{"request counter reset", 2000000, 1, false},
		{"duration counter reset", 1, 100, false},
	} {
		t.Run(tc.name, func(t *testing.T) {
			prev := readCounters(parseFixture(t, counterMetrics(allCountersPresent, 1000000, 1000000, 50)))
			families := parseFixture(t, counterMetrics(allCountersPresent, tc.duration, tc.duration, tc.count))
			sample, _, _ := normalizeTarget(testTarget(), families, prev, 5*time.Second, time.Unix(1000, 0))
			for _, latency := range []*float64{sample.Latency.E2ESeconds.P50Seconds, sample.Latency.QueueSeconds.P50Seconds} {
				if tc.wantZero {
					wantFloatPtr(t, "latency", latency, 0)
				} else if latency != nil {
					t.Errorf("latency = %v, want absent latency after reset or no requests", *latency)
				}
			}
		})
	}
}

func TestCounterLatencyPreservesSummaryQuantiles(t *testing.T) {
	prev := readCounters(parseFixture(t, counterMetrics(allCountersPresent, 1000000, 250000, 50)))
	metrics := counterMetrics(allCountersPresent, 2000000, 500000, 100) + `
# TYPE nv_inference_request_summary_us summary
nv_inference_request_summary_us{quantile="0.5"} 300000
# TYPE nv_inference_queue_summary_us summary
nv_inference_queue_summary_us{quantile="0.5"} 100000
`
	sample, _, _ := normalizeTarget(testTarget(), parseFixture(t, metrics), prev, 5*time.Second, time.Unix(1000, 0))
	wantFloatPtr(t, "E2E summary P50", sample.Latency.E2ESeconds.P50Seconds, 0.3)
	wantFloatPtr(t, "queue summary P50", sample.Latency.QueueSeconds.P50Seconds, 0.1)
}
