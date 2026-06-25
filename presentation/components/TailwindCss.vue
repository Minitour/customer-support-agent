<script setup lang="ts">
import TechIcon from './TechIcon.vue'
defineProps<{ size?: number; variant?: string }>()
</script>
<template>
  <TechIcon name="tailwind" :size="size" :variant="(variant as any)" />
</template>
