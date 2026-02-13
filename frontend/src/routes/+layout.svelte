<script lang="ts">
	import '../app.css';
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { user } from '$lib/stores/auth';
	import { checkAuth } from '$lib/services/auth';
	import Navigation from '$lib/components/Navigation.svelte';
	import ToastContainer from '$lib/components/ToastContainer.svelte';

	onMount(() => {
		checkAuth();
	});
</script>

<Navigation />

<main class="min-h-screen">
	<slot />
</main>

<ToastContainer />

<style>
	main {
		padding-top: 4rem; /* Account for fixed navigation */
	}
</style>
