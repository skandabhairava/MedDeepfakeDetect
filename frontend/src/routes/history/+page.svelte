<script lang="ts">
	import { goto } from '$app/navigation';
	import { isAuthenticated } from '$lib/stores/auth';
	import { getAnalysisHistory } from '$lib/services/analysis';
	import { formatDate, formatFileSize, getConfidenceColor } from '$lib/utils';
	import { onMount } from 'svelte';
	import { FileImage, TrendingUp, Activity, ChevronLeft, ChevronRight } from 'lucide-svelte';

	let analyses: any[] = [];
	let isLoading = true;
	let currentPage = 1;
	let pageSize = 10;
	let totalItems = 0;
	let totalPages = 0;

	onMount(async () => {
		if (!$isAuthenticated) {
			goto('/login');
			return;
		}
		await loadHistory();
	});

	async function loadHistory() {
		isLoading = true;
		const history = await getAnalysisHistory(currentPage, pageSize);
		if (history) {
			analyses = history.history;
			totalItems = history.total;
			totalPages = Math.ceil(totalItems / pageSize);
		}
		isLoading = false;
	}

	function changePage(newPage: number) {
		if (newPage >= 1 && newPage <= totalPages) {
			currentPage = newPage;
			loadHistory();
		}
	}

	function getAuthenticityIcon(isAuthentic: boolean) {
		return isAuthentic ? TrendingUp : Activity;
	}

	function getAuthenticityColor(isAuthentic: boolean) {
		return isAuthentic ? 'text-green-600' : 'text-red-600';
	}

	function getArthritisSeverityColor(severity: string) {
		switch (severity.toLowerCase()) {
			case 'normal':
			case 'mild':
				return 'text-green-600';
			case 'moderate':
				return 'text-yellow-600';
			case 'severe':
				return 'text-red-600';
			default:
				return 'text-gray-600';
		}
	}
</script>

<div class="min-h-screen bg-gray-50">
	<div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
		<!-- Header -->
		<div class="mb-8">
			<h1 class="text-3xl font-bold text-gray-900">Analysis History</h1>
			<p class="text-gray-600 mt-2">View your past medical image analyses</p>
		</div>

		<!-- Stats Summary -->
		<div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
			<div class="card">
				<div class="flex items-center space-x-3">
					<div class="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
						<FileImage class="w-5 h-5 text-blue-600" />
					</div>
					<div>
						<p class="text-sm text-gray-600">Total Analyses</p>
						<p class="text-xl font-bold text-gray-900">{totalItems}</p>
					</div>
				</div>
			</div>

			<div class="card">
				<div class="flex items-center space-x-3">
					<div class="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
						<TrendingUp class="w-5 h-5 text-green-600" />
					</div>
					<div>
						<p class="text-sm text-gray-600">Authentic</p>
						<p class="text-xl font-bold text-green-600">
							{analyses.filter(a => a.results.authenticity.is_authentic).length}
						</p>
					</div>
				</div>
			</div>

			<div class="card">
				<div class="flex items-center space-x-3">
					<div class="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
						<Activity class="w-5 h-5 text-red-600" />
					</div>
					<div>
						<p class="text-sm text-gray-600">Suspicious</p>
						<p class="text-xl font-bold text-red-600">
							{analyses.filter(a => !a.results.authenticity.is_authentic).length}
						</p>
					</div>
				</div>
			</div>

			<div class="card">
				<div class="flex items-center space-x-3">
					<div class="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
						<FileImage class="w-5 h-5 text-purple-600" />
					</div>
					<div>
						<p class="text-sm text-gray-600">X-Rays</p>
						<p class="text-xl font-bold text-purple-600">
							{analyses.filter(a => a.analysis_type === 'xray').length}
						</p>
					</div>
				</div>
			</div>
		</div>

		<!-- Analyses List -->
		<div class="card">
			<div class="flex items-center justify-between mb-6">
				<h3 class="text-lg font-semibold text-gray-900">Recent Analyses</h3>
				<a href="/analyze" class="btn btn-primary">
					New Analysis
				</a>
			</div>

			{#if isLoading}
				<div class="flex items-center justify-center py-12">
					<div class="w-8 h-8 border-2 border-primary-600 border-t-transparent rounded-full animate-spin"></div>
				</div>
			{:else if analyses.length === 0}
				<div class="text-center py-12">
					<FileImage class="w-16 h-16 text-gray-400 mx-auto mb-4" />
					<h3 class="text-lg font-medium text-gray-900 mb-2">No analyses yet</h3>
					<p class="text-gray-600 mb-6">Start by uploading your first medical image for analysis</p>
					<a href="/analyze" class="btn btn-primary">
						Start Analysis
					</a>
				</div>
			{:else}
				<div class="space-y-4">
					{#each analyses as analysis}
						<div class="border border-gray-200 rounded-lg p-6 hover:bg-gray-50 transition-colors">
							<div class="flex items-start justify-between mb-4">
								<div class="flex items-start space-x-4">
									<div class="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center flex-shrink-0">
										<FileImage class="w-6 h-6 text-gray-600" />
									</div>
									<div>
										<h4 class="font-medium text-gray-900">{analysis.filename}</h4>
										<div class="flex items-center space-x-4 mt-1">
											<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
												{analysis.analysis_type.toUpperCase()}
											</span>
											<span class="text-sm text-gray-600">{formatDate(analysis.timestamp)}</span>
										</div>
									</div>
								</div>
								<div class="flex items-center space-x-2">
									<svelte:component 
										this={getAuthenticityIcon(analysis.results.authenticity.is_authentic)} 
										class="w-5 h-5 {getAuthenticityColor(analysis.results.authenticity.is_authentic)}"
									/>
									<span class="text-sm font-medium {getAuthenticityColor(analysis.results.authenticity.is_authentic)}">
										{analysis.results.authenticity.is_authentic ? 'Authentic' : 'Suspicious'}
									</span>
								</div>
							</div>

							<div class="grid grid-cols-1 md:grid-cols-3 gap-4">
								<div>
									<p class="text-sm text-gray-600 mb-1">Confidence</p>
									<div class="flex items-center space-x-2">
										<div class="flex-1 bg-gray-200 rounded-full h-2">
											<div
												class="h-2 rounded-full {analysis.results.authenticity.confidence >= 0.8 ? 'bg-green-500' : analysis.results.authenticity.confidence >= 0.6 ? 'bg-yellow-500' : 'bg-red-500'}"
												style="width: {analysis.results.authenticity.confidence * 100}%"
											></div>
										</div>
										<span class="text-sm font-medium {getConfidenceColor(analysis.results.authenticity.confidence)} min-w-[3rem] text-right">
											{(analysis.results.authenticity.confidence * 100).toFixed(1)}%
										</span>
									</div>
								</div>

								<div>
									<p class="text-sm text-gray-600 mb-1">Model</p>
									<p class="text-sm font-medium text-gray-900">{analysis.results.model_name}</p>
								</div>

								{#if analysis.results.arthritis}
									<div>
										<p class="text-sm text-gray-600 mb-1">Arthritis Severity</p>
										<p class="text-sm font-medium {getArthritisSeverityColor(analysis.results.arthritis.severity)}">
											{analysis.results.arthritis.severity}
										</p>
									</div>
								{:else}
									<div>
										<p class="text-sm text-gray-600 mb-1">Processing Time</p>
										<p class="text-sm font-medium text-gray-900">{analysis.results.inference_time.toFixed(2)}s</p>
									</div>
								{/if}
							</div>

							{#if analysis.results.analysis_notes}
								<div class="mt-4 p-3 bg-gray-50 rounded-lg">
									<p class="text-sm text-gray-700">{analysis.results.analysis_notes}</p>
								</div>
							{/if}
						</div>
					{/each}
				</div>

				<!-- Pagination -->
				{#if totalPages > 1}
					<div class="flex items-center justify-between mt-6 pt-6 border-t border-gray-200">
						<div class="text-sm text-gray-600">
							Showing {((currentPage - 1) * pageSize) + 1} to {Math.min(currentPage * pageSize, totalItems)} of {totalItems} results
						</div>
						<div class="flex items-center space-x-2">
							<button
								on:click={() => changePage(currentPage - 1)}
								disabled={currentPage === 1}
								class="p-2 rounded-lg border border-gray-300 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
							>
								<ChevronLeft class="w-4 h-4" />
							</button>
							
							{#each Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
								let pageNum;
								if (totalPages <= 5) {
									pageNum = i + 1;
								} else if (currentPage <= 3) {
									pageNum = i + 1;
								} else if (currentPage >= totalPages - 2) {
									pageNum = totalPages - 4 + i;
								} else {
									pageNum = currentPage - 2 + i;
								}
								return pageNum;
							}) as pageNum}
								<button
									on:click={() => changePage(pageNum)}
									class="px-3 py-1 rounded-lg {currentPage === pageNum
										? 'bg-primary-600 text-white'
										: 'border border-gray-300 hover:bg-gray-50'}"
								>
									{pageNum}
								</button>
							{/each}
							
							<button
								on:click={() => changePage(currentPage + 1)}
								disabled={currentPage === totalPages}
								class="p-2 rounded-lg border border-gray-300 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
							>
								<ChevronRight class="w-4 h-4" />
							</button>
						</div>
					</div>
				{/if}
			{/if}
		</div>
	</div>
</div>
