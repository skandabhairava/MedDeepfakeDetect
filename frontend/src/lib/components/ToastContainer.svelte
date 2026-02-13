<script lang="ts">
	import { toasts, removeToast } from '$lib/stores/toast';
	import { CheckCircle, XCircle, AlertCircle, Info, X } from 'lucide-svelte';

	function getIcon(type: string) {
		switch (type) {
			case 'success':
				return CheckCircle;
			case 'error':
				return XCircle;
			case 'warning':
				return AlertCircle;
			case 'info':
				return Info;
			default:
				return Info;
		}
	}

	function getToastClasses(type: string) {
		const baseClasses = 'p-4 rounded-lg shadow-lg border-l-4 flex items-start space-x-3 animate-slide-up';
		switch (type) {
			case 'success':
				return `${baseClasses} bg-green-50 border-green-400 text-green-800`;
			case 'error':
				return `${baseClasses} bg-red-50 border-red-400 text-red-800`;
			case 'warning':
				return `${baseClasses} bg-yellow-50 border-yellow-400 text-yellow-800`;
			case 'info':
				return `${baseClasses} bg-blue-50 border-blue-400 text-blue-800`;
			default:
				return `${baseClasses} bg-gray-50 border-gray-400 text-gray-800`;
		}
	}
</script>

<div class="fixed top-20 right-4 z-50 space-y-2 max-w-sm">
	{#each $toasts as toast (toast.id)}
		<div class={getToastClasses(toast.type)} role="alert">
			<svelte:component this={getIcon(toast.type)} class="w-5 h-5 flex-shrink-0 mt-0.5" />
			<div class="flex-1 min-w-0">
				<p class="font-medium">{toast.title}</p>
				{#if toast.message}
					<p class="text-sm opacity-90 mt-1">{toast.message}</p>
				{/if}
			</div>
			<button
				on:click={() => removeToast(toast.id)}
				class="flex-shrink-0 p-1 hover:opacity-70 rounded"
				aria-label="Close notification"
			>
				<X class="w-4 h-4" />
			</button>
		</div>
	{/each}
</div>
