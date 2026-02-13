<script lang="ts">
	import { goto } from '$app/navigation';
	import { login } from '$lib/services/auth';
	import { addToast } from '$lib/stores/toast';
	import { Brain, Eye, EyeOff } from 'lucide-svelte';
	import type { LoginCredentials } from '$lib/types';
    import { isAuthenticated } from '$lib/stores/auth';

	let email = '';
	let password = '';
	let isLoading = false;
	let showPassword = false;

	// Redirect if already authenticated
	$: if ($isAuthenticated) {
		goto('/dashboard');
	}

	async function handleLogin() {
		if (!email || !password) {
			addToast({
				type: 'warning',
				title: 'Missing fields',
				message: 'Please fill in all required fields'
			});
			return;
		}

		isLoading = true;
		
		const credentials: LoginCredentials = {
			email: email.trim(),
			password
		};

		const success = await login(credentials);
		
		if (success) {
			goto('/dashboard');
		}
		
		isLoading = false;
	}

	function handleKeyPress(event: KeyboardEvent) {
		if (event.key === 'Enter') {
			handleLogin();
		}
	}
</script>

<div class="min-h-screen bg-gradient-to-br from-primary-50 to-white flex items-center justify-center px-4">
	<div class="max-w-md w-full">
		<div class="card">
			<div class="text-center mb-8">
				<div class="w-16 h-16 bg-primary-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
					<Brain class="w-10 h-10 text-white" />
				</div>
				<h2 class="text-3xl font-bold text-gray-900">Welcome Back</h2>
				<p class="text-gray-600 mt-2">Sign in to your MedScan AI account</p>
			</div>

			<!-- svelte-ignore a11y-no-noninteractive-element-interactions -->
			<form on:submit|preventDefault={handleLogin} on:keypress={handleKeyPress}>
				<div class="space-y-6">
					<div>
						<label for="email" class="label">Email Address</label>
						<input
							id="email"
							type="email"
							bind:value={email}
							placeholder="Enter your email"
							class="input"
							required
							disabled={isLoading}
						/>
					</div>

					<div>
						<label for="password" class="label">Password</label>
						<div class="relative">
							{#if showPassword}
								<input
									id="password"
									type='text'
									bind:value={password}
									placeholder="Enter your password"
									class="input pr-10"
									required
									disabled={isLoading}
								/>
							{:else}
								<input
									id="password"
									type='password'
									bind:value={password}
									placeholder="Enter your password"
									class="input pr-10"
									required
									disabled={isLoading}
								/>
							{/if}
							<button
								type="button"
								on:click={() => (showPassword = !showPassword)}
								class="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-700"
								disabled={isLoading}
							>
								{#if showPassword}
									<EyeOff class="w-5 h-5" />
								{:else}
									<Eye class="w-5 h-5" />
								{/if}
							</button>
						</div>
					</div>

					<button
						type="submit"
						class="btn btn-primary w-full text-lg py-3"
						disabled={isLoading || !email || !password}
					>
						{#if isLoading}
							<div class="flex items-center justify-center space-x-2">
								<div class="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
								<span>Signing in...</span>
							</div>
						{:else}
							Sign In
						{/if}
					</button>
				</div>
			</form>

			<div class="mt-6 text-center">
				<p class="text-gray-600">
					Don't have an account?
					<a href="/register" class="text-primary-600 hover:text-primary-700 font-medium">
						Contact your administrator
					</a>
				</p>
			</div>
		</div>
	</div>
</div>
