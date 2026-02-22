<script lang="ts">
	import { goto } from '$app/navigation';
	import { isAuthenticated } from '$lib/stores/auth';
	import { analyzeXRay, analyzeCTScan, getAnalysisStatus } from '$lib/services/analysis';
	import { addToast } from '$lib/stores/toast';
	import { formatFileSize } from '$lib/utils';
	import { getConfidenceColor } from '$lib/utils';
	import { config } from '$lib/config';
	import { onDestroy } from 'svelte';
	import { Upload, X, Loader2, Image, Brain, Activity, Clock, ExternalLink, TrendingUp } from 'lucide-svelte';

	let selectedFile: File | null = null;
	let analysisType: 'xray' | 'ct' = 'xray';
	let isAnalyzing = false;
	let analysisResult: any = null;
	let dragOver = false;
	let analysisName: string = '';
	let queueSubmissionResult = null;
	let statusPollInterval: NodeJS.Timeout | null = null;
	let isRateLimited = false;
	let rateLimitWaitTime = 0;
	let pollCount = 0;

	$: startAnalysisBtnDisabled = isAnalyzing || isRateLimited || queueSubmissionResult || analysisResult || !selectedFile || !analysisName.trim();

	// Redirect if not authenticated
	$: if (!$isAuthenticated) {
		goto('/login');
	}

	function handleFileSelect(event: Event) {
		const target = event.target as HTMLInputElement;
		if (target.files && target.files[0]) {
			selectedFile = target.files[0];
			// Set default name to filename without extension
			const filename = selectedFile.name;
			const nameWithoutExt = filename.substring(0, filename.lastIndexOf('.')) || filename;
			analysisName = nameWithoutExt;
		}
	}

	function handleDrop(event: DragEvent) {
		event.preventDefault();
		dragOver = false;
		
		if (event.dataTransfer?.files && event.dataTransfer.files[0]) {
			selectedFile = event.dataTransfer.files[0];
			// Set default name to filename without extension
			const filename = selectedFile.name;
			const nameWithoutExt = filename.substring(0, filename.lastIndexOf('.')) || filename;
			analysisName = nameWithoutExt;
		}
	}

	function handleDragOver(event: DragEvent) {
		event.preventDefault();
		dragOver = true;
	}

	function handleDragLeave(event: DragEvent) {
		event.preventDefault();
		dragOver = false;
	}

	function clearFile() {
		selectedFile = null;
		analysisResult = null;
		queueSubmissionResult = null;
		analysisName = '';
		isRateLimited = false;
		rateLimitWaitTime = 0;
		
		// Clear status polling
		if (statusPollInterval) {
			clearInterval(statusPollInterval);
			statusPollInterval = null;
		}
	}

	async function startAnalysis() {
		if (!selectedFile || !analysisName.trim()) return;

		// console.log('Starting analysis...', { selectedFile: !!selectedFile, analysisName, analysisType });
		
		isAnalyzing = true;
		analysisResult = null;
		queueSubmissionResult = null;
		isRateLimited = false;
		rateLimitWaitTime = 0;

		try {
			if (analysisType === 'xray') {
				queueSubmissionResult = await analyzeXRay(selectedFile, analysisName.trim());
			} else {
				queueSubmissionResult = await analyzeCTScan(selectedFile, analysisName.trim());
			}
			
			// console.log('Analysis result:', queueSubmissionResult);
			
			// Handle rate limiting response
			if (queueSubmissionResult && !queueSubmissionResult.success && queueSubmissionResult.error === 'rate_limited') {
				// console.log('Rate limited:', queueSubmissionResult);
				isRateLimited = true;
				rateLimitWaitTime = queueSubmissionResult.wait_time || config.analysis.statusPollInterval / 1000;
				startRateLimitCountdown();
			} else if (queueSubmissionResult && queueSubmissionResult.success) {
				// console.log('Analysis submitted successfully:', queueSubmissionResult);
				// Start status polling for successful submission
				startStatusPolling(queueSubmissionResult.history_id);
			}
		} catch (error) {
			// console.error('Analysis error:', error);
			addToast({
				type: 'error',
				title: 'Analysis Failed',
				message: error instanceof Error ? error.message : 'An error occurred during analysis'
			});
		} finally {
			isAnalyzing = false;
		}
	}

	function startRateLimitCountdown() {
		if (statusPollInterval) {
			clearInterval(statusPollInterval);
		}
		
		let remainingTime = rateLimitWaitTime;
		
		statusPollInterval = setInterval(() => {
			remainingTime--;
			rateLimitWaitTime = remainingTime;
			
			if (remainingTime <= 0) {
				clearInterval(statusPollInterval);
				statusPollInterval = null;
				isRateLimited = false;
				rateLimitWaitTime = 0;
			}
		}, 1000);
	}

	// Cleanup on page unload
	onDestroy(() => {
		if (statusPollInterval) {
			clearInterval(statusPollInterval);
		}
	});

	async function startStatusPolling(historyId: number) {
		// console.log('Starting status polling for history_id:', historyId);
		
		if (statusPollInterval) {
			clearInterval(statusPollInterval);
		}
		
		statusPollInterval = setInterval(async () => {
			// console.log('Polling status for history_id:', historyId);
			// console.log('Poll count:', ++pollCount);
			// console.log('Current statusPollInterval ID:', statusPollInterval);
			
			try {
				// console.log('Making API call to getAnalysisStatus...');
				const statusResult = await getAnalysisStatus(historyId);
				// console.log('Status result:', statusResult);
				
				if (statusResult && statusResult.success) {
					const status = statusResult.status;
					// console.log('Current analysis status:', status);
					
					// Update queue position if still pending
					if (status.status === 'pending' && status.queue_position > 0) {
						if (queueSubmissionResult) {
							queueSubmissionResult.queue_position = status.queue_position;
							queueSubmissionResult.estimated_wait_time = status.queue_position * 30;
						}
					}
					
					// Stop polling if analysis is completed or failed
					if (status.status === 'completed' || status.status === 'failed') {
						// console.log('Analysis status changed:', status.status, 'Setting analysisResult:', status.status === 'completed' ? status : null);
						// console.log('Clearing interval:', statusPollInterval);
						clearInterval(statusPollInterval);
						statusPollInterval = null;
						
						// Store the completed analysis result
						if (status.status === 'completed') {
							// Parse the JSON string results from backend
							analysisResult = typeof status.results === 'string' ? JSON.parse(status.results) : status.results;
							// console.log('analysisResult set to:', analysisResult);
						}
						
						// Show completion notification
						if (status.status === 'completed') {
							addToast({
								type: 'success',
								title: 'Analysis Complete',
								message: `Your ${analysisType === 'xray' ? 'X-Ray' : 'CT Scan'} analysis is ready!`
							});
						} else if (status.status === 'failed') {
							addToast({
								type: 'error',
								title: 'Analysis failed',
								message: 'Your analysis could not be completed. Please try again.'
							});
						}
					}
				} else {
					// console.log('Status result failed or missing:', statusResult);
				}
			} catch (error) {
				// console.error('Error polling analysis status:', error);
				// console.error('Error details:', error.message, error.stack);
			}
		}, config.analysis.statusPollInterval);
		
		// console.log('Status polling interval set to:', config.analysis.statusPollInterval, 'ms');
		// console.log('Final statusPollInterval ID:', statusPollInterval);
	}

	function getAuthenticityIcon(analysisResult: any) {
		return analysisResult?.authenticity?.is_real ? Activity : TrendingUp;
	}

	function getAuthenticityColor(analysisResult: any) {
		return analysisResult?.authenticity?.is_real ? 'text-green-600' : 'text-red-600';
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
	<div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
		<!-- Header -->
		<div class="mb-8">
			<h1 class="text-3xl font-bold text-gray-900">Image Analysis</h1>
			<p class="text-gray-600 mt-2">Upload medical images for deepfake detection and analysis</p>
		</div>

		<!-- Analysis Type Selection -->
		<div class="card mb-6">
			<h2 class="text-lg font-semibold text-gray-900 mb-4">Select Analysis Type</h2>
			<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
				<button
					on:click={() => (analysisType = 'xray')}
					class="p-4 border-2 rounded-lg transition-all {analysisType === 'xray'
						? 'border-primary-500 bg-primary-50'
						: 'border-gray-200 hover:border-gray-300'}"
				>
					<div class="flex items-center space-x-3">
						<Image class="w-6 h-6 {analysisType === 'xray' ? 'text-primary-600' : 'text-gray-600'}" />
						<div class="text-left">
							<h3 class="font-medium text-gray-900">Knee X-Ray</h3>
							<p class="text-sm text-gray-600">Authenticity + Arthritis Severity</p>
						</div>
					</div>
				</button>

				<button
					on:click={() => (analysisType = 'ct')}
					class="p-4 border-2 rounded-lg transition-all {analysisType === 'ct'
						? 'border-primary-500 bg-primary-50'
						: 'border-gray-200 hover:border-gray-300'}"
				>
					<div class="flex items-center space-x-3">
						<Brain class="w-6 h-6 {analysisType === 'ct' ? 'text-primary-600' : 'text-gray-600'}" />
						<div class="text-left">
							<h3 class="font-medium text-gray-900">CT Scan</h3>
							<p class="text-sm text-gray-600">Authenticity Analysis Only</p>
						</div>
					</div>
				</button>
			</div>
		</div>

		<!-- Rate Limit Warning -->
		{#if isRateLimited}
			<div class="card border-yellow-200 bg-yellow-50 mb-6">
				<div class="flex items-center space-x-3">
					<div class="w-10 h-10 bg-yellow-100 rounded-full flex items-center justify-center">
						<Clock class="w-5 h-5 text-yellow-600" />
					</div>
					<div>
						<p class="font-medium text-yellow-900">Rate limit in effect</p>
						<p class="text-sm text-yellow-700">Please wait {rateLimitWaitTime} seconds before submitting another analysis</p>
					</div>
				</div>
			</div>
		{/if}

		<!-- File Upload -->
		<div class="card mb-6">
			<h2 class="text-lg font-semibold text-gray-900 mb-4">Upload Image</h2>
			
			<!-- <div class="text-xs text-gray-500 mb-4">
				DEBUG: selectedFile={!!selectedFile}, analysisName="{analysisName}", queueResult={!!queueSubmissionResult}, analysisResult={!!analysisResult}
			</div> -->
			
			{#if !selectedFile}
				<div
					class="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-primary-400 transition-colors {dragOver ? 'border-primary-500 bg-primary-50' : ''}"
					on:drop={handleDrop}
					on:dragover={handleDragOver}
					on:dragleave={handleDragLeave}
				>
					<Upload class="w-12 h-12 text-gray-400 mx-auto mb-4" />
					<p class="text-gray-600 mb-2">Drag and drop your image here, or</p>
					<label class="btn btn-secondary cursor-pointer">
						Browse Files
						<input
							type="file"
							accept="image/*"
							on:change={handleFileSelect}
							class="hidden"
						/>
					</label>
					<p class="text-sm text-gray-500 mt-4">Supports JPG, PNG formats</p>
				</div>
			{:else}
				<div class="border border-gray-200 rounded-lg p-4">
					<div class="flex items-center justify-between mb-4">
						<div class="flex items-center space-x-3">
							<div class="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center">
								<Image class="w-6 h-6 text-gray-600" />
							</div>
							<div>
								<p class="font-medium text-gray-900">{selectedFile.name}</p>
								<p class="text-sm text-gray-600">{formatFileSize(selectedFile.size)}</p>
							</div>
						</div>
						<button
							on:click={clearFile}
							class="p-2 text-gray-500 hover:text-red-600 transition-colors"
						>
							<X class="w-5 h-5" />
						</button>
					</div>

					<!-- Image Preview -->
					<div class="mb-4">
						<img
							src={URL.createObjectURL(selectedFile)}
							alt="Preview"
							class="w-full max-h-64 object-contain rounded-lg bg-gray-50"
						/>
					</div>

					<!-- Name Input -->
					<div class="mb-4">
						<label for="analysis-name" class="block text-sm font-medium text-gray-700 mb-2">
							Analysis Name
						</label>
						<input
							id="analysis-name"
							type="text"
							bind:value={analysisName}
							placeholder="Enter a name for this analysis"
							class="input w-full"
							required
						/>
					</div>
					
					{#if !startAnalysisBtnDisabled}
						<button
							on:click={startAnalysis}
							disabled={startAnalysisBtnDisabled}
							class="btn btn-primary w-full {(startAnalysisBtnDisabled?'bg-gray-300':'')}"
						>
							{#if isAnalyzing}
								<div class="flex items-center justify-center space-x-2">
									<Loader2 class="w-5 h-5 animate-spin" />
									<span>Analyzing...</span>
								</div>
							{:else if isRateLimited}
								<div class="flex items-center justify-center space-x-2">
									<Clock class="w-5 h-5" />
									<span>Wait {rateLimitWaitTime}s</span>
								</div>
							{:else}
								<div class="flex items-center justify-center space-x-2">
									<Activity class="w-5 h-5" />
									<span>Start Analysis</span>
								</div>
							{/if}
						</button>
					{/if}
				</div>
			{/if}
		</div>

		<!-- Results -->
		{#if queueSubmissionResult || analysisResult}
			{#if queueSubmissionResult && !analysisResult}
				<!-- Queue Status -->
				<div class="card animate-slide-up">
					<h2 class="text-lg font-semibold text-gray-900 mb-4">Analysis Submitted</h2>
					
					<div class="border border-blue-200 bg-blue-50 rounded-lg p-4 mb-6">
						<div class="flex items-center space-x-3">
							<div class="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
								<Clock class="w-5 h-5 text-blue-600" />
							</div>
							<div>
								<p class="font-medium text-blue-900">Your analysis is in the queue</p>
								<p class="text-sm text-blue-700">Position: {queueSubmissionResult.queue_position} • Estimated wait: {Math.round(queueSubmissionResult.estimated_wait_time / 60)} minutes</p>
								{#if statusPollInterval}
									<p class="text-xs text-blue-600 mt-1">
										<Loader2 class="w-3 h-3 inline animate-spin mr-1" />
										Auto-updating queue position...
									</p>
								{/if}
							</div>
						</div>
					</div>
				</div>
			{:else if analysisResult}
				<!-- Analysis Results -->
				<div class="card animate-slide-up">
					<h2 class="text-lg font-semibold text-gray-900 mb-4">Analysis Results</h2>
					
					<!-- Authenticity Results -->
					<div class="border border-gray-200 rounded-lg p-4 mb-6">
						<h4 class="font-medium text-gray-900 mb-3">Authenticity Assessment</h4>
						<div class="flex items-center space-x-3">
							<div>
								<p class="text-sm text-gray-600 mb-1">Authenticity Confidence</p>
								<div class="flex justify-between items-center mb-1">
									<span class="text-sm font-medium {getConfidenceColor(analysisResult.authenticity.confidence)}">
										{(analysisResult.authenticity.confidence * 100).toFixed(1)}%
									</span>
								</div>
								<div class="w-full bg-gray-200 rounded-full h-2">
									<div
										class="h-2 rounded-full transition-all duration-500 {analysisResult.authenticity.confidence >= 0.8 ? 'bg-green-500' : analysisResult.authenticity.confidence >= 0.6 ? 'bg-yellow-500' : 'bg-red-500'}"
										style="width: {analysisResult.authenticity.confidence * 100}%"
									></div>
								</div>
							</div>
							<div class="ml-4">
								<div class="flex items-center space-x-2">
									<div class="w-8 h-8 {getAuthenticityColor(analysisResult)} rounded-full flex items-center justify-center">
										<svelte:component this={getAuthenticityIcon(analysisResult)} class="w-4 h-4" />
									</div>
									{#if analysisResult.authenticity.removed_injected}
										<span class="text-sm font-medium text-green-600">
											{analysisResult.authenticity.removed_injected}
										</span>
									{:else}
										<span class="text-sm font-medium {getAuthenticityColor(analysisResult)}">
											{analysisResult.authenticity.is_real ? 'Authentic' : 'Synthetic'}
										</span>
									{/if}
								</div>
							</div>
						</div>
					</div>

					<!-- Arthritis Results -->
					{#if analysisResult.arthritis}
						<div class="border border-gray-200 rounded-lg p-4 mb-6">
							<h4 class="font-medium text-gray-900 mb-3">Arthritis Assessment</h4>
							<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
								<div>
									<p class="text-sm text-gray-600 mb-1">Severity</p>
									<p class="text-lg font-semibold {getArthritisSeverityColor(analysisResult.arthritis.severity)}">
										{analysisResult.arthritis.severity}
									</p>
								</div>
								<div>
									<p class="text-sm text-gray-600 mb-1">Confidence</p>
									<p class="text-lg font-semibold {getConfidenceColor(analysisResult.arthritis.confidence)}">
										{(analysisResult.arthritis.confidence * 100).toFixed(1)}%
									</p>
								</div>
							</div>
							{#if analysisResult.arthritis.classification}
								<p class="text-sm text-gray-600 mt-3">
									Classification: {analysisResult.arthritis.classification}
								</p>
							{/if}
						</div>
					{/if}

					<!-- GradCAM Visualization -->
					{#if analysisResult.gradcam}
						<div class="border border-gray-200 rounded-lg p-4 mb-6">
							<h4 class="font-medium text-gray-900 mb-3">GradCAM Visualization</h4>
							<div class="border border-gray-200 rounded-lg p-4">
								<img
									src={`data:image/png;base64,${analysisResult.gradcam}`}
									alt="GradCAM Visualization"
									class="w-full h-auto"
								/>
								<p class="text-sm text-gray-600 mt-2">
									Areas highlighted in red indicate regions of model focused on during analysis.
								</p>
							</div>
						</div>
					{/if}

					<!-- Actions -->
					<div class="flex items-center space-x-3">
						<a href="/history" class="btn btn-primary flex items-center">
							<ExternalLink class="w-4 h-4 mr-1" />
							View History
						</a>
						<button
							on:click={clearFile}
							class="btn btn-secondary"
						>
							Analyze Another Image
						</button>
					</div>
				</div>

			{/if}
		{/if}
		
	</div>
</div>