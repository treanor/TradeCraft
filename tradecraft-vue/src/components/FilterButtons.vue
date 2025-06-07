<template>
  <div class="filter-buttons-row">
    <button
      v-for="option in options"
      :key="option.value"
      :class="['filter-btn', { active: modelValue === option.value }]"
      @click="$emit('update:modelValue', option.value)"
    >
      {{ option.label }}
    </button>
  </div>
</template>

<script setup lang="ts">
import { defineProps, defineEmits } from 'vue';

const props = defineProps({
  modelValue: String,
  options: {
    type: Array as () => { label: string; value: string }[],
    required: true
  }
});
const emit = defineEmits(['update:modelValue']);
</script>

<style scoped>
.filter-buttons-row {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  background: #232b3b;
  border-radius: 12px;
  padding: 0.5rem 1rem;
  margin-bottom: 1.2rem;
  align-items: center;
  box-shadow: 0 2px 8px 0 rgba(0,0,0,0.10);
}
.filter-btn {
  background: transparent;
  color: #a3adc2;
  border: none;
  border-radius: 8px;
  padding: 0.5rem 1.2rem;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s, color 0.2s;
}
.filter-btn.active, .filter-btn:hover {
  background: #2b6cb0;
  color: #fff;
}
</style>
