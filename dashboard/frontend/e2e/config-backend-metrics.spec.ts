import { expect, test, type Page } from '@playwright/test'

import { mockAuthenticatedAppShell } from './support/auth'

const backendRef = {
  name: 'triton-primary',
  backend_id: 'triton-a',
  engine_kind: 'tensorrt-llm',
  endpoint: 'triton:8000',
  protocol: 'http',
  weight: 1,
  metrics_port: 9100,
  metrics_path: '/private-metrics',
}

function buildConfig() {
  return {
    version: 'v0.3',
    listeners: [{ name: 'public', address: '0.0.0.0', port: 8801 }],
    providers: {
      defaults: { default_model: 'llama' },
      models: [{ name: 'llama', provider_model_id: 'physical/llama', backend_refs: [backendRef] }],
    },
    routing: { modelCards: [{ name: 'llama' }], decisions: [], signals: {} },
    global: {},
    plugins: {},
  }
}

async function mockTritonConfig(page: Page) {
  // Never send fixture test traffic to a locally running router.
  await page.route('**/api/**', (route) => route.fulfill({ status: 404, json: {} }))
  await mockAuthenticatedAppShell(page)
  let config = buildConfig()
  const writes: ReturnType<typeof buildConfig>[] = []
  await page.route('**/api/router/config/all', (route) => route.fulfill({ json: config }))
  await page.route('**/api/router/config/global', (route) => route.fulfill({ json: config.global }))
  await page.route('**/api/router/config/update', async (route) => {
    config = route.request().postDataJSON() as ReturnType<typeof buildConfig>
    writes.push(config)
    await route.fulfill({ json: { success: true } })
  })
  await page.route('**/api/status', (route) => route.fulfill({
    json: {
      overall: 'healthy',
      deployment_type: 'local',
      services: [{ name: 'router', status: 'running', healthy: true }],
      models: { models: [], summary: { loaded_models: 0, total_models: 0 } },
    },
  }))
  return writes
}

test('model edit/save preserves custom Triton metrics and allows updating them', async ({ page }) => {
  const writes = await mockTritonConfig(page)
  await page.goto('/config/models')
  await page.getByRole('button', { name: 'Edit llama', exact: true }).click()
  const dialog = page.getByRole('dialog', { name: 'Edit Model: llama' })
  await dialog.getByRole('region', { name: 'triton-primary' }).getByRole('button', { name: 'Edit', exact: true }).click()
  await expect(dialog.getByLabel('Metrics port', { exact: true })).toHaveValue('9100')
  await expect(dialog.getByLabel('Metrics path', { exact: true })).toHaveValue('/private-metrics')
  await dialog.getByLabel('Provider Model ID').fill('physical/llama-v2')
  await dialog.getByRole('button', { name: 'Save', exact: true }).click()
  await expect(dialog).toBeHidden()
  await expect.poll(() => writes.length).toBe(1)
  expect(writes[0].providers.models[0]).toMatchObject({
    provider_model_id: 'physical/llama-v2',
    backend_refs: [backendRef],
  })

  await page.reload()
  await page.getByRole('button', { name: 'Edit llama', exact: true }).click()
  await dialog.getByRole('region', { name: 'triton-primary' }).getByRole('button', { name: 'Edit', exact: true }).click()
  await expect(dialog.getByLabel('Metrics port', { exact: true })).toHaveValue('9100')
  await expect(dialog.getByLabel('Metrics path', { exact: true })).toHaveValue('/private-metrics')
  await dialog.getByLabel('Metrics port', { exact: true }).fill('9200')
  await dialog.getByLabel('Metrics path', { exact: true }).fill('/another-metrics')
  await dialog.getByRole('button', { name: 'Save', exact: true }).click()
  await expect(dialog).toBeHidden()
  await expect.poll(() => writes.length).toBe(2)
  expect(writes[1].providers.models[0].backend_refs).toEqual([
    { ...backendRef, metrics_port: 9200, metrics_path: '/another-metrics' },
  ])
})

test('clearing optional metrics settings does not reinsert a default into saved config', async ({ page }) => {
  const writes = await mockTritonConfig(page)
  await page.goto('/config/models')
  await page.getByRole('button', { name: 'Edit llama', exact: true }).click()
  const dialog = page.getByRole('dialog', { name: 'Edit Model: llama' })
  await dialog.getByRole('region', { name: 'triton-primary' }).getByRole('button', { name: 'Edit', exact: true }).click()
  await dialog.getByLabel('Metrics port', { exact: true }).fill('')
  await dialog.getByLabel('Metrics path', { exact: true }).fill('')
  await dialog.getByRole('button', { name: 'Save', exact: true }).click()
  await expect(dialog).toBeHidden()
  await expect.poll(() => writes.length).toBe(1)
  const savedRef = writes[0].providers.models[0].backend_refs[0]
  expect(savedRef).not.toHaveProperty('metrics_port')
  expect(savedRef).not.toHaveProperty('metrics_path')
  expect(savedRef.endpoint).toBe('triton:8000')
})
