import { writable } from 'svelte/store';

export interface Toast {
	id: string;
	type: 'success' | 'error' | 'warning' | 'info';
	title: string;
	message?: string;
	duration?: number;
}

export const toasts = writable<Toast[]>([]);

export function addToast(toast: Omit<Toast, 'id'>) {
	const id = Date.now().toString();
	const newToast: Toast = {
		id,
		duration: 5000,
		...toast
	};
	
	toasts.update(current => [...current, newToast]);
	
	if (newToast.duration && newToast.duration > 0) {
		setTimeout(() => {
			removeToast(id);
		}, newToast.duration);
	}
	
	return id;
}

export function removeToast(id: string) {
	toasts.update(current => current.filter(toast => toast.id !== id));
}

export function clearToasts() {
	toasts.set([]);
}
