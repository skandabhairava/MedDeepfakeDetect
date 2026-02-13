<script lang="ts">
	import '../app.css';
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { user, isAuthenticated } from '$lib/stores/auth';
	import { checkAuth } from '$lib/services/auth';
	import { goto } from '$app/navigation';
	import Navigation from '$lib/components/Navigation.svelte';
	import ToastContainer from '$lib/components/ToastContainer.svelte';

	let authChecked = false;

	onMount(async () => {
		await checkAuth();
		authChecked = true;
		
		// Check if user is trying to access protected routes
		const publicRoutes = ['/', '/login'];
		const currentPath = $page.url.pathname;
		
		if (!publicRoutes.includes(currentPath) && !$isAuthenticated) {
			goto('/login');
		}
	});

	// Watch for route changes
	$: if (authChecked && !$isAuthenticated) {
		const publicRoutes = ['/', '/login'];
		const currentPath = $page.url.pathname;
		
		if (!publicRoutes.includes(currentPath)) {
			goto('/login');
		}
	}
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
