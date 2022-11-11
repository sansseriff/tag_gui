import { writable } from 'svelte/store'

export const colorModeStore = writable({ color: "light" })