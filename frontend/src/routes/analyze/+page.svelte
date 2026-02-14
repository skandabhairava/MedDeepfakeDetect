<script lang="ts">
	import { goto } from '$app/navigation';
	import { isAuthenticated } from '$lib/stores/auth';
	import { analyzeXRay, analyzeCTScan } from '$lib/services/analysis';
	import { addToast } from '$lib/stores/toast';
	import { formatFileSize } from '$lib/utils';
	import { Upload, X, Loader2, Image, Brain, Activity } from 'lucide-svelte';

	let selectedFile: File | null = null;
	let analysisType: 'xray' | 'ct' = 'xray';
	let isAnalyzing = false;
	let analysisResult: any = null;
	let dragOver = false;
	let analysisName: string = '';

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
		analysisName = '';
	}

	async function startAnalysis() {
		if (!selectedFile || !analysisName.trim()) return;

		isAnalyzing = true;
		analysisResult = null;

		try {
			if (analysisType === 'xray') {
				analysisResult = await analyzeXRay(selectedFile, analysisName.trim());
			} else {
				analysisResult = await analyzeCTScan(selectedFile, analysisName.trim());
			}
		} finally {
			isAnalyzing = false;
		}
	}

	function getConfidenceColor(confidence: number) {
		if (confidence >= 0.8) return 'text-green-600';
		if (confidence >= 0.6) return 'text-yellow-600';
		return 'text-red-600';
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

		<!-- File Upload -->
		<div class="card mb-6">
			<h2 class="text-lg font-semibold text-gray-900 mb-4">Upload Image</h2>
			
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

					<button
						on:click={startAnalysis}
						disabled={isAnalyzing || !analysisName.trim()}
						class="btn btn-primary w-full"
					>
						{#if isAnalyzing}
							<div class="flex items-center justify-center space-x-2">
								<Loader2 class="w-5 h-5 animate-spin" />
								<span>Analyzing...</span>
							</div>
						{:else}
							<div class="flex items-center justify-center space-x-2">
								<Activity class="w-5 h-5" />
								<span>Start Analysis</span>
							</div>
						{/if}
					</button>
				</div>
			{/if}
		</div>

		<!-- Results -->
		{#if analysisResult}
			<div class="card animate-slide-up">
				<h2 class="text-lg font-semibold text-gray-900 mb-4">Analysis Results</h2>
				
				<!-- Authenticity Results -->
				<div class="mb-6">
					<h3 class="font-medium text-gray-900 mb-3">Authenticity Analysis</h3>
					<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
						<div class="border border-gray-200 rounded-lg p-4">
							<div class="flex items-center space-x-3 mb-2">
								{#if analysisResult.authenticity.is_authentic}
									<div class="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
										<Activity class="w-5 h-5 text-green-600" />
									</div>
								{:else}
									<div class="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center">
										<X class="w-5 h-5 text-red-600" />
									</div>
								{/if}
								<div>
									<p class="font-medium text-gray-900">
										{analysisResult.authenticity.is_authentic ? 'Authentic' : 'Suspicious'}
									</p>
									<p class="text-sm text-gray-600">{analysisResult.authenticity.prediction}</p>
								</div>
							</div>
							<div class="mt-3">
								<div class="flex justify-between items-center mb-1">
									<span class="text-sm text-gray-600">Confidence</span>
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
						</div>

						<div class="border border-gray-200 rounded-lg p-4">
							<h4 class="font-medium text-gray-900 mb-2">Analysis Details</h4>
							<div class="space-y-1 text-sm">
								<div class="flex justify-between">
									<span class="text-gray-600">Model:</span>
									<span class="text-gray-900">{analysisResult.model_name}</span>
								</div>
								<div class="flex justify-between">
									<span class="text-gray-600">Processing Time:</span>
									<span class="text-gray-900">{analysisResult.inference_time.toFixed(2)}s</span>
								</div>
								<div class="flex justify-between">
									<span class="text-gray-600">Device:</span>
									<span class="text-gray-900">{analysisResult.device}</span>
								</div>
							</div>
						</div>
					</div>
				</div>

				<!-- Arthritis Results (X-ray only) -->
				{#if analysisResult.arthritis}
					<div class="mb-6">
						<h3 class="font-medium text-gray-900 mb-3">Arthritis Assessment</h3>
						<div class="border border-gray-200 rounded-lg p-4">
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
					</div>
				{/if}

				<!-- GradCAM Visualization -->
				{#if analysisResult.gradcam}
					<div class="mb-6">
						<h3 class="font-medium text-gray-900 mb-3">GradCAM Visualization</h3>
						<div class="border border-gray-200 rounded-lg p-4">
							<img
								src={`data:image/png;base64,${analysisResult.gradcam}`}
								alt="GradCAM Visualization"
								class="w-full max-h-64 object-contain rounded-lg bg-gray-50"
							/>
							<p class="text-sm text-gray-600 mt-2">
								Areas highlighted in red indicate regions the model focused on during analysis.
							</p>
						</div>
					</div>
				{/if}
			</div>
		{/if}
	</div>
</div>
