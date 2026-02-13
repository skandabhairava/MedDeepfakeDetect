<script lang="ts">
	import { goto } from '$app/navigation';
	import { user, isAuthenticated } from '$lib/stores/auth';
	import { changePassword } from '$lib/services/auth';
	import { addToast } from '$lib/stores/toast';
	import { formatTimeForUser, formatRelativeTime } from '$lib/utils/timezone';
	import { User, Mail, Calendar, Shield, Eye, EyeOff, Loader2 } from 'lucide-svelte';

	let currentPassword = '';
	let newPassword = '';
	let confirmPassword = '';
	let isLoading = false;
	let showCurrentPassword = false;
	let showNewPassword = false;
	let showConfirmPassword = false;

	// Redirect if not authenticated
	$: if (!$isAuthenticated) {
		goto('/login');
	}

	async function handlePasswordChange() {
		if (!currentPassword || !newPassword || !confirmPassword) {
			addToast({
				type: 'warning',
				title: 'Missing fields',
				message: 'Please fill in all password fields'
			});
			return;
		}

		if (newPassword !== confirmPassword) {
			addToast({
				type: 'error',
				title: 'Passwords do not match',
				message: 'New password and confirmation must be the same'
			});
			return;
		}

		if (newPassword.length < 8) {
			addToast({
				type: 'error',
				title: 'Password too short',
				message: 'Password must be at least 8 characters long'
			});
			return;
		}

		isLoading = true;

		const success = await changePassword({
			current_password: currentPassword,
			new_password: newPassword
		});

		if (success) {
			currentPassword = '';
			newPassword = '';
			confirmPassword = '';
		}

		isLoading = false;
	}
</script>

<div class="min-h-screen bg-gray-50">
	<div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
		<!-- Header -->
		<div class="mb-8">
			<h1 class="text-3xl font-bold text-gray-900">Profile</h1>
			<p class="text-gray-600 mt-2">Manage your account settings and preferences</p>
		</div>

		<div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
			<!-- User Info -->
			<div class="lg:col-span-1">
				<div class="card">
					<div class="text-center">
						<div class="w-20 h-20 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
							<User class="w-10 h-10 text-primary-600" />
						</div>
						<h2 class="text-xl font-semibold text-gray-900 break-words">{$user?.account_name}</h2>
						<p class="text-gray-600 break-words">{$user?.email}</p>
						
						{#if $user?.is_admin}
							<div class="mt-4">
								<span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-purple-100 text-purple-800">
									<Shield class="w-4 h-4 mr-1" />
									Administrator
								</span>
							</div>
						{/if}
					</div>

					<div class="mt-6 pt-6 border-t border-gray-200">
						<div class="space-y-3">
							<div class="flex items-center text-sm text-gray-600" title={$user?.created_at ? formatTimeForUser($user?.created_at).date_display : 'Unknown'}>
								<Calendar class="w-4 h-4 mr-2" />
								Joined {formatRelativeTime($user?.created_at)}
							</div>
						</div>
					</div>
				</div>
			</div>

			<!-- Password Change -->
			<div class="lg:col-span-2">
				<div class="card">
					<h3 class="text-lg font-semibold text-gray-900 mb-6">Change Password</h3>
					
					<form on:submit|preventDefault={handlePasswordChange}>
						<div class="space-y-6">
							<div>
								<label for="current_password" class="label">Current Password</label>
								<div class="relative">
									{#if showCurrentPassword}
										<input
											id="current_password"
											type='text'
											bind:value={currentPassword}
											placeholder="Enter your current password"
											class="input pr-10"
											required
											minlength="8"
											disabled={isLoading}
										/>
									{:else}
										<input
											id="current_password"
											type='password'
											bind:value={currentPassword}
											placeholder="Enter your current password"
											class="input pr-10"
											required
											disabled={isLoading}
										/>
									{/if}
									<button
										type="button"
										on:click={() => (showCurrentPassword = !showCurrentPassword)}
										class="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-700"
										disabled={isLoading}
									>
										{#if showCurrentPassword}
											<EyeOff class="w-5 h-5" />
										{:else}
											<Eye class="w-5 h-5" />
										{/if}
									</button>
								</div>
							</div>

							<div>
								<label for="new_password" class="label">New Password</label>
								<div class="relative">
									{#if showNewPassword}
										<input
											id="new_password"
											type='text'
											bind:value={newPassword}
											placeholder="Enter your new password"
											class="input pr-10"
											required
											minlength="8"
											disabled={isLoading}
										/>
									{:else}
										<input
											id="new_password"
											type='password'
											bind:value={newPassword}
											placeholder="Enter your new password"
											class="input pr-10"
											required
											minlength="8"
											disabled={isLoading}
										/>
									{/if}
									<button
										type="button"
										on:click={() => (showNewPassword = !showNewPassword)}
										class="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-700"
										disabled={isLoading}
									>
										{#if showNewPassword}
											<EyeOff class="w-5 h-5" />
										{:else}
											<Eye class="w-5 h-5" />
										{/if}
									</button>
								</div>
								<p class="text-sm text-gray-500 mt-1">Must be at least 8 characters long</p>
							</div>

							<div>
								<label for="confirm_password" class="label">Confirm New Password</label>
								<div class="relative">
									{#if showConfirmPassword}
										<input
											id="confirm_password"
											type='text'
											bind:value={confirmPassword}
											placeholder="Confirm your new password"
											class="input pr-10"
											required
											minlength="8"
											disabled={isLoading}
										/>
									{:else}
										<input
											id="confirm_password"
											type='password'
											bind:value={confirmPassword}
											placeholder="Confirm your new password"
											class="input pr-10"
											required
											minlength="8"
											disabled={isLoading}
										/>
									{/if}
									<button
										type="button"
										on:click={() => (showConfirmPassword = !showConfirmPassword)}
										class="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-700"
										disabled={isLoading}
									>
										{#if showConfirmPassword}
											<EyeOff class="w-5 h-5" />
										{:else}
											<Eye class="w-5 h-5" />
										{/if}
									</button>
								</div>
							</div>

							<button
								type="submit"
								class="btn btn-primary w-full"
								disabled={isLoading || !currentPassword || !newPassword || !confirmPassword}
							>
								{#if isLoading}
									<div class="flex items-center justify-center space-x-2">
										<Loader2 class="w-5 h-5 animate-spin" />
										<span>Updating Password...</span>
									</div>
								{:else}
									Update Password
								{/if}
							</button>
						</div>
					</form>
				</div>

				<!-- Security Information -->
				<div class="card mt-6">
					<h3 class="text-lg font-semibold text-gray-900 mb-4">Security Information</h3>
					<div class="space-y-4">
						<div class="flex items-center justify-between p-4 bg-green-50 border border-green-200 rounded-lg">
							<div class="flex items-center space-x-3">
								<Shield class="w-5 h-5 text-green-600" />
								<div>
									<p class="font-medium text-green-900">Account Secure</p>
									<p class="text-sm text-green-700">Your account is protected with strong authentication</p>
								</div>
							</div>
						</div>
						
						<div class="text-sm text-gray-600">
							<p class="font-medium mb-2">Security Tips:</p>
							<ul class="list-disc list-inside space-y-1">
								<li>Use a strong, unique password</li>
								<li>Never share your login credentials</li>
								<li>Log out after each session</li>
								<li>Keep your password confidential</li>
							</ul>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
</div>
