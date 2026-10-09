<script lang="ts">
	import { goto } from '$app/navigation';
	import { user, isAuthenticated } from '$lib/stores/auth';
	import { changePassword, deleteCurrentAccount } from '$lib/services/auth';
	import { addToast } from '$lib/stores/toast';
	import { formatTimeForUser, formatRelativeTime } from '$lib/utils/timezone';
	import { User, Mail, Calendar, Shield, Eye, EyeOff, Loader2, FileText, Lock, Trash2, AlertTriangle, X } from 'lucide-svelte';

	let currentPassword = '';
	let newPassword = '';
	let confirmPassword = '';
	let isLoading = false;
	let showCurrentPassword = false;
	let showNewPassword = false;
	let showConfirmPassword = false;

	// Account deletion state & safeguards
	let showDeleteModal = false;
	let deleteConfirmationText = '';
	let isDeletingAccount = false;
	let confirmUnderstandPurge = false;
	let confirmUnderstandIrreversible = false;
	let confirmSelfDeleteIntent = false;

	$: canSubmitDelete = confirmUnderstandPurge &&
		confirmUnderstandIrreversible &&
		confirmSelfDeleteIntent &&
		deleteConfirmationText.trim().toLowerCase() === 'delete my account';

	// Redirect if not authenticated
	$: if (!$isAuthenticated) {
		goto('/login');
	}

	function openDeleteModal() {
		showDeleteModal = true;
		deleteConfirmationText = '';
		confirmUnderstandPurge = false;
		confirmUnderstandIrreversible = false;
		confirmSelfDeleteIntent = false;
	}

	async function handleDeleteAccount() {
		if (!canSubmitDelete) {
			addToast({
				type: 'warning',
				title: 'Safeguards required',
				message: 'Please check all 3 safeguard boxes and type "delete my account" to confirm'
			});
			return;
		}

		isDeletingAccount = true;
		const success = await deleteCurrentAccount();
		isDeletingAccount = false;
		if (success) {
			showDeleteModal = false;
		}
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
								Joined {formatRelativeTime($user?.created_at || '')}
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

				<!-- Legal & Compliance Policies -->
				<div class="card mt-6">
					<h3 class="text-lg font-semibold text-gray-900 mb-4 flex items-center space-x-2">
						<FileText class="w-5 h-5 text-primary-600" />
						<span>Legal & Compliance Policies</span>
					</h3>
					<p class="text-sm text-gray-600 mb-4">
						Review our research platform terms, clinical disclaimers, and data protection policies:
					</p>
					<div class="space-y-3">
						<a
							href="/privacy"
							class="flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors group"
						>
							<div class="flex items-center space-x-3">
								<Lock class="w-4 h-4 text-gray-500 group-hover:text-primary-600" />
								<div>
									<p class="text-sm font-medium text-gray-900 group-hover:text-primary-600">Privacy Policy</p>
									<p class="text-xs text-gray-500">Data encryption, patient consent rules, and data retention</p>
								</div>
							</div>
							<span class="text-xs font-medium text-primary-600">&rarr;</span>
						</a>

						<a
							href="/terms"
							class="flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors group"
						>
							<div class="flex items-center space-x-3">
								<Shield class="w-4 h-4 text-gray-500 group-hover:text-primary-600" />
								<div>
									<p class="text-sm font-medium text-gray-900 group-hover:text-primary-600">Terms of Service & Research Disclaimer</p>
									<p class="text-xs text-gray-500">Non-diagnostic use disclaimer and liability terms</p>
								</div>
							</div>
							<span class="text-xs font-medium text-primary-600">&rarr;</span>
						</a>
					</div>
				</div>

				<!-- Danger Zone: Account Deletion (Self-Service & Admin Deletion) -->
				<div class="card mt-6 border-red-200 bg-red-50/40">
					<h3 class="text-lg font-semibold text-red-900 mb-2 flex items-center space-x-2">
						<Trash2 class="w-5 h-5 text-red-600" />
						<span>Danger Zone</span>
					</h3>
					<p class="text-xs text-red-700 mb-4 leading-relaxed">
						Permanently delete your account and all associated data. You can self-delete your account at any time, and administrators can also delete accounts. All your encrypted scans, Grad-CAM heatmaps, credentials, and analysis history will be permanently erased. This action cannot be undone.
					</p>
					<button
						type="button"
						on:click={openDeleteModal}
						class="btn bg-white hover:bg-red-50 text-red-600 border border-red-300 text-sm font-semibold flex items-center space-x-2"
					>
						<Trash2 class="w-4 h-4 text-red-600" />
						<span>Delete My Account</span>
					</button>
				</div>
			</div>
		</div>
	</div>
</div>

<!-- Delete Account Confirmation Modal -->
{#if showDeleteModal}
	<div class="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
		<div class="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-gray-200 animate-slide-up space-y-4">
			<div class="flex items-start justify-between">
				<div class="w-12 h-12 bg-red-100 rounded-xl flex items-center justify-center text-red-600 flex-shrink-0">
					<AlertTriangle class="w-6 h-6" />
				</div>
				<button
					type="button"
					on:click={() => (showDeleteModal = false)}
					class="text-gray-400 hover:text-gray-600"
					disabled={isDeletingAccount}
				>
					<X class="w-5 h-5" />
				</button>
			</div>

			<div>
				<h3 class="text-lg font-bold text-gray-900">Permanently Delete Account?</h3>
				<p class="text-sm text-gray-600 mt-2">
					This action is <strong>immediate and irreversible</strong>. Your account, encrypted medical imagery, and analysis records will be permanently purged from the database.
				</p>
			</div>

			<div class="p-3 bg-red-50 border border-red-200 rounded-lg text-xs text-red-800 space-y-1">
				<p class="font-semibold">Compliance Note (Apple 5.1.1(v) & GDPR Art. 17):</p>
				<p>Users and administrators both possess deletion rights. Your encryption key is immediately evicted from memory and all stored ciphertext is destroyed.</p>
			</div>

			<!-- Required Safeguard Checkmarks -->
			<div class="space-y-2.5 p-3.5 bg-gray-50 border border-gray-200 rounded-xl text-xs text-gray-800">
				<p class="font-bold text-gray-900 mb-1">Required Safeguard Confirmations:</p>

				<label class="flex items-start space-x-2.5 cursor-pointer">
					<input
						type="checkbox"
						bind:checked={confirmUnderstandPurge}
						class="mt-0.5 w-4 h-4 text-red-600 rounded border-gray-300 focus:ring-red-500 cursor-pointer flex-shrink-0"
						disabled={isDeletingAccount}
					/>
					<span class="leading-relaxed">
						I understand that deleting my account permanently erases all my encrypted medical scans, Grad-CAM visualizations, and analysis history.
					</span>
				</label>

				<label class="flex items-start space-x-2.5 cursor-pointer">
					<input
						type="checkbox"
						bind:checked={confirmUnderstandIrreversible}
						class="mt-0.5 w-4 h-4 text-red-600 rounded border-gray-300 focus:ring-red-500 cursor-pointer flex-shrink-0"
						disabled={isDeletingAccount}
					/>
					<span class="leading-relaxed">
						I understand that this action is immediate, final, and cannot be undone by administrators or support.
					</span>
				</label>

				<label class="flex items-start space-x-2.5 cursor-pointer">
					<input
						type="checkbox"
						bind:checked={confirmSelfDeleteIntent}
						class="mt-0.5 w-4 h-4 text-red-600 rounded border-gray-300 focus:ring-red-500 cursor-pointer flex-shrink-0"
						disabled={isDeletingAccount}
					/>
					<span class="leading-relaxed">
						I confirm that I want to permanently delete my account and forfeit all access to this research testbed.
					</span>
				</label>
			</div>

			<div>
				<label for="delete_confirm_input" class="block text-xs font-medium text-gray-700 mb-1">
					Type <span class="font-bold text-red-600">delete my account</span> to confirm:
				</label>
				<input
					id="delete_confirm_input"
					type="text"
					bind:value={deleteConfirmationText}
					placeholder="delete my account"
					class="input text-sm border-red-300 focus:border-red-500 focus:ring-red-500"
					disabled={isDeletingAccount}
				/>
			</div>

			<div class="flex items-center space-x-3 pt-2">
				<button
					type="button"
					on:click={() => (showDeleteModal = false)}
					class="btn btn-secondary flex-1"
					disabled={isDeletingAccount}
				>
					Cancel
				</button>
				<button
					type="button"
					on:click={handleDeleteAccount}
					class="btn bg-red-600 hover:bg-red-700 text-white flex-1 font-semibold flex items-center justify-center space-x-2"
					disabled={!canSubmitDelete || isDeletingAccount}
				>
					{#if isDeletingAccount}
						<Loader2 class="w-4 h-4 animate-spin" />
						<span>Deleting...</span>
					{:else}
						<Trash2 class="w-4 h-4" />
						<span>Confirm Delete</span>
					{/if}
				</button>
			</div>
		</div>
	</div>
{/if}


