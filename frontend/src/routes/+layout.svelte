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
	import { showStudyConsentModal, openStudyConsentModal, closeStudyConsentModal } from '$lib/stores/consent';

	let authChecked = false;
	let isAcceptingConsent = false;
	let consentCheckboxChecked = false;

	const publicRoutes = ['/', '/login/', '/privacy/', '/terms/'];
	const currentPath = $page.url.pathname;

	onMount(async () => {
		await checkAuth();
		authChecked = true;
		
		if (!publicRoutes.includes(currentPath) && !$isAuthenticated) {
			goto('/login');
		}

		// Show first-login modal if authenticated but study consent not yet recorded
		if ($isAuthenticated && $user && !$user.study_consent_accepted_at) {
			if (!publicRoutes.includes(currentPath)) { // dont show consent modal if you're on public routes
				// showStudyConsentModal = true;
				openStudyConsentModal();
			}
		}
	});

	// Watch for route changes
	$: if (authChecked && !$isAuthenticated) {
		if (!publicRoutes.includes(currentPath)) {
			goto('/login');
		}
	}

	// Show modal whenever a logged-in user hasn't accepted yet
	$: if (authChecked && $isAuthenticated && $user && !$user.study_consent_accepted_at) {
		if (!publicRoutes.includes(currentPath)) { // dont show consent modal if you're on public routes
			openStudyConsentModal();
		}
	}

	async function handleAcceptConsent() {
		if (!consentCheckboxChecked) return;
		isAcceptingConsent = true;
		const ok = await acceptStudyConsent();
		isAcceptingConsent = false;
		if (ok) {
			// showStudyConsentModal = false;
			closeStudyConsentModal();
			console.log("closing consent modal", $showStudyConsentModal);
		}
	}
</script>

<svelte:head>
	<title>MedVeri</title>
</svelte:head>

<Navigation />

<!-- First-Login Study Consent Modal — unavoidable; no dismiss/close/escape -->
{#if $showStudyConsentModal}
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
					This platform is strictly an experimental research testbed. Access is restricted exclusively to pre-authorized study investigators and scientific collaborators.
				</div>

				<div class="space-y-3 leading-relaxed">
					<p><strong>Study & Project Title:</strong> Medical Deepfake Detection Research Study — Investigational Prototype Evaluation</p>

                    <p><strong>Strictly Non-Commercial:</strong> This project is strictly for non-commercial academic research. Commercial use, clinical practice, fee-for-service patient billing, software resale, or software embedding is strictly prohibited.</p>

                    <p><strong>Not a Diagnostic Medical Device:</strong> MedVeri is <strong>NOT</strong> cleared or approved by the FDA, CE, or any health authority as Software as a Medical Device (SaMD). Do <strong>NOT</strong> use this system for clinical diagnosis, intervention, or patient treatment.</p>

                    <p><strong>Investigational Model Limitations:</strong> Neural network predictions, authenticity probabilities, severity scores, and Grad-CAM heatmaps are experimental benchmark outputs subject to model error, biases, false positives, and false negatives. Outputs <strong>must never replace human clinical expertise</strong>, and imaging must always be verified by certified specialists.</p>

                    <p><strong>No Doctor-Patient Relationship:</strong> Usage of this platform creates no doctor-patient, radiologist-patient, fiduciary, or healthcare provider relationship between you (or your patients) and platform developers or contributors.</p>

                    <p><strong>Mandatory De-Identification (HIPAA / GDPR):</strong> All uploaded medical scans must be completely scrubbed of Protected Health Information (PHI) and Personally Identifiable Information (PII). You accept personal legal responsibility for ensuring complete de-identification.</p>

                    <p><strong>Security, Encryption & User Password Liability:</strong> Scans and metadata are encrypted at rest with keys derived from user passwords. You bear sole responsibility for securing your login credentials and personal devices.</p>

                    <p><strong>Account Deletion Rights:</strong> Users retain full rights to self-service account termination and data erasure via Profile settings at any time.</p>

					<p><strong>Confidentiality:</strong> This platform and its outputs are confidential research materials. Do not share results outside the authorized study team.</p>

					<p><strong>Consent Timestamp:</strong> By clicking "I Accept", your acceptance is recorded server-side with a UTC timestamp as part of the study audit trail.</p>

					<p class="p-3 bg-gray-50 border border-gray-200 rounded-lg text-xs text-gray-700">
                        📄 <strong>Full Legal Terms:</strong> By proceeding, you agree to these key points and our complete legal policies. Please review the full document at 
                        <a href="/terms" target="_blank" rel="noopener noreferrer" class="text-primary-600 hover:text-primary-700 underline font-semibold">Terms of Service & Research Disclaimer (/terms)</a>.
						<a href="/privacy" target="_blank" rel="noopener noreferrer" class="text-primary-600 hover:text-primary-700 underline font-semibold">Privacy Policy (/privacy)</a>.
                    </p>

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
						<strong>I confirm</strong> that I am a pre-authorized study investigator, that I have read and agree to the <a href="/terms" target="_blank" rel="noopener noreferrer" class="text-primary-600 underline font-medium">Terms of Service</a> and the <a href="/privacy" target="_blank" rel="noopener noreferrer" class="text-primary-600 underline font-medium">Privacy Policy</a>, that I will use this platform solely for the approved non-commercial research purpose, that all uploaded images are fully de-identified, and that outputs <strong>will not be used for clinical diagnosis or patient care</strong>.
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
						I Accept - Proceed to Research Platform
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

