<script lang="ts">
	import { isAuthenticated } from '$lib/stores/auth';
	import { Shield, Brain, Activity, TrendingUp } from 'lucide-svelte';
</script>

<div class="min-h-screen bg-gradient-to-br from-primary-50 to-white flex items-center justify-center px-4 py-8">
	<div class="max-w-6xl w-full">
		<div class="text-center mb-10">
			<div class="flex justify-center items-center space-x-3 mb-4 mt-2">
				<div class="w-16 h-16 bg-primary-600 rounded-2xl flex items-center justify-center animate-pulse-slow">
					<Brain class="w-10 h-10 text-white" />
				</div>
				<h1 class="text-4xl md:text-5xl font-bold text-gray-900">MedVeri Research Testbed</h1>
			</div>

			<!-- Mandatory landing screen statement -->
			<div class="max-w-3xl mx-auto mb-6 p-4 bg-amber-50 border-2 border-amber-300 rounded-xl shadow-sm text-amber-950 text-sm md:text-base font-semibold leading-relaxed">
				MedVeri Research Testbed — Restricted Access. This app is part of an ongoing scientific investigation. Access is restricted to pre-authorized study investigators.
			</div>

			<p class="text-xs uppercase tracking-widest text-gray-500 font-bold mb-2">
				For Research and Investigational Use Only. Not for Use in Diagnostic Procedures.
			</p>
			<p class="text-base text-gray-600 max-w-2xl mx-auto">
				Experimental machine learning workbench evaluating synthetic manipulation detection and downstream classification performance on medical imaging.
			</p>
		</div>

		<div class="grid md:grid-cols-2 gap-8 mb-12">
			<div class="card hover:shadow-lg transition-shadow duration-300">
				<div class="flex items-center space-x-4 mb-4">
					<div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
						<Shield class="w-6 h-6 text-blue-600" />
					</div>
					<h3 class="text-xl font-semibold text-gray-900">Authenticity Research</h3>
				</div>
				<p class="text-gray-600">
					Dual-domain CNN models evaluate spatial and frequency artifacts to research synthetic manipulation detection in medical scans.
				</p>
			</div>

			<div class="card hover:shadow-lg transition-shadow duration-300">
				<div class="flex items-center space-x-4 mb-4">
					<div class="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
						<Activity class="w-6 h-6 text-green-600" />
					</div>
					<h3 class="text-xl font-semibold text-gray-900">Arthritis Severity Grading (Research Benchmark)</h3>
				</div>
				<p class="text-gray-600">
					Downstream model evaluation of knee X-rays to assess algorithmic performance. Investigational benchmark only; not for clinical diagnosis or treatment recommendations.
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
					Gradient-weighted class activation mapping with hardcoded statutory research watermarking for transparent algorithmic explainability.
				</p>
			</div>

			<div class="card hover:shadow-lg transition-shadow duration-300">
				<div class="flex items-center space-x-4 mb-4">
					<div class="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
						<TrendingUp class="w-6 h-6 text-orange-600" />
					</div>
					<h3 class="text-xl font-semibold text-gray-900">Data History</h3>
				</div>
				<p class="text-gray-600">
					Track your data history and monitor trends over time with insights.
				</p>
			</div>
		</div>

		<div class="text-center">
			<a href={$isAuthenticated ? "/dashboard" : "/login"} class="btn btn-primary text-lg px-8 py-3">
				Enter Research Testbed
			</a>
		</div>
	</div>
</div>
