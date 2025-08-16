<script setup>
const apiUrl = 'http://localhost:8000/healthz'
async function ping() {
  const res = await fetch(apiUrl)
  const json = await res.json()
  alert(JSON.stringify(json))
}
</script>

<template>
  <main style="font: 16px/1.4 system-ui, sans-serif; padding: 32px;">
    <h1>EMS Frontend</h1>
    <p>If backend is running, this button should show its health JSON.</p>
    <button @click="ping">Ping API</button>
  </main>
</template>
