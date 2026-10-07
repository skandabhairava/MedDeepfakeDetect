<script lang="ts">
	import { page } from '$app/stores';
	import { isAuthenticated, user } from '$lib/stores/auth';
	import { logout } from '$lib/services/auth';
	import { ChevronDown, User, LogOut, Activity } from 'lucide-svelte';

	let showMobileMenu = false;
	let showUserMenu = false;

	$: currentPath = $page.url.pathname;
	$: isAuthPage = currentPath === '/login';

	function handleLogout() {
		logout();
		showUserMenu = false;
	}

	function closeMenus() {
		showMobileMenu = false;
		showUserMenu = false;
	}
</script>

{#if !isAuthPage}
	<nav class="fixed top-0 left-0 right-0 bg-white border-b border-gray-200 z-50">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
			<div class="flex justify-between items-center h-16">
				<!-- Logo and Brand -->
				<div class="flex items-center">
					<a href="/" class="flex items-center space-x-3">
						<div class="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
							<Activity class="w-5 h-5 text-white" />
						</div>
						<span class="text-xl font-semibold text-gray-900">MedScan AI</span>
					</a>
				</div>

				<!-- Desktop Navigation -->
				<div class="hidden md:flex items-center space-x-8">
					<a
						href="/dashboard"
						class="text-gray-700 hover:text-primary-600 px-3 py-2 text-sm font-medium transition-colors"
						class:bg-primary-50={currentPath === '/dashboard'}
					>
						Dashboard
					</a>
					<a
						href="/analyze"
						class="text-gray-700 hover:text-primary-600 px-3 py-2 text-sm font-medium transition-colors"
						class:bg-primary-50={currentPath === '/analyze'}
					>
						Analyze
					</a>
					<a
						href="/history"
						class="text-gray-700 hover:text-primary-600 px-3 py-2 text-sm font-medium transition-colors"
						class:bg-primary-50={currentPath === '/history'}
					>
						History
					</a>
					{#if $user?.is_admin}
						<a
							href="/admin"
							class="text-gray-700 hover:text-primary-600 px-3 py-2 text-sm font-medium transition-colors"
							class:bg-primary-50={currentPath === '/admin'}
						>
							Admin
						</a>
					{/if}
				</div>

				<!-- User Menu -->
				<div class="flex items-center space-x-4">
					{#if $isAuthenticated && $user}
						<div class="relative">
							<button
								on:click={() => (showUserMenu = !showUserMenu)}
								class="flex items-center space-x-2 text-sm rounded-lg hover:bg-gray-100 px-3 py-2 transition-colors"
							>
								<div class="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
									<User class="w-4 h-4 text-primary-600" />
								</div>
								<span class="hidden sm:block font-medium text-gray-700">{$user.account_name}</span>
								<ChevronDown class="w-4 h-4 text-gray-500" />
							</button>

							{#if showUserMenu}
								<div class="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-1">
									<a
										href="/profile"
										class="flex items-center space-x-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
										on:click={closeMenus}
									>
										<User class="w-4 h-4" />
										<span>Profile</span>
									</a>
									<hr class="my-1" />
									<button
										on:click={handleLogout}
										class="flex items-center space-x-2 px-4 py-2 text-sm text-red-600 hover:bg-red-50 w-full text-left"
									>
										<LogOut class="w-4 h-4" />
										<span>Logout</span>
									</button>
								</div>
							{/if}
						</div>
					{:else}
						<a href="/login" class="btn btn-primary">Login</a>
					{/if}

					<!-- Mobile menu button -->
					<button
						on:click={() => (showMobileMenu = !showMobileMenu)}
						class="md:hidden p-2 rounded-lg hover:bg-gray-100"
					>
						<div class="w-6 h-6 flex flex-col justify-center space-y-1">
							<div class="w-full h-0.5 bg-gray-600"></div>
							<div class="w-full h-0.5 bg-gray-600"></div>
							<div class="w-full h-0.5 bg-gray-600"></div>
						</div>
					</button>
				</div>
			</div>

			<!-- Mobile Navigation -->
			{#if showMobileMenu}
				<div class="md:hidden border-t border-gray-200 py-4">
					<div class="flex flex-col space-y-2">
						<a
							href="/dashboard"
							class="text-gray-700 hover:text-primary-600 px-3 py-2 text-sm font-medium"
							class:bg-primary-50={currentPath === '/dashboard'}
							on:click={closeMenus}
						>
							Dashboard
						</a>
						<a
							href="/analyze"
							class="text-gray-700 hover:text-primary-600 px-3 py-2 text-sm font-medium"
							class:bg-primary-50={currentPath === '/analyze'}
							on:click={closeMenus}
						>
							Analyze
						</a>
						<a
							href="/history"
							class="text-gray-700 hover:text-primary-600 px-3 py-2 text-sm font-medium"
							class:bg-primary-50={currentPath === '/history'}
							on:click={closeMenus}
						>
							History
						</a>
						{#if $user?.is_admin}
							<a
								href="/admin"
								class="text-gray-700 hover:text-primary-600 px-3 py-2 text-sm font-medium"
								class:bg-primary-50={currentPath === '/admin'}
								on:click={closeMenus}
							>
								Admin
							</a>
						{/if}
					</div>
				</div>
			{/if}
		</div>
	</nav>

	<!-- Click outside to close menus -->
	{#if showUserMenu || showMobileMenu}
		<div class="fixed inset-0 z-40" on:click={closeMenus}></div>
	{/if}
{/if}
