<script lang="ts">
	import '../app.css';
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { user, isAuthenticated } from '$lib/stores/auth';
	import { checkAuth, acceptStudyConsent } from '$lib/services/auth';
	import { goto } from '$app/navigation';
	import Navigation from '$lib/components/Navigation.svelte';
	import ToastContainer from '$lib/components/ToastContainer.svelte';
	import { ShieldAlert } from 'lucide-svelte';

	let authChecked = false;
	let showStudyConsentModal = false;
	let isAcceptingConsent = false;
	let consentCheckboxChecked = false;

	onMount(async () => {
		await checkAuth();
		authChecked = true;
		
		// Check if user is trying to access protected routes
		const publicRoutes = ['/', '/login/', '/privacy/', '/terms/'];
		const currentPath = $page.url.pathname;
		
		if (!publicRoutes.includes(currentPath) && !$isAuthenticated) {
			goto('/login');
		}

		// Show first-login modal if authenticated but study consent not yet recorded
		if ($isAuthenticated && $user && !$user.study_consent_accepted_at) {
			showStudyConsentModal = true;
		}
	});

	// Watch for route changes
	$: if (authChecked && !$isAuthenticated) {
		const publicRoutes = ['/', '/login/', '/privacy/', '/terms/'];
		const currentPath = $page.url.pathname;
		
		if (!publicRoutes.includes(currentPath)) {
			goto('/login');
		}
	}

	// Show modal whenever a logged-in user hasn't accepted yet
	$: if (authChecked && $isAuthenticated && $user && !$user.study_consent_accepted_at) {
		showStudyConsentModal = true;
	}

	async function handleAcceptConsent() {
		if (!consentCheckboxChecked) return;
		isAcceptingConsent = true;
		const ok = await acceptStudyConsent();
		isAcceptingConsent = false;
		if (ok) {
			showStudyConsentModal = false;
		}
	}
</script>

<!-- Mandatory statutory banner — present on every screen -->
<div class="w-full bg-amber-600 text-white text-center py-1.5 px-4 text-xs font-semibold tracking-wide z-50 sticky top-0 shadow-sm">
	For Research and Investigational Use Only. Not for Use in Diagnostic Procedures.
</div>

<Navigation />

<!-- First-Login Study Consent Modal — unavoidable; no dismiss/close/escape -->
{#if showStudyConsentModal}
	<div class="fixed inset-0 z-[200] flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
		<div class="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
			<!-- Header -->
			<div class="bg-primary-700 rounded-t-2xl px-6 py-5 text-white">
				<div class="flex items-center space-x-3 mb-1">
					<ShieldAlert class="w-6 h-6 text-amber-300 flex-shrink-0" />
					<h2 class="text-xl font-bold">Mandatory First-Access Study Agreement</h2>
				</div>
				<p class="text-primary-200 text-sm">You must review and accept this agreement before accessing the platform.</p>
			</div>

			<!-- Body -->
			<div class="px-6 py-5 space-y-4 text-sm text-gray-800">
				<div class="p-3 bg-amber-50 border border-amber-300 rounded-lg text-amber-900 text-xs font-semibold leading-relaxed">
					MedVeri Research Testbed — Restricted Access.<br />
					This app is part of an ongoing scientific investigation. Access is restricted to pre-authorized study investigators.
				</div>

				<div class="space-y-3 leading-relaxed">
					<p><strong>Study Title:</strong> Medical Deepfake Detection Research Study — Investigational Prototype Evaluation</p>

					<p><strong>IRB / Ethics Notice:</strong> This software is an investigational research prototype. It has <strong>not</strong> been cleared or approved by the FDA, CE, or any regulatory authority as a medical device or Software as a Medical Device (SaMD).</p>

					<p><strong>Investigational Nature:</strong> All outputs — including deepfake authenticity signals, arthritis severity index scores, and GradCAM visualizations — are <strong>experimental model benchmarks for research evaluation only</strong>. They do <strong>not</strong> constitute medical diagnoses, clinical assessments, or treatment recommendations.</p>

					<p><strong>No Diagnostic Use:</strong> You agree that you will <strong>not</strong> use any output of this system as a primary or secondary basis for any clinical decision, patient management action, or treatment recommendation.</p>

					<p><strong>De-Identification Obligation:</strong> All medical images submitted must be completely de-identified (HIPAA Safe Harbor / GDPR pseudonymisation). You accept personal legal responsibility for ensuring no Protected Health Information (PHI) is uploaded.</p>

					<p><strong>Data Handling:</strong> Images and metadata are encrypted at rest using AES-256-GCM. No PHI will be shared with third parties.</p>

					<p><strong>Confidentiality:</strong> This platform and its outputs are confidential research materials. Do not share results outside the authorized study team.</p>

					<p><strong>Consent Timestamp:</strong> By clicking "I Accept", your acceptance is recorded server-side with a UTC timestamp as part of the study audit trail.</p>
				</div>

				<!-- Mandatory checkbox -->
				<div class="p-4 bg-blue-50 border border-blue-200 rounded-xl flex items-start space-x-3">
					<input
						id="study-consent-cb"
						type="checkbox"
						bind:checked={consentCheckboxChecked}
						class="mt-0.5 w-4 h-4 text-primary-600 rounded border-gray-300 focus:ring-primary-500 cursor-pointer flex-shrink-0"
					/>
					<label for="study-consent-cb" class="text-xs text-gray-800 leading-relaxed cursor-pointer select-none">
						<strong>I confirm</strong> that I am a pre-authorized study investigator, that I have read and understood this agreement, that I will use this platform solely for the approved research purpose, and that I will ensure all uploaded images are fully de-identified. I understand that outputs are investigational benchmarks and <strong>must not</strong> be used for clinical diagnosis.
					</label>
				</div>

				<p class="text-[11px] text-gray-500 text-center">
					For questions about this study, please contact admin@medveri.xyz.
				</p>
			</div>

			<!-- Action -->
			<div class="px-6 pb-6">
				<button
					on:click={handleAcceptConsent}
					disabled={!consentCheckboxChecked || isAcceptingConsent}
					class="btn btn-primary w-full py-3 text-base font-semibold transition-all duration-200
						{(!consentCheckboxChecked || isAcceptingConsent) ? 'opacity-50 cursor-not-allowed bg-gray-400 hover:bg-gray-400' : 'hover:shadow-md'}"
				>
					{#if isAcceptingConsent}
						<span class="flex items-center justify-center space-x-2">
							<span class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin inline-block"></span>
							<span>Recording agreement...</span>
						</span>
					{:else}
						I Accept — Proceed to Research Platform
					{/if}
				</button>
				{#if !consentCheckboxChecked}
					<p class="text-xs text-amber-700 text-center mt-2">Please check the confirmation box above to proceed.</p>
				{/if}
			</div>
		</div>
	</div>
{/if}

<div class="min-h-screen flex flex-col justify-between" style="padding-top: 4rem;">
	<main class="flex-grow">
		<slot />
	</main>

	<footer class="bg-white border-t border-gray-200 py-6 px-4 sm:px-6 lg:px-8 mt-auto">
		<div class="max-w-7xl mx-auto flex flex-col sm:flex-row justify-between items-center gap-4 text-xs text-gray-500">
			<div class="flex flex-col items-start space-y-1">
				<div class="flex items-center space-x-2">
					<span class="font-medium text-gray-700">MedVeri Research Testbed</span>
					<span>&bull;</span>
					<span>Restricted Access — Pre-Authorized Investigators Only</span>
				</div>
				<span class="text-[10px] text-amber-700 font-semibold">
					For Research and Investigational Use Only. Not for Use in Diagnostic Procedures.
				</span>
			</div>
			<div class="flex items-center space-x-6">
				<a href="/privacy" class="hover:text-primary-600 transition-colors">Privacy Policy</a>
				<a href="/terms" class="hover:text-primary-600 transition-colors">Terms of Service</a>
				<a href="mailto:admin@medveri.xyz" class="hover:text-primary-600 transition-colors">Contact Admin</a>
			</div>
		</div>
	</footer>
</div>

<ToastContainer />

