import { describe, expect, it } from 'vitest'

import {
  canonicalizeConfigForManagerSave,
  projectCanonicalConfigForManager,
} from './configPageCanonicalization'
import { buildProviderModelPayload, normalizeModelBackendRefs } from './configPageModelFormSupport'
import type { ConfigData } from './configPageSupport'

describe('model backend metrics settings', () => {
  it.each([
    { metrics_port: 9100, metrics_path: '/private-metrics' },
    { metrics_port: 9100 },
    { metrics_path: '/private-metrics' },
    {},
  ])('preserves optional metrics settings through edit/save: %j', (metrics) => {
    const backendRef = {
      name: 'triton-primary',
      backend_id: 'triton-a',
      engine_kind: 'tensorrt-llm',
      endpoint: 'triton:8000',
      protocol: 'http' as const,
      weight: 1,
      ...metrics,
    }
    const original: ConfigData = {
      version: 'v0.3',
      providers: { models: [{ name: 'llama', backend_refs: [backendRef] }] },
      routing: { modelCards: [{ name: 'llama' }], decisions: [], signals: {} },
    }
    const projected = projectCanonicalConfigForManager(original)
    const model = projected.providers!.models[0]
    projected.providers!.models[0] = buildProviderModelPayload(model.name, {
      ...model,
      provider_model_id: 'physical/llama-v2',
      backend_refs: normalizeModelBackendRefs(model.backend_refs),
    }, model)

    const saved = canonicalizeConfigForManagerSave(projected)
    expect(saved.providers!.models[0].provider_model_id).toBe('physical/llama-v2')
    expect(saved.providers!.models[0].backend_refs).toEqual([backendRef])
    expect(projectCanonicalConfigForManager(saved).providers!.models[0].backend_refs).toEqual([backendRef])
    expect(original.providers!.models[0].backend_refs).toEqual([backendRef])
  })

  it('normalizes only finite numeric ports and nonempty paths', () => {
    expect(normalizeModelBackendRefs([
      { metrics_port: 9100, metrics_path: ' /private-metrics ' },
      { metrics_port: Number.NaN, metrics_path: ' ' },
      { metrics_port: Number.POSITIVE_INFINITY, metrics_path: 123 },
      { metrics_port: '9100' },
    ])).toEqual([{ metrics_port: 9100, metrics_path: '/private-metrics' }, {}, {}, {}])
  })
})
