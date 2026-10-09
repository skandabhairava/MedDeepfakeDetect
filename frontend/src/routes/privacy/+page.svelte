<script lang="ts">
	import { Shield, Lock, FileText, AlertTriangle, UserCheck, Trash2, Mail } from 'lucide-svelte';
</script>

<svelte:head>
	<title>Privacy Policy - MedVeri</title>
</svelte:head>

<div class="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
	<div class="max-w-4xl mx-auto bg-white rounded-2xl shadow-sm border border-gray-200 p-8 sm:p-12">
		<!-- Header -->
		<div class="border-b border-gray-200 pb-8 mb-8">
			<div class="flex items-center space-x-3 mb-4">
				<div class="w-12 h-12 bg-primary-100 rounded-xl flex items-center justify-center text-primary-600">
					<Shield class="w-6 h-6" />
				</div>
				<div>
					<h1 class="text-3xl font-bold text-gray-900">Privacy Policy</h1>
					<p class="text-sm text-gray-500 mt-1">
						Effective & Last Updated: October 7, 2026 &bull; 
						<a href="/privacy.txt" target="_blank" rel="noopener noreferrer" class="text-primary-600 hover:text-primary-700 underline font-medium">View Plain Text (privacy.txt)</a>
					</p>
				</div>
			</div>
			<div class="bg-amber-50 border border-amber-200 rounded-xl p-4 text-amber-900 text-sm flex items-start space-x-3">
				<AlertTriangle class="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
				<div>
					<span class="font-semibold">Non-Commercial Research & Investigational Platform Notice:</span>
					MedVeri is a strictly non-commercial scientific testbed for research evaluation of synthetic medical imagery and algorithmic authenticity benchmarks. <strong>This project is NOT for commercial usage, commercial clinical practice, or monetization.</strong> It is not an FDA-cleared, CE-marked, or certified medical diagnostic device.
				</div>
			</div>
		</div>

		<!-- Body Content -->
		<div class="space-y-8 text-gray-700 leading-relaxed text-sm sm:text-base">
			<!-- Section 1 -->
			<section>
				<h2 class="text-xl font-bold text-gray-900 mb-3 flex items-center space-x-2">
					<span class="text-primary-600">1.</span>
					<span>Scope & Non-Commercial Research Purpose</span>
				</h2>
				<p>
					This Privacy Policy governs the collection, processing, storage, and protection of information submitted to the MedVeri platform ("Platform", "we", "us", or "our"). <strong>The Platform operates exclusively as a non-commercial scientific testbed for algorithmic experimentation and academic investigation. It is NOT provided for commercial exploitation, fee-for-service clinical billing, or commercial health services.</strong>
				</p>
				<p class="mt-2 text-sm text-gray-600">
					This policy applies to pre-authorized study investigators, healthcare providers, clinical researchers, and institutional participants ("Investigator", "User", or "you") accessing this evaluation workbench.
				</p>
			</section>

			<!-- Section 2 -->
			<section>
				<h2 class="text-xl font-bold text-gray-900 mb-3 flex items-center space-x-2">
					<span class="text-primary-600">2.</span>
					<span>Mandatory Patient Consent & De-Identification</span>
				</h2>
				<div class="p-4 bg-blue-50 border border-blue-200 rounded-xl space-y-2 text-blue-900">
					<p class="font-semibold flex items-center space-x-2">
						<UserCheck class="w-5 h-5 text-blue-700" />
						<span>Doctor / Clinician Obligations</span>
					</p>
					<p>
						Clinicians and researchers submitting imaging data must adhere strictly to applicable patient privacy regulations (including HIPAA, GDPR, and institutional ethical standards):
					</p>
					<ul class="list-disc pl-5 space-y-1 text-sm">
						<li><strong>Explicit Informed Consent:</strong> You represent and warrant that you have obtained all necessary patient informed consents, authorizations, or Institutional Review Board (IRB) approvals to upload imaging data for research and integrity evaluation.</li>
						<li><strong>Mandatory De-Identification:</strong> You must strip and de-identify all Protected Health Information (PHI) and Personally Identifiable Information (PII)—including patient names, hospital record numbers (MRNs), dates of birth, and embedded DICOM patient tags—prior to upload.</li>
					</ul>
				</div>
			</section>

			<!-- Section 3 -->
			<section>
				<h2 class="text-xl font-bold text-gray-900 mb-3 flex items-center space-x-2">
					<span class="text-primary-600">3.</span>
					<span>Information We Collect</span>
				</h2>
				<ul class="list-disc pl-5 space-y-2">
					<li><strong>Account Credentials:</strong> Username, registered institutional/professional email address, account creation timestamp, and cryptographically hashed passwords.</li>
					<li><strong>Uploaded Medical Scans:</strong> Knee X-rays and CT slices submitted for tamper and integrity analysis, alongside arbitrary study labels or identifiers assigned by you.</li>
					<li><strong>Analysis Outputs:</strong> Machine learning inference outputs, classification scores, and Grad-CAM visual explanation heatmaps generated during analysis.</li>
					<li><strong>Operational Logs:</strong> Request timestamps, processing queue statuses, and diagnostic error logs used solely for queue throughput and platform stability.</li>
				</ul>
			</section>

			<!-- Section 4 -->
			<section>
				<h2 class="text-xl font-bold text-gray-900 mb-3 flex items-center space-x-2">
					<span class="text-primary-600">4.</span>
					<span>How Data is Handled and Protected</span>
				</h2>
				<div class="space-y-3">
					<div class="flex items-start space-x-3">
						<Lock class="w-5 h-5 text-primary-600 flex-shrink-0 mt-1" />
						<div>
							<h3 class="font-semibold text-gray-900">Encryption at Rest & Credential-Bound Keys (PHI Protection)</h3>
							<p class="text-sm text-gray-600">
								All stored medical scans, Grad-CAM heatmaps, and sensitive metadata (including upload filenames and study labels) are encrypted at rest using industry-standard authenticated encryption (AES-256-GCM). Cryptographic key derivation (Argon2id) is tied directly to user authentication credentials. No plaintext image data, metadata, or static master decryption keys are stored in the database.
							</p>
						</div>
					</div>
					<div class="flex items-start space-x-3">
						<Shield class="w-5 h-5 text-primary-600 flex-shrink-0 mt-1" />
						<div>
							<h3 class="font-semibold text-gray-900">Volatile Memory Processing & Zero-Fill Ephemeral Storage Wipe</h3>
							<p class="text-sm text-gray-600">
								Temporary scratch files created during neural network inference are processed in isolated environments and sanitized using zero-fill disk sector overwriting prior to unlinking, preventing forensic recovery. Decryption keys exist exclusively in volatile system memory during active sessions and are evicted upon logout.
							</p>
						</div>
					</div>
					<div class="flex items-start space-x-3">
						<FileText class="w-5 h-5 text-primary-600 flex-shrink-0 mt-1" />
						<div>
							<h3 class="font-semibold text-gray-900">Encryption in Transit</h3>
							<p class="text-sm text-gray-600">
								All data transmitted between your browser/client application and our backend endpoints is encrypted in transit using Transport Layer Security (TLS/HTTPS).
							</p>
						</div>
					</div>
				</div>
			</section>

			<!-- Section 5 -->
			<section>
				<h2 class="text-xl font-bold text-gray-900 mb-3 flex items-center space-x-2">
					<span class="text-primary-600">5.</span>
					<span>Allocation of Security Liability & Password Disclaimer</span>
				</h2>
				<div class="p-4 bg-red-50 border border-red-200 rounded-xl space-y-2 text-red-900 text-sm">
					<p class="font-semibold text-base">Notice of Password Security Responsibility:</p>
					<p>
						Because cryptographic access to stored image records relies on keys derived from your secret password, the confidentiality of your data fundamentally depends on you safeguarding your credentials:
					</p>
					<ul class="list-disc pl-5 space-y-1">
						<li><strong>Database Security:</strong> We have implemented best-effort technical defenses and authenticated encryption to safeguard the database. In the event of an external database leak or breach, image data remains encrypted and unreadable without the corresponding password.</li>
						<li><strong>User Liability for Credential Compromise:</strong> We explicitly disclaim all liability if your account, password, session token, or data is accessed as a result of compromised passwords, credential reuse, phishing, malware on your device, or unauthorized credential sharing.</li>
					</ul>
				</div>
			</section>

			<!-- Section 6 -->
			<section>
				<h2 class="text-xl font-bold text-gray-900 mb-3 flex items-center space-x-2">
					<span class="text-primary-600">6.</span>
					<span>Data Retention, Self-Service Deletion & Administrative Erasure</span>
				</h2>
				<p class="mb-3">
					In accordance with Google Play Store, Apple App Store, and international privacy standards, users maintain complete control over their uploaded data:
				</p>
				<div class="grid sm:grid-cols-2 gap-4">
					<div class="p-4 border border-gray-200 rounded-xl">
						<h3 class="font-semibold text-gray-900 flex items-center space-x-2 mb-1">
							<Trash2 class="w-4 h-4 text-red-500" />
							<span>Item Deletion</span>
						</h3>
						<p class="text-xs text-gray-600">
							You may delete individual past analysis entries at any time via your History dashboard. This permanently deletes the record and associated ciphertext from our servers.
						</p>
					</div>
					<div class="p-4 border border-gray-200 rounded-xl">
						<h3 class="font-semibold text-gray-900 flex items-center space-x-2 mb-1">
							<Trash2 class="w-4 h-4 text-primary-600" />
							<span>Complete Account Erasure</span>
						</h3>
						<p class="text-xs text-gray-600">
							You may permanently delete your account and all associated encrypted medical records at any time directly through your Profile settings (Danger Zone). Platform administrators also have the capability to delete accounts upon request or during study decommission. Deletion is immediate and irreversible.
						</p>
					</div>
				</div>
			</section>

			<!-- Section 7 -->
			<section class="border-t border-gray-200 pt-6">
				<h2 class="text-xl font-bold text-gray-900 mb-3">7. Contact Information</h2>
				<p class="text-sm text-gray-600">
					If you have questions regarding this Privacy Policy, your rights, or data security practices, please contact our administrative team at:
					<br />
					<strong>Email:</strong> admin@medveri.xyz
				</p>
			</section>
		</div>

		<!-- Footer Link Back -->
		<div class="mt-12 pt-6 border-t border-gray-200 flex justify-between items-center text-sm text-gray-500">
			<a href="/" class="text-primary-600 hover:text-primary-700 font-medium">&larr; Return to Home</a>
			<a href="/terms" class="text-primary-600 hover:text-primary-700 font-medium">Terms of Service &rarr;</a>
		</div>
	</div>
</div>
