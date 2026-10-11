<script lang="ts">
	import { Shield, AlertTriangle, UserCheck } from 'lucide-svelte';
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
						Effective & Last Updated: October 11, 2026 &bull; 
						<a href="/privacy.txt" target="_blank" rel="noopener noreferrer" class="text-primary-600 hover:text-primary-700 underline font-medium">View Plain Text (privacy.txt)</a>
					</p>
				</div>
			</div>
			<div class="bg-amber-50 border border-amber-200 rounded-xl p-4 text-amber-900 text-sm flex items-start space-x-3">
				<AlertTriangle class="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
				<div>
					<span class="font-semibold">Non-Commercial Research & Investigational Platform Notice:</span>
					MedVeri is a strictly non-commercial scientific testbed for research evaluation of synthetic medical imagery and algorithmic authenticity benchmarks. <strong>This project is NOT for commercial usage, commercial healthcare billing, private patient fees, software resale, software embedding, or monetization.</strong> It is not an FDA-cleared, CE-marked, or certified medical diagnostic device.
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
					This Privacy Policy governs the collection, processing, storage, protection, and deletion of information submitted to the MedVeri platform ("Platform", "we", "us", or "our"). The Platform operates exclusively as a non-commercial scientific testbed for algorithmic experimentation and academic investigation.
				</p>
				<p>
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
						<span>User Obligations</span>
					</p>
					<p>
						Clinicians, researchers, and users submitting imaging data must adhere strictly to applicable patient privacy regulations (including HIPAA, GDPR, and institutional ethical standards):
					</p>
					<ul class="list-disc pl-5 space-y-1 text-sm">
						<li><strong>Explicit Informed Consent:</strong> You represent and warrant that you have obtained all necessary, documented patient informed consents, authorizations, or Institutional Review Board (IRB) ethical clearances to upload imaging data for research and integrity evaluation.</li>
						<li><strong>Mandatory De-Identification:</strong> You must strip, scrub, and de-identify all Protected Health Information (PHI) and Personally Identifiable Information (PII)-including patient names, hospital record numbers (MRNs), social IDs, dates of birth, legible clinical tags, and embedded DICOM patient metadata—prior to transmission. You accept sole personal legal responsibility for ensuring no PHI/PII is uploaded.</li>
					</ul>
				</div>
			</section>

			<!-- Section 3 -->
			<section>
				<h2 class="text-xl font-bold text-gray-900 mb-3 flex items-center space-x-2">
					<span class="text-primary-600">3.</span>
					<span>Information We Collect</span>
				</h2>
				<p>We collect only the minimum data necessary to operate, secure, and validate the platform:</p>
				<ul class="list-disc pl-5 space-y-2">
					<li><strong>Account Credentials:</strong> Username, registered institutional/professional email address, account creation timestamp, and cryptographically hashed passwords.</li>
					<li><strong>Uploaded Medical Scans & Metadata:</strong> Knee X-rays and CT slices submitted for tamper and integrity analysis, alongside user-assigned study labels or filenames.</li>
					<li><stong>Analysis Outputs:</stong> Machine learning inference outputs, classification probabilities/scores, confidence metrics, severity scores, and Grad-CAM visual explanation heatmaps generated during analysis.</li>
					<li><strong>Operational Logs:</strong> Request timestamps, queue processing IDs, processing queue statuses, security logs, and diagnostic error traces used solely for system throughput, platform stability, and security monitoring.</li>
					<li><strong>Consent & Legal Audit Records:</strong> When you accept the Privacy Policy and Terms of Service during registration/login, or provide consent prior to submitting an image for analysis, we record the consent timestamp, IP address, and user-agent. These records are collected solely to evidence legal consent, maintain compliance audit trails, and resolve potential legal disputes.</li>
				</ul>
			</section>

			<!-- Section 4 -->
			<section>
				<h2 class="text-xl font-bold text-gray-900 mb-3 flex items-center space-x-2">
					<span class="text-primary-600">4.</span>
					<span>How Data is Encrypted, Handled & Protected</span>
				</h2>
				<p>
					We enforce strict cryptographic safeguards so that stored medical data remains completely inaccessible to third parties, hosting infrastructure providers, and platform administrators:
				</p>
				<ul class="list-disc pl-5 space-y-1">
					<li><strong>Encryption at Rest:</strong> All stored medical scans, Grad-CAM heatmaps, and protected study metadata (including upload filenames, study labels) are encrypted using authenticated industry-standard encryption. Decryption keys are derived directly from user login credentials. Neither we nor our hosting providers can view or decrypt your uploaded medical data or study metadata, as static master decryption keys and plaintext records are never stored on disk or in the database.</li>
					<li><strong>Encryption in Transit:</strong> All communications and data transmitted between client applications/browsers and our backend endpoints are encrypted in transit using Transport Layer Security (TLS/HTTPS).</li>
					<li><strong>European Union (EU) Infrastructure & Hosting:</strong> Application infrastructure and databases are hosted on servers located within the European Union (EU). Infrastructure providers act solely on our behalf to host and maintain system uptime. Stored patient imaging and study metadata are encrypted and are not accessible in decrypted form to hosting providers or platform administrators.</li>
				</ul>
			</section>

			<!-- Section 5 -->
			<section>
				<h2 class="text-xl font-bold text-gray-900 mb-3 flex items-center space-x-2">
					<span class="text-primary-600">5.</span>
					<span>Email Communications & Marketing Policy</span>
				</h2>
				<ul class="list-disc pl-5 space-y-1">
					<li><strong>No Marketing or Mailing Lists:</strong> We do NOT maintain general marketing mailing lists, send promotional newsletters, or share email addresses with third-party advertisers.</li>
					<li><strong>Mandatory Legal & System Notices:</strong> We will ONLY use your registered email address to deliver legally required notifications (such as material updates to our Terms of Service or Privacy Policy) or critical security/account alerts.</li>
				</ul>
			</section>

			<!-- Section 6 -->
			<section>
				<h2 class="text-xl font-bold text-gray-900 mb-3 flex items-center space-x-2">
					<span class="text-primary-600">6.</span>
					<span>Allocation of Security Liability & Password Disclaimer</span>
				</h2>
				<p class="mb-3">
					As cryptographic access to stored image records relies on keys derived from your secret password, the confidentiality of your data fundamentally depends on you safeguarding your credentials:
				</p>
				<ul class="list-disc pl-5 space-y-1">
					<li><strong>Database Security & Leak Resilience:</strong> In the event of an external database breach or unauthorized database leak, stored image data and study metadata remain encrypted and unreadable without your password-derived decryption key.</li>
					<li><strong>User Liability for Credential Compromise:</strong> We explicitly disclaim all liability if your account, password, session token, or data is accessed as a result of weak passwords, credential reuse, phishing, malware on your personal device, or unauthorized sharing of your credentials. You bear sole responsibility for maintaining credential confidentiality.</li>
				</ul>
			</section>

			<!-- Section 7 -->
			<section class="border-t border-gray-200 pt-6">
				<h2 class="text-xl font-bold text-gray-900 mb-3 flex items-center space-x-2">
					<span class="text-primary-600">7.</span>
					<span>Data Retention, Self-Service Deletion & Administrative Erasure</span>
				</h2>
				<p class="mb-3">
					In accordance with global privacy frameworks (including GDPR, HIPAA, and app store developer standards), users maintain complete self-service control over their data:
				</p>
				<ul class="list-disc pl-5 space-y-1">
					<li><strong>Item Deletion:</strong> You may permanently delete individual past analysis entries at any time via your History dashboard. This immediately purges the corresponding database record and ciphertext from active servers.</li>
					<li><strong>Complete Account & Data Erasure:</strong> You may permanently delete your account and all associated encrypted medical records, analysis data, and encryption keys at any time directly through your Profile settings (Delete Account / Danger Zone). Platform administrators also retain authority to erase accounts upon request or during study decommissioning. Deletion from active systems is immediate and irreversible.</li>
					<li><strong>Limited Retention Exclusions:</strong> Limited consent timestamps, security logs, or legal-compliance audit trails may be retained only where reasonably necessary or required by applicable law, and backup copies expire through the ordinary automated backup-retention cycle.</li>
					<li><strong>User Rights & Consent Withdrawal:</strong> Users may request information regarding their data processing, correction, or data erasure, and may withdraw consent at any time by contacting us. Withdrawal of consent does not affect processing lawfully conducted prior to withdrawal, but may prevent continued use of features requiring that consent.</li>
				</ul>
			</section>

			<!-- Section 8 -->
			<section class="border-t border-gray-200 pt-6">
				<h2 class="text-xl font-bold text-gray-900 mb-3 flex items-center space-x-2">
					<span class="text-primary-600">8.</span>
					<span>No Third-Party Sale or Commercial Exploitation</span>
				</h2>
				<p class="mb-3">
					We do not sell, rent, license, monetize, trade, or disclose user data, uploaded medical images, or consent metadata to advertisers, commercial aggregators, or third parties for their independent commercial purposes. Data is processed exclusively by infrastructure service providers acting strictly on our behalf under confidentiality obligations to host, secure, and maintain the platform.
				</p>
			</section>

			<!-- Section 9 -->
			<section class="border-t border-gray-200 pt-6">
				<h2 class="text-xl font-bold text-gray-900 mb-3 flex items-center space-x-2">
					<span class="text-primary-600">9.</span>
					<span>Contact Information & Grievances</span>
				</h2>
				<p class="mb-3">
					If you have questions, privacy grievances, or requests regarding this Privacy Policy, your rights, or data security practices, please contact our administrative team at: <a href="mailto:admin@medveri.xyz" class="hover:text-primary-600 transition-colors">admin@medveri.xyz</a>
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
