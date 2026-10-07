<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { user, isAuthenticated } from '$lib/stores/auth';
	import { createUser, listUsers, deleteUser } from '$lib/services/auth';
	import { addToast } from '$lib/stores/toast';
	import { formatRelativeTime, formatTimeForUser } from '$lib/utils/timezone';
	import { UserPlus, Users, Trash2, Loader2, Shield, Eye, EyeOff, RefreshCw, Activity, User as UserIcon } from 'lucide-svelte';
	import type { User, UserCreate } from '$lib/types';

	let formData: UserCreate = {
		account_name: '',
		email: '',
		password: '',
		is_admin: false
	};
	let isLoading = false;
	let showPassword = false;

	let users: User[] = [];
	let isLoadingUsers = true;
	let deletingUserId: number | null = null;

	$: if (!$isAuthenticated || !$user?.is_admin) {
		goto('/dashboard');
	}

	onMount(async () => {
		if ($isAuthenticated && $user?.is_admin) {
			await loadUsers();
		}
	});

	async function loadUsers() {
		isLoadingUsers = true;
		users = await listUsers();
		isLoadingUsers = false;
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
			await loadUsers();
		}

		isLoading = false;
	}

	async function handleDeleteUser(targetUser: User) {
		if (targetUser.id === $user?.id) {
			addToast({
				type: 'error',
				title: 'Action not allowed',
				message: 'You cannot delete your own account'
			});
			return;
		}

		if (confirm(`Are you sure you want to delete user "${targetUser.account_name}" (${targetUser.email})? This will permanently delete their account and analysis history.`)) {
			deletingUserId = targetUser.id;
			const success = await deleteUser(targetUser.id);
			if (success) {
				await loadUsers();
			}
			deletingUserId = null;
		}
	}
</script>

<div class="min-h-screen bg-gray-50">
	<div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
		<!-- Header -->
		<div class="mb-8">
			<div class="flex items-center space-x-3 mb-2">
				<Shield class="w-8 h-8 text-purple-600" />
				<h1 class="text-3xl font-bold text-gray-900">Admin Panel</h1>
			</div>
			<p class="text-gray-600">Manage user accounts and view system activity</p>
		</div>

		<!-- Registered Users Table -->
		<div class="card mb-8">
			<div class="flex items-center justify-between mb-6">
				<div class="flex items-center space-x-3">
					<Users class="w-6 h-6 text-primary-600" />
					<div>
						<h2 class="text-xl font-semibold text-gray-900">Registered Users ({users.length})</h2>
						<p class="text-sm text-gray-500">View user details and number of analyses conducted</p>
					</div>
				</div>
				<button
					on:click={loadUsers}
					disabled={isLoadingUsers}
					class="btn btn-secondary btn-sm flex items-center"
					title="Refresh user list"
				>
					<RefreshCw class="w-4 h-4 mr-1 {isLoadingUsers ? 'animate-spin' : ''}" />
					{isLoadingUsers ? 'Refreshing...' : 'Refresh'}
				</button>
			</div>

			{#if isLoadingUsers}
				<div class="flex items-center justify-center py-10">
					<Loader2 class="w-8 h-8 text-primary-600 animate-spin" />
				</div>
			{:else if users.length === 0}
				<div class="text-center py-10 text-gray-500">
					<Users class="w-12 h-12 mx-auto text-gray-400 mb-2" />
					<p>No registered users found.</p>
				</div>
			{:else}
				<div class="overflow-x-auto">
					<table class="min-w-full divide-y divide-gray-200">
						<thead>
							<tr class="bg-gray-50">
								<th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">User</th>
								<th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Role</th>
								<th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Analyses Conducted</th>
								<th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Joined</th>
								<th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
							</tr>
						</thead>
						<tbody class="bg-white divide-y divide-gray-200">
							{#each users as u (u.id)}
								<tr class="hover:bg-gray-50 transition-colors">
									<td class="px-4 py-4 whitespace-nowrap">
										<div class="flex items-center space-x-3">
											<div class="w-9 h-9 {u.is_admin ? 'bg-purple-100 text-purple-600' : 'bg-primary-100 text-primary-600'} rounded-full flex items-center justify-center font-semibold text-sm">
												{u.account_name.charAt(0).toUpperCase()}
											</div>
											<div>
												<div class="text-sm font-medium text-gray-900">{u.account_name}</div>
												<div class="text-xs text-gray-500">{u.email}</div>
											</div>
										</div>
									</td>
									<td class="px-4 py-4 whitespace-nowrap">
										{#if u.is_admin}
											<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
												<Shield class="w-3 h-3 mr-1" />
												Admin
											</span>
										{:else}
											<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
												<UserIcon class="w-3 h-3 mr-1" />
												Regular
											</span>
										{/if}
									</td>
									<td class="px-4 py-4 whitespace-nowrap">
										<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium {u.analyses_count ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-600'}">
											<Activity class="w-3 h-3 mr-1" />
											{u.analyses_count ?? 0} {u.analyses_count === 1 ? 'analysis' : 'analyses'}
										</span>
									</td>
									<td class="px-4 py-4 whitespace-nowrap text-sm text-gray-500" title={formatTimeForUser(u.created_at).date_display}>
										{formatRelativeTime(u.created_at)}
									</td>
									<td class="px-4 py-4 whitespace-nowrap text-right text-sm">
										{#if u.id === $user?.id}
											<span class="text-xs text-gray-400 italic">Current User</span>
										{:else}
											<button
												on:click={() => handleDeleteUser(u)}
												disabled={deletingUserId === u.id}
												class="btn btn-secondary btn-sm text-red-600 hover:bg-red-50 p-2 inline-flex items-center"
												title="Delete user"
											>
												{#if deletingUserId === u.id}
													<Loader2 class="w-4 h-4 animate-spin text-red-600" />
												{:else}
													<Trash2 class="w-4 h-4" />
												{/if}
											</button>
										{/if}
									</td>
								</tr>
							{/each}
						</tbody>
					</table>
				</div>
			{/if}
		</div>

		<div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
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
							<p class="text-sm text-gray-500 mt-1">3-50 characters, displayed in the interface</p>
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
							<p class="text-sm text-gray-500 mt-1">Used for login and notifications</p>
						</div>

						<div>
							<label for="password" class="label">Password</label>
							<div class="relative">
								{#if showPassword}
									<input
										id="password"
										type="text"
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
										type="password"
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
								Grants access to admin functions and user management
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
			<div class="card">
				<h3 class="text-lg font-semibold text-gray-900 mb-4">Admin Information</h3>
				<div class="space-y-4">
					<div class="p-4 bg-blue-50 border border-blue-200 rounded-lg">
						<h4 class="font-medium text-blue-900 mb-2">User Management</h4>
						<p class="text-sm text-blue-700">
							As an administrator, you can view all registered accounts, see their total analysis volume, 
							create new user credentials, and remove accounts as needed.
						</p>
					</div>

					<div class="p-4 bg-purple-50 border border-purple-200 rounded-lg">
						<h4 class="font-medium text-purple-900 mb-2">Account Types</h4>
						<div class="space-y-2 text-sm text-purple-700">
							<div>
								<strong>Regular User:</strong> Can analyze images and view their personal analysis history.
							</div>
							<div>
								<strong>Administrator:</strong> Can access admin functions, manage users, and run analyses.
							</div>
						</div>
					</div>

					<div class="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
						<h4 class="font-medium text-yellow-900 mb-2">Security Guidelines</h4>
						<ul class="text-sm text-yellow-700 space-y-1">
							<li>• Issue strong temporary passwords</li>
							<li>• Deleting a user permanently deletes their analysis records</li>
							<li>• Administrators cannot delete their own active account</li>
						</ul>
					</div>
				</div>
			</div>
		</div>
	</div>
</div>
