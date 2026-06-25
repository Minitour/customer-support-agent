<script setup lang="ts">
import { computed } from 'vue'
import reactIcon from '@thesvg/icons/react'
import viteIcon from '@thesvg/icons/vite'
import tailwindIcon from '@thesvg/icons/tailwind-css'
import fastapiIcon from '@thesvg/icons/fastapi'
import postgresqlIcon from '@thesvg/icons/postgresql'
import sqlalchemyIcon from '@thesvg/icons/sqlalchemy'
import chromaIcon from '@thesvg/icons/chroma'
import openaiIcon from '@thesvg/icons/openai'
import langchainIcon from '@thesvg/icons/langchain'
import langgraphIcon from '@thesvg/icons/langgraph'
import ollamaIcon from '@thesvg/icons/ollama'
import qwenIcon from '@thesvg/icons/qwen'

const props = defineProps<{
  name: string
  size?: number
  variant?: 'default' | 'mono' | 'light' | 'dark' | 'wordmark'
}>()

type IconData = { svg: string; hex: string; variants?: Record<string, string> }

const iconMap: Record<string, IconData> = {
  react: reactIcon,
  vite: viteIcon,
  tailwind: tailwindIcon,
  fastapi: fastapiIcon,
  postgresql: postgresqlIcon,
  sqlalchemy: sqlalchemyIcon,
  chroma: chromaIcon,
  openai: openaiIcon,
  langchain: langchainIcon,
  langgraph: langgraphIcon,
  ollama: ollamaIcon,
  qwen: qwenIcon,
}

function luminance(hex: string): number {
  const h = hex.replace('#', '')
  const r = parseInt(h.length === 3 ? h[0] + h[0] : h.slice(0, 2), 16)
  const g = parseInt(h.length === 3 ? h[1] + h[1] : h.slice(2, 4), 16)
  const b = parseInt(h.length === 3 ? h[2] + h[2] : h.slice(4, 6), 16)
  return (0.299 * r + 0.587 * g + 0.114 * b) / 255
}

const svgContent = computed(() => {
  const icon = iconMap[props.name]
  if (!icon) return ''

  // Auto-switch to mono for icons that are too light to see on a white background
  const autoMono = luminance(icon.hex) > 0.65 && !!icon.variants?.mono
  const variant = props.variant ?? (autoMono ? 'mono' : 'default')
  const raw = (variant !== 'default' && icon.variants?.[variant]) ? icon.variants[variant] : icon.svg

  const px = props.size ?? 16
  // The source SVGs only carry a viewBox (no width/height), so strip any existing
  // dimensions and inject our own, otherwise the icon collapses to zero size.
  return raw
    .replace(/\s(?:width|height)="[^"]*"/g, '')
    .replace(/<svg\b/, `<svg width="${px}" height="${px}" style="display:inline-block;vertical-align:middle"`)
})
</script>

<template>
  <span class="inline-flex items-center justify-center shrink-0" v-html="svgContent" />
</template>
