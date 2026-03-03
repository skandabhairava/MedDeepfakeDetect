<script lang="ts">
	import { goto } from '$app/navigation';
	import { isAuthenticated } from '$lib/stores/auth';
	import { getAnalysisHistory, deleteHistoryItem } from '$lib/services/analysis';
	import { getConfidenceColor } from '$lib/utils';
	import { formatTimeForUser, formatRelativeTime } from '$lib/utils/timezone';
	import { onMount } from 'svelte';
	import { FileImage, TrendingUp, Activity, ChevronLeft, ChevronRight, X, Download, Trash2, RefreshCw, Loader2 } from 'lucide-svelte';

	let analyses: any[] = [];
	let isLoading = true;
	let currentPage = 1;
	let pageSize = 10;
	let totalItems = 0;
	let totalPages = 0;
	let selectedImage: string | null = null;
	let selectedGradcam: string | null = null;
	let showImageModal = false;
	let showGradcamModal = false;
	let isRefreshing = false;

	// Redirect if not authenticated
	$: if (!$isAuthenticated) {
		goto('/login');
	}

	// Load history on mount
	onMount(async () => {
		if ($isAuthenticated) {
			await loadHistory();
		}
	});

	async function loadHistory() {
		isLoading = true;
		const history = await getAnalysisHistory(currentPage, pageSize);

		console.log(history);

		if (history) {
			analyses = history.history;
			totalItems = history.total;
			totalPages = Math.ceil(totalItems / pageSize);
		}
		isLoading = false;
	}

	async function refreshHistory() {
		isRefreshing = true;
		const history = await getAnalysisHistory(currentPage, pageSize);
		console.log(history);
		if (history) {
			analyses = history.history;
			totalItems = history.total;
			totalPages = Math.ceil(totalItems / pageSize);
		}
		isRefreshing = false;
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

	function isPendingAnalysis(analysis: any) {
		return analysis.results?.status === 'pending';
	}

	function getAnalysisDisplayData(analysis: any) {
		if (isPendingAnalysis(analysis)) {
			return {
				status: analysis.results?.status || 'pending',
				message: analysis.results?.message || 'Processing...',
				showAuthenticity: false,
				showConfidence: false,
				showArthritis: false,
				showGradcam: false
			};
		} else {
			return {
				status: 'completed',
				showAuthenticity: true,
				showConfidence: true,
				showArthritis: analysis.results?.arthritis ? true : false,
				showGradcam: analysis.results?.gradcam ? true : false
			};
		}
	}

	function openImageModal(imageBase64: string) {
		selectedImage = imageBase64;
		showImageModal = true;
	}

	function openGradcamModal(gradcamBase64: string) {
		selectedGradcam = gradcamBase64;
		showGradcamModal = true;
		console.log(gradcamBase64);
	}

	function closeModals() {
		showImageModal = false;
		showGradcamModal = false;
		selectedImage = null;
		selectedGradcam = null;
	}

	function downloadImage(base64Data: string, filename: string) {
		const link = document.createElement('a');
		link.href = `data:image/png;base64,${base64Data}`;
		link.download = filename;
		document.body.appendChild(link);
		link.click();
		document.body.removeChild(link);
	}

	async function handleDelete(historyId: number) {
		if (confirm('Are you sure you want to delete this analysis?')) {
			const success = await deleteHistoryItem(historyId);
			if (success) {
				await loadHistory(); // Reload history
			}
		}
	}

	function formatAnalysisTime(timestamp: string) {
		const relativeTime = formatRelativeTime(timestamp);
		const timeInfo = formatTimeForUser(timestamp);
		return {
			relative: relativeTime,
			full: timeInfo.full_display,
		};
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
		<div class="grid grid-cols-1 md:grid-cols-5 gap-4 mb-8">
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
							{analyses.filter(a => a.results.authenticity.is_real).length}
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
							{analyses.filter(a => !a.results.authenticity.is_real).length}
						</p>
					</div>
				</div>
			</div>
		<!-- </div> -->

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

			<div class="card">
				<div class="flex items-center space-x-3">
					<div class="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
						<FileImage class="w-5 h-5 text-amber-600" />
					</div>
					<div>
						<p class="text-sm text-gray-600">CT Scans</p>
						<p class="text-xl font-bold text-amber-600">
							{analyses.filter(a => a.analysis_type === 'ct').length}
						</p>
					</div>
				</div>
			</div>
		</div>

		<!-- Analyses List -->
		<div class="card">
			<div class="flex items-center justify-between mb-6">
				<h3 class="text-lg font-semibold text-gray-900">Recent Analyses</h3>
				<div class="flex items-center space-x-3">
					<button
						on:click={refreshHistory}
						disabled={isRefreshing}
						class="btn btn-secondary btn-sm flex items-center"
						title="Refresh history"
					>
						<RefreshCw class="w-4 h-4 mr-1 {isRefreshing ? 'animate-spin' : ''}" />
						{isRefreshing ? 'Refreshing...' : 'Refresh'}
					</button>
					<a href="/analyze" class="btn btn-primary">
						New Analysis
					</a>
				</div>
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
						{@const timeInfo = formatAnalysisTime(analysis.timestamp)}
						{@const displayData = getAnalysisDisplayData(analysis)}
						<div class="border border-gray-200 rounded-lg p-6 hover:bg-gray-50 transition-colors">
							<div class="flex items-start justify-between mb-4">
								<div class="flex items-start space-x-4">
									<div class="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center flex-shrink-0">
										<FileImage class="w-6 h-6 text-gray-600" />
									</div>
									<div>
										<h4 class="font-medium text-gray-900">{analysis.name || 'Untitled Analysis'}</h4>
										<p class="text-sm text-gray-600 mt-1">{analysis.filename || 'Unknown File'}</p>
										<div class="flex items-center space-x-4 mt-2">
											<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
												{analysis.analysis_type?.toUpperCase() || 'UNKNOWN'}
											</span>
											<span class="text-sm text-gray-600" title={timeInfo.full}>
												{timeInfo.relative}
											</span>
											{#if displayData.status === 'pending'}
												<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
													Pending
												</span>
											{:else}
												<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
													Completed
												</span>
											{/if}
										</div>
									</div>
								</div>
								<div class="flex items-center space-x-2">
									{#if displayData.showAuthenticity}
										<svelte:component 
											this={getAuthenticityIcon(analysis.results?.authenticity?.is_real)} 
											class="w-5 h-5 {getAuthenticityColor(analysis.results?.authenticity?.is_real)}"
										/>
										{#if analysis.results?.authenticity?.prediction}
											<span class="text-sm font-medium {getAuthenticityColor(analysis.results?.authenticity?.is_real)}">
												{analysis.results?.authenticity?.prediction}
											</span>
										{:else}
											<span class="text-sm font-medium {getAuthenticityColor(analysis.results?.authenticity?.is_real)}">
												{analysis.results?.authenticity?.is_real ? 'Authentic' : 'Synthetic'}
											</span>
										{/if}
									{:else}
										<div class="text-sm text-gray-500">
											{displayData.message}
										</div>
									{/if}
								</div>
							</div>

							<!-- Action Buttons -->
							<div class="flex items-center space-x-2">
								{#if analysis.image_base64}
									<button
										on:click={() => openImageModal(analysis.image_base64)}
										class="btn btn-secondary btn-sm flex items-center"
										title="View original image"
									>
										<FileImage class="w-4 h-4 mr-1" />
										View Image
									</button>
								{/if}
								{#if analysis.results?.gradcam_base64}
									<button
										on:click={() => openGradcamModal(analysis.results.gradcam_base64)}
										class="btn btn-secondary btn-sm flex items-center"
										title="View GradCAM visualization"
									>
										<Activity class="w-4 h-4 mr-1" />
										View GradCAM
									</button>
								{/if}
								<button
									on:click={() => handleDelete(analysis.id)}
									class="btn btn-secondary btn-sm text-red-600 hover:bg-red-50"
									title="Delete analysis"
								>
									<Trash2 class="w-4 h-4" />
								</button>
							</div>

							<!-- Arthritis Results -->
							{#if displayData.showArthritis && analysis.results?.arthritis}
								<div class="border border-gray-200 rounded-lg p-4 mt-4 mb-4">
									<h4 class="font-medium text-gray-900 mb-3">Arthritis Assessment</h4>
									<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
										<div>
											<p class="text-sm text-gray-600 mb-1">Severity</p>
											<p class="text-lg font-semibold {analysis.results.arthritis.severity}">
												{analysis.results.arthritis.severity}
											</p>
										</div>
										<div>
											<p class="text-sm text-gray-600 mb-1">Confidence</p>
											<p class="text-lg font-semibold {getConfidenceColor(analysis.results.arthritis.confidence)}">
												{(analysis.results.arthritis.confidence * 100).toFixed(1)}%
											</p>
										</div>
									</div>
									{#if analysis.results.arthritis.classification}
										<p class="text-sm text-gray-600 mt-3">
											Classification: {analysis.results.arthritis.classification}
										</p>
									{/if}
								</div>
							{/if}

							<!-- GradCAM Visualization -->
							{#if displayData.showGradcam && analysis.results?.gradcam}
								<div class="border border-gray-200 rounded-lg p-4">
									<h4 class="font-medium text-gray-900 mb-3">GradCAM Visualization</h4>
									<div class="border border-gray-200 rounded-lg p-4">
										<img
											src={`data:image/png;base64,${analysis.results.gradcam}`}
											alt="GradCAM Visualization"
											class="w-full h-auto"
										/>
										<p class="text-sm text-gray-600 mt-2">
											Areas highlighted in red indicate regions the model focused on during analysis.
										</p>
									</div>
								</div>
							{/if}

							<div class="grid grid-cols-1 {(analysis.results.arthritis)?'md:grid-cols-4':'md:grid-cols-3'} gap-4">
								<div>
									<p class="text-sm text-gray-600 mb-1">Confidence</p>
									<div class="flex items-center space-x-2">
										{#if displayData.showConfidence && analysis.results?.authenticity?.confidence}
											<div class="flex-1 bg-gray-200 rounded-full h-2">
												<div
													class="h-2 rounded-full {analysis.results.authenticity.confidence >= 0.8 ? 'bg-green-500' : analysis.results.authenticity.confidence >= 0.6 ? 'bg-yellow-500' : 'bg-red-500'}"
													style="width: {analysis.results.authenticity.confidence * 100}%"
												></div>
											</div>
											<span class="text-sm font-medium {getConfidenceColor(analysis.results.authenticity.confidence)} min-w-[3rem] text-right">
												{(analysis.results.authenticity.confidence * 100).toFixed(1)}%
											</span>
										{:else}
											<div class="flex-1 bg-gray-200 rounded-full h-2">
												<div
													class="h-2 rounded-full bg-gray-500"
													style="width: 100%"
												></div>
											</div>
											<span class="text-sm font-medium text-gray-600 min-w-[3rem] text-right">
												<Loader2 class="w-5 h-5 animate-spin" />
											</span>
										{/if}
									</div>
								</div>

								<div>
									<p class="text-sm text-gray-600 mb-1">Model</p>
									<p class="text-sm font-medium text-gray-900">{analysis.results.model_name}</p>
								</div>

								{#if analysis.results.arthritis}
									<div>
										<p class="text-sm text-gray-600 mb-1">Arthritis Severity</p>
										<p class="text-sm font-medium {analysis.results.arthritis.severity}">
											{analysis.results.arthritis.severity}
										</p>
									</div>
								{/if}
									<div>
										<p class="text-sm text-gray-600 mb-1">Processing Time</p>
										<p class="text-sm font-medium text-gray-900">{analysis.results.inference_time.toFixed(2)}s</p>
									</div>
							</div>
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

<!-- Image Modal -->
{#if showImageModal && selectedImage}
	<div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4" on:click={closeModals}>
		<div class="bg-white rounded-lg max-w-4xl max-h-[90vh] overflow-auto" on:click|stopPropagation>
			<div class="sticky top-0 bg-white border-b border-gray-200 p-4 flex items-center justify-between">
				<h3 class="text-lg font-semibold text-gray-900 mr-6">Original Image</h3>
				<div class="flex items-center space-x-2">
					<button
						on:click={() => selectedImage && downloadImage(selectedImage, 'original-image.png')}
						class="btn btn-secondary btn-sm flex items-center"
						disabled={!selectedImage}
					>
						<Download class="w-4 h-4 mr-1" />
						Download
					</button>
					<button
						on:click={closeModals}
						class="p-2 text-gray-500 hover:text-gray-700"
					>
						<X class="w-5 h-5" />
					</button>
				</div>
			</div>
			<div class="p-4">
				<img
					src={`data:image/png;base64,${selectedImage}`}
					alt="Original analysis image"
					class="w-full h-auto"
				/>
			</div>
		</div>
	</div>
{/if}

<!-- GradCAM Modal -->
{#if showGradcamModal && selectedGradcam}
	<div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4" on:click={closeModals}>
		<div class="bg-white rounded-lg max-w-4xl max-h-[90vh] overflow-auto" on:click|stopPropagation>
			<div class="sticky top-0 bg-white border-b border-gray-200 p-4 flex items-center justify-between gap-4">
				<h3 class="text-lg font-semibold text-gray-900">GradCAM Visualization</h3>
				<div class="flex items-center">
					<button
						on:click={() => selectedGradcam && downloadImage(selectedGradcam, 'gradcam-visualization.png')}
						class="btn btn-secondary btn-sm flex items-center"
						disabled={!selectedGradcam}
					>
						<Download class="w-4 h-4 mr-1" />
						Download
					</button>
					<button
						on:click={closeModals}
						class="p-2 text-gray-500 hover:text-gray-700"
					>
						<X class="w-5 h-5" />
					</button>
				</div>
			</div>
			<div class="p-4">
				<img
					src={`data:image/png;base64,${selectedGradcam}`}
					alt="GradCAM visualization"
					class="w-full h-auto"
				/>
			</div>
		</div>
	</div>
{/if}
