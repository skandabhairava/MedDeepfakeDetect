<script lang="ts">
	import { goto } from '$app/navigation';
	import { isAuthenticated } from '$lib/stores/auth';
	import { analyzeXRay, analyzeCTScan, getAnalysisStatus } from '$lib/services/analysis';
	import { addToast } from '$lib/stores/toast';
	import { formatFileSize } from '$lib/utils';
	import { getConfidenceColor } from '$lib/utils';
	import { config } from '$lib/config';
	import { onDestroy } from 'svelte';
	import { Upload, X, Loader2, Image, Brain, Activity, Clock, ExternalLink, TrendingUp, ShieldAlert } from 'lucide-svelte';
	import type { QueueSubmissionResponse } from '$lib/types';

	let selectedFile: File | null = null;
	let analysisType: 'xray' | 'ct' = 'xray';
	let isAnalyzing = false;
	let analysisResult: any = null;
	let dragOver = false;
	let analysisName: string = '';
	let queueSubmissionResult: QueueSubmissionResponse | null = null;
	let statusPollInterval: ReturnType<typeof setInterval> | null = null;
	let isRateLimited = false;
	let rateLimitWaitTime = 0;
	let pollCount = 0;
	let consentConfirmed = false;

	$: startAnalysisBtnDisabled = isAnalyzing || isRateLimited || !!queueSubmissionResult || !!analysisResult || !selectedFile || !analysisName.trim() || !consentConfirmed;

	// Redirect if not authenticated
	$: if (!$isAuthenticated) {
		goto('/login');
	}

	$: if (analysisResult) {
		console.log(analysisResult)
	}

	$: disableConsentCheck = isAnalyzing || isRateLimited || !!queueSubmissionResult || !!analysisResult || !selectedFile || !analysisName.trim()

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
		consentConfirmed = false;
		
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
				queueSubmissionResult = await analyzeXRay(selectedFile, analysisName.trim(), consentConfirmed);
			} else {
				queueSubmissionResult = await analyzeCTScan(selectedFile, analysisName.trim(), consentConfirmed);
			}
			
			// console.log('Analysis result:', queueSubmissionResult);
			
			// Handle rate limiting response
			if (queueSubmissionResult && !queueSubmissionResult.success && queueSubmissionResult.error === 'rate_limited') {
				// console.log('Rate limited:', queueSubmissionResult);
				isRateLimited = true;
				rateLimitWaitTime = queueSubmissionResult.wait_time || config.analysis.statusPollInterval / 1000;
				startRateLimitCountdown();
			} else if (queueSubmissionResult && queueSubmissionResult.success && queueSubmissionResult.history_id) {
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
				if (statusPollInterval) {
					clearInterval(statusPollInterval);
				}
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
					if (status.status === 'pending' && (status.queue_position ?? 0) > 0) {
						if (queueSubmissionResult) {
							queueSubmissionResult.queue_position = status.queue_position;
							queueSubmissionResult.estimated_wait_time = (status.queue_position ?? 1) * 30;
						}
					}
					
					// Stop polling if analysis is completed or failed
					if (status.status === 'completed' || status.status === 'failed') {
						// console.log('Analysis status changed:', status.status, 'Setting analysisResult:', status.status === 'completed' ? status : null);
						// console.log('Clearing interval:', statusPollInterval);
						if (statusPollInterval) {
							clearInterval(statusPollInterval);
						}
						statusPollInterval = null;
						
						// Show completion notification
						if (status.status === 'completed') {
							// Parse the JSON string results from backend
							analysisResult = typeof status.results === 'string' ? JSON.parse(status.results) : status.results;
							console.log('analysisResult set to:', analysisResult);

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
</script>

<div class="min-h-screen bg-gray-50">
	<div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
		<!-- Header -->
		<div class="mb-8">
			<div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
				<div>
					<h1 class="text-3xl font-bold text-gray-900">Image Analysis</h1>
					<p class="text-gray-600 mt-2">Upload medical images for deepfake detection and authenticity evaluation</p>
				</div>
				<div class="inline-flex items-center px-3.5 py-1.5 rounded-full text-xs font-semibold bg-amber-100 text-amber-900 border border-amber-300 self-start sm:self-auto shadow-sm">
					<ShieldAlert class="w-4 h-4 mr-1.5 text-amber-700 flex-shrink-0" />
					<span>Investigational Prototype • Non-Diagnostic</span>
				</div>
			</div>
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
							accept="image/jpeg, .png, .jpg"
							on:change={handleFileSelect}
							class="hidden"
						/>
					</label>
					<p class="text-sm text-gray-500 mt-4">Supports JPG, PNG formats</p>
					<div class="mt-4 p-2.5 bg-blue-50/80 border border-blue-200 rounded-lg text-xs text-blue-900 text-left flex items-start space-x-2">
						<ShieldAlert class="w-4 h-4 text-blue-600 flex-shrink-0 mt-0.5" />
						<p>
							<strong>Patient Privacy Requirement:</strong> All uploaded medical images must be obtained with patient informed consent and completely de-identified (strip all PHI/PII). See our 
							<a href="/terms" target="_blank" class="text-primary-700 underline font-medium hover:text-primary-800">Terms of Service</a>.
						</p>
					</div>
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
					
					<!-- De-Identification Checklist & Mandatory Clickwrap Consent -->
					<div class="mb-5 p-4 bg-blue-50/80 border border-blue-200 rounded-xl space-y-3">
						<div class="flex items-start space-x-3">
							<input
								id="consent-checkbox"
								type="checkbox"
								bind:checked={consentConfirmed}
								disabled={disableConsentCheck}
								class="mt-1 w-4 h-4 text-primary-600 rounded border-gray-300 focus:ring-primary-500 cursor-pointer"
							/>
							<label for="consent-checkbox" class="text-xs text-gray-800 leading-relaxed cursor-pointer select-none">
								<span class="font-bold text-gray-900 block mb-0.5">Mandatory Clinical Research Certification & De-Identification Warranty:</span>
								I certify that this medical scan has been completely de-identified (containing <strong>NO</strong> patient names, hospital record numbers/MRNs, dates of birth, or burned-in annotations), that patient consent or institutional IRB authorization was obtained, and that this experimental tool will not be used as a primary diagnostic device.
							</label>
						</div>
					</div>

					<button
						on:click={startAnalysis}
						disabled={startAnalysisBtnDisabled}
						class="btn btn-primary w-full text-base py-3 font-semibold transition-all duration-200 {startAnalysisBtnDisabled ? 'opacity-50 cursor-not-allowed bg-gray-400 hover:bg-gray-400' : 'hover:shadow-md'}"
					>
						{#if isAnalyzing}
							<div class="flex items-center justify-center space-x-2">
								<Loader2 class="w-5 h-5 animate-spin" />
								<span>Submitting to Queue...</span>
							</div>
						{:else if isRateLimited}
							<div class="flex items-center justify-center space-x-2">
								<Clock class="w-5 h-5" />
								<span>Rate Limited — Wait {rateLimitWaitTime}s</span>
							</div>
						{:else}
							<div class="flex items-center justify-center space-x-2">
								<Activity class="w-5 h-5" />
								<span>Start Authenticity Analysis</span>
							</div>
						{/if}
					</button>

					{#if !consentConfirmed && selectedFile && analysisName.trim()}
						<p class="text-xs text-amber-700 text-center mt-2 flex items-center justify-center space-x-1">
							<ShieldAlert class="w-3.5 h-3.5 text-amber-600 inline mr-1 flex-shrink-0" />
							<span>Check the de-identification certification above to enable analysis</span>
						</p>
					{/if}

					<p class="text-xs text-gray-500 text-center mt-2">
						By submitting, you agree to our 
						<a href="/terms" target="_blank" class="text-primary-600 underline hover:text-primary-700">Terms of Service</a> & 
						<a href="/privacy" target="_blank" class="text-primary-600 underline hover:text-primary-700">Privacy Policy</a>. Research Use Only.
					</p>

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
								{#if queueSubmissionResult.queue_position && queueSubmissionResult.estimated_wait_time}
								<p class="text-sm text-blue-700">Position: {queueSubmissionResult.queue_position} • Estimated wait: {Math.round(queueSubmissionResult.estimated_wait_time / 60)} minutes</p>
								{/if}
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
					<h2 class="text-lg font-semibold text-gray-900 mb-2">Analysis Results</h2>

					<!-- Mandatory Statutory Non-Diagnostic Disclaimer Strip -->
					<div class="mb-5 p-3.5 bg-amber-50 border border-amber-300 rounded-xl text-xs text-amber-950 flex items-start space-x-2.5">
						<ShieldAlert class="w-4 h-4 text-amber-700 flex-shrink-0 mt-0.5" />
						<div class="leading-relaxed">
							<strong>Investigational Model Benchmark — Non-Diagnostic Output:</strong>
							These outputs are experimental algorithmic predictions for scientific evaluation only and do <strong>not</strong> constitute medical diagnoses or treatment recommendations. Clinical decisions must not be based on these results.
						</div>
					</div>
					
					<!-- Authenticity Results -->
					<div class="border border-gray-200 rounded-lg p-4 mb-6">
						<h4 class="font-medium text-gray-900 mb-3">Authenticity Signal (Research Benchmark)</h4>
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
									{#if analysisResult.authenticity.prediction}
										<span class="text-sm font-medium text-green-600">
											{analysisResult.authenticity.prediction}
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
							<h4 class="font-medium text-gray-900 mb-3">Arthritis Severity Grading (Research Benchmark)</h4>
							<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
								<div>
									<p class="text-sm text-gray-600 mb-1">KL Grade Severity Index (Research Benchmark)</p>
									<p class="text-lg font-semibold {analysisResult.arthritis.severity}">
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
							<p class="text-[11px] text-gray-500 mt-2.5 italic">
								* Value represents an experimental downstream model benchmark score, not a clinical Kellgren-Lawrence grade or medical diagnosis.
							</p>
						</div>
					{/if}

					<!-- GradCAM Visualization -->
					{#if analysisResult.gradcam_base64 || analysisResult.gradcam}
						<div class="border border-gray-200 rounded-lg p-4 mb-6">
							<h4 class="font-medium text-gray-900 mb-3">GradCAM Visualization (Research Use Only)</h4>
							<div class="border border-gray-200 rounded-lg p-4">
								<img
									src={`data:image/png;base64,${analysisResult.gradcam_base64 || analysisResult.gradcam}`}
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