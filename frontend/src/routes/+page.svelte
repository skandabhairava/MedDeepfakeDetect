<script lang="ts">
	// import { goto } from '$app/navigation';
	// import { isAuthenticated } from '$lib/stores/auth';
	// import { onMount } from 'svelte';
	import { Shield, Brain, Activity, TrendingUp } from 'lucide-svelte';

	// onMount(() => {
	// 	if ($isAuthenticated) {
	// 		goto('/dashboard');
	// 	}
	// });
</script>

<div class="min-h-screen bg-gradient-to-br from-primary-50 to-white flex items-center justify-center px-4">
	<div class="max-w-6xl w-full">
		<div class="text-center mb-12">
			<div class="flex justify-center items-center space-x-3 mb-6 mt-4">
				<div class="w-16 h-16 bg-primary-600 rounded-2xl flex items-center justify-center animate-pulse-slow">
					<Brain class="w-10 h-10 text-white" />
				</div>
				<h1 class="text-4xl md:text-5xl font-bold text-gray-900">MedScan AI</h1>
			</div>
			<p class="text-xl text-gray-600 max-w-2xl mx-auto">
				Advanced medical image analysis powered by deep learning for detecting deepfakes and assessing arthritis severity
			</p>
		</div>

		<div class="grid md:grid-cols-2 gap-8 mb-12">
			<div class="card hover:shadow-lg transition-shadow duration-300">
				<div class="flex items-center space-x-4 mb-4">
					<div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
						<Shield class="w-6 h-6 text-blue-600" />
					</div>
					<h3 class="text-xl font-semibold text-gray-900">Deepfake Detection</h3>
				</div>
				<p class="text-gray-600">
					State-of-the-art CNN models analyze medical images to detect sophisticated deepfake manipulations with high accuracy.
				</p>
			</div>

			<div class="card hover:shadow-lg transition-shadow duration-300">
				<div class="flex items-center space-x-4 mb-4">
					<div class="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
						<Activity class="w-6 h-6 text-green-600" />
					</div>
					<h3 class="text-xl font-semibold text-gray-900">Arthritis Assessment</h3>
				</div>
				<p class="text-gray-600">
					Comprehensive analysis of knee X-rays to classify arthritis severity and provide detailed medical insights.
				</p>
			</div>

			<div class="card hover:shadow-lg transition-shadow duration-300">
				<div class="flex items-center space-x-4 mb-4">
					<div class="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
						<Brain class="w-6 h-6 text-purple-600" />
					</div>
					<h3 class="text-xl font-semibold text-gray-900">GradCAM Visualization</h3>
				</div>
				<p class="text-gray-600">
					Visual explanations of model decisions through gradient-weighted class activation mapping for transparency.
				</p>
			</div>

			<div class="card hover:shadow-lg transition-shadow duration-300">
				<div class="flex items-center space-x-4 mb-4">
					<div class="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
						<TrendingUp class="w-6 h-6 text-orange-600" />
					</div>
					<h3 class="text-xl font-semibold text-gray-900">Analysis History</h3>
				</div>
				<p class="text-gray-600">
					Track your analysis history and monitor trends over time with detailed confidence scores and insights.
				</p>
			</div>
		</div>

		<div class="text-center">
			<a href="/login" class="btn btn-primary text-lg px-8 py-3 mr-4">
				Get Started
			</a>
			<a href="#features" class="btn btn-secondary text-lg px-8 py-3">
				Learn More
			</a>
		</div>
	</div>
</div>
