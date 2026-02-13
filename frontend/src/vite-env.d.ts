/// <reference types="svelte" />
/// <reference types="vite/client" />

declare module '*.svg' {
	import type { SvelteComponentDev } from 'svelte/internal';
	const content: SvelteComponentDev;
	export default content;
}

interface ImportMetaEnv {
	readonly VITE_API_URL: string;
}

interface ImportMeta {
	readonly env: ImportMetaEnv;
}
