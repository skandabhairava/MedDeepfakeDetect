import type { ClassValue } from 'clsx';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
	return twMerge(clsx(inputs));
}

export function formatDate(dateString: string): string {
	return new Date(dateString).toLocaleDateString('en-US', {
		year: 'numeric',
		month: 'short',
		day: 'numeric',
		hour: '2-digit',
		minute: '2-digit'
	});
}

export function formatFileSize(bytes: number): string {
	if (bytes === 0) return '0 Bytes';
	const k = 1024;
	const sizes = ['Bytes', 'KB', 'MB', 'GB'];
	const i = Math.floor(Math.log(bytes) / Math.log(k));
	return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

export function getConfidenceColor(confidence: number): string {
	if (confidence >= 0.8) return 'text-green-600';
	if (confidence >= 0.6) return 'text-yellow-600';
	return 'text-red-600';
}

export function getArthritisSeverityColor(severity: string): string {
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
