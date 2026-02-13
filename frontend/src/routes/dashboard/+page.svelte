<script lang="ts">
	import { goto } from '$app/navigation';
	import { isAuthenticated, user } from '$lib/stores/auth';
	import { getAnalysisHistory } from '$lib/services/analysis';
	import { formatDate, getConfidenceColor } from '$lib/utils';
	import { onMount } from 'svelte';
	import { Activity, TrendingUp, Clock, FileImage } from 'lucide-svelte';

	let recentAnalyses: any[] = [];
	let isLoading = true;

	onMount(async () => {
		if (!$isAuthenticated) {
			goto('/login');
			return;
		}

		// Load recent analyses
		const history = await getAnalysisHistory(1, 5);
		if (history) {
			recentAnalyses = history.history;
		}
		isLoading = false;
	});

	function getAuthenticityIcon(isAuthentic: boolean) {
		return isAuthentic ? TrendingUp : Activity;
	}

	function getAuthenticityColor(isAuthentic: boolean) {
		return isAuthentic ? 'text-green-600' : 'text-red-600';
	}
</script>

<div class="min-h-screen bg-gray-50">
	<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
		<!-- Header -->
		<div class="mb-8">
			<h1 class="text-3xl font-bold text-gray-900">Dashboard</h1>
			<p class="text-gray-600 mt-2">Welcome back, {$user?.account_name}!</p>
		</div>

		<!-- Quick Stats -->
		<div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
			<div class="card">
				<div class="flex items-center justify-between">
					<div>
						<p class="text-sm font-medium text-gray-600">Total Analyses</p>
						<p class="text-2xl font-bold text-gray-900">{recentAnalyses.length}</p>
					</div>
					<div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
						<FileImage class="w-6 h-6 text-blue-600" />
					</div>
				</div>
			</div>

			<div class="card">
				<div class="flex items-center justify-between">
					<div>
						<p class="text-sm font-medium text-gray-600">Authentic Images</p>
						<p class="text-2xl font-bold text-green-600">
							{recentAnalyses.filter(a => a.results.authenticity.is_authentic).length}
						</p>
					</div>
					<div class="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
						<TrendingUp class="w-6 h-6 text-green-600" />
					</div>
				</div>
			</div>

			<div class="card">
				<div class="flex items-center justify-between">
					<div>
						<p class="text-sm font-medium text-gray-600">Suspicious Images</p>
						<p class="text-2xl font-bold text-red-600">
							{recentAnalyses.filter(a => !a.results.authenticity.is_authentic).length}
						</p>
					</div>
					<div class="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center">
						<Activity class="w-6 h-6 text-red-600" />
					</div>
				</div>
			</div>
		</div>

		<!-- Quick Actions -->
		<div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
			<a href="/analyze" class="card hover:shadow-lg transition-shadow duration-300 group">
				<div class="flex items-center space-x-4">
					<div class="w-16 h-16 bg-primary-100 rounded-xl flex items-center justify-center group-hover:bg-primary-200 transition-colors">
						<Activity class="w-8 h-8 text-primary-600" />
					</div>
					<div>
						<h3 class="text-lg font-semibold text-gray-900">Analyze Image</h3>
						<p class="text-gray-600">Upload and analyze medical images</p>
					</div>
				</div>
			</a>

			<a href="/history" class="card hover:shadow-lg transition-shadow duration-300 group">
				<div class="flex items-center space-x-4">
					<div class="w-16 h-16 bg-purple-100 rounded-xl flex items-center justify-center group-hover:bg-purple-200 transition-colors">
						<Clock class="w-8 h-8 text-purple-600" />
					</div>
					<div>
						<h3 class="text-lg font-semibold text-gray-900">View History</h3>
						<p class="text-gray-600">Browse your analysis history</p>
					</div>
				</div>
			</a>
		</div>

		<!-- Recent Analyses -->
		<div class="card">
			<div class="flex items-center justify-between mb-4">
				<h3 class="text-lg font-semibold text-gray-900">Recent Analyses</h3>
				<a href="/history" class="text-primary-600 hover:text-primary-700 text-sm font-medium">
					View All
				</a>
			</div>

			{#if isLoading}
				<div class="flex items-center justify-center py-8">
					<div class="w-8 h-8 border-2 border-primary-600 border-t-transparent rounded-full animate-spin"></div>
				</div>
			{:else if recentAnalyses.length === 0}
				<div class="text-center py-8">
					<FileImage class="w-12 h-12 text-gray-400 mx-auto mb-4" />
					<p class="text-gray-600 mb-4">No analyses yet</p>
					<a href="/analyze" class="btn btn-primary mt-4">
						Start Your First Analysis
					</a>
				</div>
			{:else}
				<div class="space-y-4">
					{#each recentAnalyses as analysis}
						<div class="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors">
							<div class="flex items-center justify-between">
								<div class="flex items-center space-x-3">
									<svelte:component 
										this={getAuthenticityIcon(analysis.results.authenticity.is_authentic)} 
										class="w-5 h-5 {getAuthenticityColor(analysis.results.authenticity.is_authentic)}"
									/>
									<div>
										<p class="font-medium text-gray-900">{analysis.filename}</p>
										<p class="text-sm text-gray-600">
											{analysis.analysis_type.toUpperCase()} • {formatDate(analysis.timestamp)}
										</p>
									</div>
								</div>
								<div class="text-right">
									<p class="text-sm font-medium {getConfidenceColor(analysis.results.authenticity.confidence)}">
										{(analysis.results.authenticity.confidence * 100).toFixed(1)}% confidence
									</p>
									<p class="text-xs text-gray-500">
										{analysis.results.authenticity.is_authentic ? 'Authentic' : 'Suspicious'}
									</p>
								</div>
							</div>
						</div>
					{/each}
				</div>
			{/if}
		</div>
	</div>
</div>
