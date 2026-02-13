<script lang="ts">
	import { goto } from '$app/navigation';
	import { user, isAuthenticated } from '$lib/stores/auth';
	import { createUser } from '$lib/services/auth';
	import { addToast } from '$lib/stores/toast';
	import { UserPlus, Loader2, Shield, Eye, EyeOff } from 'lucide-svelte';
	import type { UserCreate } from '$lib/types';

	let formData: UserCreate = {
		account_name: '',
		email: '',
		password: '',
		is_admin: false
	};
	let isLoading = false;
	let showPassword = false;

	$: if (!$isAuthenticated || !$user?.is_admin) {
		goto('/dashboard');
	}

	async function handleCreateUser() {
		if (!formData.account_name || !formData.email || !formData.password) {
			addToast({
				type: 'warning',
				title: 'Missing fields',
				message: 'Please fill in all required fields'
			});
			return;
		}

		if (formData.password.length < 8) {
			addToast({
				type: 'error',
				title: 'Password too short',
				message: 'Password must be at least 8 characters long'
			});
			return;
		}

		isLoading = true;

		const success = await createUser(formData);

		if (success) {
			// Reset form
			formData = {
				account_name: '',
				email: '',
				password: '',
				is_admin: false
			};
		}

		isLoading = false;
	}
</script>

<div class="min-h-screen bg-gray-50">
	<div class="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
		<!-- Header -->
		<div class="mb-8">
			<div class="flex items-center space-x-3 mb-4">
				<Shield class="w-8 h-8 text-purple-600" />
				<h1 class="text-3xl font-bold text-gray-900">Admin Panel</h1>
			</div>
			<p class="text-gray-600">Create new user accounts for the Medical Image Analyzer</p>
		</div>

		<!-- Create User Form -->
		<div class="card">
			<div class="flex items-center space-x-3 mb-6">
				<UserPlus class="w-6 h-6 text-primary-600" />
				<h2 class="text-xl font-semibold text-gray-900">Create New User</h2>
			</div>

			<form on:submit|preventDefault={handleCreateUser}>
				<div class="space-y-6">
					<div>
						<label for="account_name" class="label">Account Name</label>
						<input
							id="account_name"
							type="text"
							bind:value={formData.account_name}
							placeholder="Enter user's account name"
							class="input"
							required
							minlength="3"
							maxlength="50"
							disabled={isLoading}
						/>
						<p class="text-sm text-gray-500 mt-1">3-50 characters, will be displayed in the interface</p>
					</div>

					<div>
						<label for="email" class="label">Email Address</label>
						<input
							id="email"
							type="email"
							bind:value={formData.email}
							placeholder="Enter user's email address"
							class="input"
							required
							disabled={isLoading}
						/>
						<p class="text-sm text-gray-500 mt-1">Used for login and account recovery</p>
					</div>

					<div>
						<label for="password" class="label">Password</label>
						<div class="relative">
							{#if showPassword}
								<input
									id="password"
									type='text'
									bind:value={formData.password}
									placeholder="Enter temporary password"
									class="input pr-10"
									required
									minlength="8"
									disabled={isLoading}
								/>
							{:else}
								<input
									id="password"
									type='password'
									bind:value={formData.password}
									placeholder="Enter temporary password"
									class="input pr-10"
									required
									minlength="8"
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
						<p class="text-sm text-gray-500 mt-1">Minimum 8 characters. User can change this after login.</p>
					</div>

					<div>
						<label class="flex items-center space-x-3 cursor-pointer">
							<input
								type="checkbox"
								bind:checked={formData.is_admin}
								class="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
								disabled={isLoading}
							/>
							<span class="text-sm font-medium text-gray-700">Administrator Account</span>
						</label>
						<p class="text-sm text-gray-500 mt-1 ml-7">
							Administrators can create new users and access the admin panel
						</p>
					</div>

					<button
						type="submit"
						class="btn btn-primary w-full"
						disabled={isLoading || !formData.account_name || !formData.email || !formData.password}
					>
						{#if isLoading}
							<div class="flex items-center justify-center space-x-2">
								<Loader2 class="w-5 h-5 animate-spin" />
								<span>Creating User...</span>
							</div>
						{:else}
							<div class="flex items-center justify-center space-x-2">
								<UserPlus class="w-5 h-5" />
								<span>Create User Account</span>
							</div>
						{/if}
					</button>
				</div>
			</form>
		</div>

		<!-- Admin Information -->
		<div class="card mt-6">
			<h3 class="text-lg font-semibold text-gray-900 mb-4">Admin Information</h3>
			<div class="space-y-4">
				<div class="p-4 bg-blue-50 border border-blue-200 rounded-lg">
					<h4 class="font-medium text-blue-900 mb-2">User Management</h4>
					<p class="text-sm text-blue-700">
						As an administrator, you can create new user accounts. Each user will receive login credentials 
						that they can use to access the Medical Image Analyzer. Users can change their passwords after 
						first login through their profile page.
					</p>
				</div>

				<div class="p-4 bg-purple-50 border border-purple-200 rounded-lg">
					<h4 class="font-medium text-purple-900 mb-2">Account Types</h4>
					<div class="space-y-2 text-sm text-purple-700">
						<div>
							<strong>Regular User:</strong> Can analyze images and view their own history
						</div>
						<div>
							<strong>Administrator:</strong> Can create users and access admin functions
						</div>
					</div>
				</div>

				<div class="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
					<h4 class="font-medium text-yellow-900 mb-2">Security Notes</h4>
					<ul class="text-sm text-yellow-700 space-y-1">
						<li>• Use strong temporary passwords</li>
						<li>• Communicate passwords securely</li>
						<li>• Regular users should not have admin access</li>
						<li>• Review user accounts periodically</li>
					</ul>
				</div>
			</div>
		</div>
	</div>
</div>
