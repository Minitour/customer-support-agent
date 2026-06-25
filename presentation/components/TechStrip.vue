<script setup lang="ts">
import TechIcon from './TechIcon.vue'

const items: { name: string; label: string; variant?: string }[] = [
  { name: 'react', label: 'React' },
  { name: 'vite', label: 'Vite' },
  { name: 'tailwind', label: 'Tailwind' },
  { name: 'fastapi', label: 'FastAPI' },
  { name: 'sqlalchemy', label: 'SQLAlchemy' },
  { name: 'postgresql', label: 'PostgreSQL' },
  { name: 'chroma', label: 'ChromaDB' },
  { name: 'openai', label: 'OpenAI', variant: 'light' },
  { name: 'langgraph', label: 'LangGraph' },
  { name: 'ollama', label: 'Ollama' },
  { name: 'qwen', label: 'Qwen', variant: 'light' },
]
</script>

<template>
  <div class="flex items-center shrink-0" aria-hidden="true">
    <div
      v-for="item in items"
      :key="item.name"
      class="flex items-center gap-2 px-6 text-gray-500"
    >
      <TechIcon :name="item.name" :size="26" :variant="(item.variant as any)" />
      <span class="text-base font-medium whitespace-nowrap">{{ item.label }}</span>
    </div>
  </div>
</template>
