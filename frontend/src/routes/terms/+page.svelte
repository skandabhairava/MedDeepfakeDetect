<script lang="ts">
	import { AlertOctagon, Scale, ShieldAlert, CheckCircle, HelpCircle, FileCheck } from 'lucide-svelte';
</script>

<svelte:head>
	<title>Terms of Service & Research Disclaimer - MedVeri</title>
</svelte:head>

<div class="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
	<div class="max-w-4xl mx-auto bg-white rounded-2xl shadow-sm border border-gray-200 p-8 sm:p-12">
		<!-- Header -->
		<div class="border-b border-gray-200 pb-8 mb-8">
			<div class="flex items-center space-x-3 mb-4">
				<div class="w-12 h-12 bg-primary-100 rounded-xl flex items-center justify-center text-primary-600">
					<Scale class="w-6 h-6" />
				</div>
				<div>
					<h1 class="text-3xl font-bold text-gray-900">Terms of Service & Research Disclaimer</h1>
					<p class="text-sm text-gray-500 mt-1">
						Effective & Last Updated: October 8, 2026 &bull; 
						<a href="/toc.txt" target="_blank" rel="noopener noreferrer" class="text-primary-600 hover:text-primary-700 underline font-medium">View Plain Text (toc.txt)</a>
					</p>
				</div>
			</div>
			
			<div class="bg-red-50 border border-red-200 rounded-xl p-4 text-red-900 text-sm flex items-start space-x-3">
				<AlertOctagon class="w-6 h-6 text-red-600 flex-shrink-0 mt-0.5" />
				<div class="space-y-1">
					<p class="font-bold uppercase tracking-wide">Strict Clinical Disclaimer — Not a Diagnostic Medical Device</p>
					<p>
						MedVeri is an investigational, experimental research tool. It is <strong>NOT</strong> approved by the FDA, CE, or any health regulatory authority as Software as a Medical Device (SaMD). Do <strong>NOT</strong> use this tool as a basis for medical diagnosis, clinical intervention, or patient treatment.
					</p>
				</div>
			</div>
		</div>

		<!-- Body Content -->
		<div class="space-y-8 text-gray-700 leading-relaxed text-sm sm:text-base">
			<!-- Section 1 -->
			<section>
				<h2 class="text-xl font-bold text-gray-900 mb-3 flex items-center space-x-2">
					<span class="text-primary-600">1.</span>
					<span>Strictly Non-Commercial Research Testing Platform</span>
				</h2>
				<p>
					The MedVeri application ("Platform") is an <strong>experimental research testing testbed</strong> developed strictly for academic, scientific, and investigational evaluation. <strong>This project is NOT for commercial usage, commercial clinical practice, private patient billing, commercial software resale, or monetization.</strong> Access is restricted to pre-authorized study investigators and clinicians participating in approved academic/scientific evaluations.
				</p>
				<div class="mt-3 p-4 bg-blue-50 border border-blue-200 rounded-xl space-y-1 text-sm text-blue-900">
					<p class="font-bold">Non-Commercial Scope & Research Purpose:</p>
					<ul class="list-disc pl-5 space-y-1 text-xs sm:text-sm">
						<li><strong>No Commercial Billing or Fees:</strong> The Platform must never be used for fee-for-service clinical billing, commercial medical practice, private patient fees, or commercial software resale.</li>
						<li><strong>Investigational Study Testbed:</strong> Access is restricted exclusively to pre-authorized study investigators, clinicians, and research collaborators participating in scientific evaluations of deepfake detection and algorithmic authenticity benchmarks.</li>
						<li><strong>Academic & Non-Profit Intent:</strong> The platform operates solely as a non-commercial scientific testbed to benchmark neural network resilience against synthetic radiological tampering.</li>
					</ul>
				</div>
				<p class="mt-3">
					MedVeri does <strong>not</strong> provide medical diagnoses, radiological sign-offs, or clinical treatment plans. It is <strong>NOT</strong> cleared by the FDA, CE, or any health regulatory authority as Software as a Medical Device (SaMD). Inferences, authenticity probabilities, and Grad-CAM activation heatmaps are informational benchmark outputs from neural network models and must not replace human clinical expertise.
				</p>
			</section>

			<!-- Section 2 -->
			<section>
				<h2 class="text-xl font-bold text-gray-900 mb-3 flex items-center space-x-2">
					<span class="text-primary-600">2.</span>
					<span>Not A Medical Diagnostic Device</span>
				</h2>
				<div class="p-4 bg-amber-50 border border-amber-200 rounded-xl space-y-2 text-amber-900">
					<p>
						MedVeri is an investigational, experimental research tool. It is NOT approved by the FDA, CE, or any health regulatory authority as Software as a Medical Device (SaMD). Do NOT use this platform as a basis for medical/clinical diagnosis, clinical intervention, or patient treatment.
					</p>
				</div>
			</section>

			<!-- Section 3 -->
			<section>
				<h2 class="text-xl font-bold text-gray-900 mb-3 flex items-center space-x-2">
					<span class="text-primary-600">3.</span>
					<span>Mandatory Specialist Consultation & Known Limitations</span>
				</h2>
				<div class="p-4 bg-amber-50 border border-amber-200 rounded-xl space-y-2 text-amber-900">
					<ul class="list-disc pl-5 space-y-2 mt-2">
						<li>Neural network models are subject to errors, dataset biases, false positives (flagging genuine scans as synthetic), and false negatives (failing to identify manipulations).</li>
						<li>Doctors and clinicians must NEVER rely on outputs from this platform.</li>
						<li>You must ALWAYS verify all imaging with certified radiologists, specialist clinicians, and verified patient documentation.</li>
					</ul>
				</div>
			</section>

			<!-- Section 4 -->
			<section>
				<h2 class="text-xl font-bold text-gray-900 mb-3 flex items-center space-x-2">
					<span class="text-primary-600">4.</span>
					<span>User Representations & Patient Consent</span>
				</h2>
				<p>By registering, logging in, or uploading medical files, you represent, warrant, and agree that:</p>
				<ul class="list-disc pl-5 space-y-2 mt-2">
					<li><strong>Patient Consent:</strong> You have obtained all necessary, informed, and documented patient consents, institutional authorizations, and IRB approvals allowing the upload and computational research evaluation of the scans.</li>
					<li><strong>De-Identification (HIPAA / GDPR):</strong> You have completely scrubbed all Protected Health Information (PHI) and Personally Identifiable Information (PII) before transmission. Scans must not contain identifiable names, social IDs, dates of birth, or legible clinical tags.</li>
					<li><strong>Authorized Professional Status:</strong> You are an authorized healthcare practitioner, researcher, academic, or medical student evaluating image authenticity under appropriate supervision.</li>
					<li><strong>Consent Collection:</strong> When you accept the Privacy Policy and these Terms during first time log-in, and when you provide consent before submitting an image for analysis, the platform may record the consent timestamp, IP address, and user-agent solely to evidence consent and maintain legal/compliance records.</li>
				</ul>
			</section>

			<!-- Section 5 -->
			<section>
				<h2 class="text-xl font-bold text-gray-900 mb-3 flex items-center space-x-2">
					<span class="text-primary-600">5.</span>
					<span>No Doctor-Patient Relationship</span>
				</h2>
				<p>
					Using this Platform does not create any doctor-patient, radiologist-patient, fiduciary, or healthcare provider relationship between you (or your patients) and the platform developers, host providers, or research contributors.
				</p>
			</section>

			<!-- Section 5 -->
			<section>
				<h2 class="text-xl font-bold text-gray-900 mb-3 flex items-center space-x-2">
					<span class="text-primary-600">5.</span>
					<span>Limitation of Liability & Data Breach Disclaimer</span>
				</h2>
				<div class="space-y-4">
					<div class="p-4 bg-gray-50 border border-gray-200 rounded-xl space-y-2">
						<h3 class="font-bold text-gray-900">A. Clinical & Medical Malpractice Disclaimer</h3>
						<p class="text-sm text-gray-600 uppercase tracking-wide">
							TO THE MAXIMUM EXTENT PERMITTED BY LAW, THE DEVELOPERS, SPONSORS, AND OPERATORS SHALL NOT BE LIABLE FOR ANY MISDIAGNOSES, DELAYED DIAGNOSES, ADVERSE CLINICAL OUTCOMES, PHYSICAL INJURY, LOSS OF LIFE, OR DAMAGES ARISING OUT OF RELIANCE UPON ANY OUTPUT, PREDICTION, OR VISUALIZATION GENERATED BY THIS PLATFORM.
						</p>
					</div>

					<div class="p-4 bg-gray-50 border border-gray-200 rounded-xl space-y-2">
						<h3 class="font-bold text-gray-900">B. Security, Encryption & User Password Liability</h3>
						<p class="text-sm text-gray-600">
							We implement state-of-the-art cryptographic safeguards (AES-256 authenticated encryption with Argon2id key derivation) to protect database records at rest. Decryption keys are derived directly from user credentials and are not stored in plaintext by the platform.
						</p>
						<p class="text-sm text-gray-600 font-medium">
							Consequently, if our database is leaked, encrypted data cannot be decrypted without your password. If you compromise, share, reuse, or leak your password or login credentials, or if your local computer is compromised, YOU BEAR SOLE RESPONSIBILITY. We disclaim all liability for any breach, exposure, or unauthorized access resulting from user credential compromise.
						</p>
					</div>
				</div>
			</section>

			<!-- Section 6 -->
			<section>
				<h2 class="text-xl font-bold text-gray-900 mb-3 flex items-center space-x-2">
					<span class="text-primary-600">6.</span>
					<span>Acceptable Use & Platform Integrity</span>
				</h2>
				<p>Users agree not to:</p>
				<ul class="list-disc pl-5 space-y-1 mt-2 text-sm">
					<li>Use or deploy the platform, its backend endpoints, or model inferences for commercial medical operations, fee-for-service clinical billing, or commercial software resale.</li>
					<li>Reverse engineer, exploit, decompile, or exfiltrate model weights for unauthorized commercial purposes.</li>
					<li>Upload corrupted, malicious, or non-medical files intended to compromise service operations.</li>					
					<li>Attempt to bypass rate limits or authentication mechanisms.</li>
				</ul>
			</section>

			<!-- Section 7 -->
			<section class="border-t border-gray-200 pt-6">
				<h2 class="text-xl font-bold text-gray-900 mb-3">
					<span class="text-primary-600">7.</span> 
					Modifications & Account Termination
				</h2>
				<p class="text-sm text-gray-600 mb-2">
					We reserve the right to revise these Terms at any time to reflect updates in regulatory requirements, model updates, or platform features. Continued use of the platform after updates signifies acceptance of the amended Terms.
				</p>
				<p class="text-sm text-gray-600">
					Users may terminate and permanently delete their account at any time via the self-service Delete Account option in Profile settings. Platform administrators also retain the authority to terminate, decommission, or erase accounts and associated study records. Account deletion immediately and irrevocably erases all encrypted scans, outputs, and credentials.
				</p>
			</section>
		</div>

		<!-- Footer Link Back -->
		<div class="mt-12 pt-6 border-t border-gray-200 flex justify-between items-center text-sm text-gray-500">
			<a href="/" class="text-primary-600 hover:text-primary-700 font-medium">&larr; Return to Home</a>
			<a href="/privacy" class="text-primary-600 hover:text-primary-700 font-medium">Privacy Policy &rarr;</a>
		</div>
	</div>
</div>
