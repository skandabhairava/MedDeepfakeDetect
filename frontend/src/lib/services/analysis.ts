import { api } from './api';
import { addToast } from '$lib/stores/toast';
import { config } from '$lib/config';
import type { AnalysisResponse, HistoryResponse, QueueSubmissionResponse, AnalysisStatusResponse } from '$lib/types';

export async function analyzeXRay(file: File, name: string): Promise<QueueSubmissionResponse | null> {
	try {
		addToast({
			type: 'info',
			title: 'Submitting X-ray for analysis',
			message: 'Your X-ray is being added to the analysis queue...'
		});
		
		const result = await api.upload<QueueSubmissionResponse>('/analyze/xray', file, { name });
		
		if (result.success) {
			addToast({
				type: 'success',
				title: 'X-ray submitted to queue',
				message: `Position in queue: ${result.queue_position ?? 1}. Estimated wait time: ${Math.round((result.estimated_wait_time ?? 30) / 60)} minutes`
			});
		}
		
		return result;
	} catch (error: any) {
		// Handle rate limiting
		if (error?.status === 429) {
			addToast({
				type: 'warning',
				title: 'Rate limit exceeded',
				message: error.detail?.message || 'Please wait before submitting another analysis',
				duration: 5000
			});
			return {
				success: false,
				error: 'rate_limited',
				message: error.detail?.message || 'Rate limit exceeded',
				wait_time: error.detail?.wait_time || config.analysis.statusPollInterval / 1000
			} as QueueSubmissionResponse;
		}
		
		addToast({
			type: 'error',
			title: 'Submission failed',
			message: error instanceof Error ? error.message : 'Failed to submit X-ray for analysis'
		});
		return null;
	}
}

export async function analyzeCTScan(file: File, name: string): Promise<QueueSubmissionResponse | null> {
	try {
		addToast({
			type: 'info',
			title: 'Submitting CT scan for analysis',
			message: 'Your CT scan is being added to the analysis queue...'
		});
		
		const result = await api.upload<QueueSubmissionResponse>('/analyze/ct', file, { name });
		
		if (result.success) {
			let toast_est_time = '';
			if (result.estimated_wait_time && result.queue_position){
				toast_est_time = `Position in queue: ${result.queue_position}. Estimated wait time: ${Math.round(result.estimated_wait_time / 60)} minutes`;
			}
			addToast({
				type: 'success',
				title: 'CT scan submitted to queue',
				message: `${toast_est_time}`
			});
		}
		
		return result;
	} catch (error: any) {
		// Handle rate limiting
		if (error?.status === 429) {
			addToast({
				type: 'warning',
				title: 'Rate limit exceeded',
				message: error.detail?.message || 'Please wait before submitting another analysis',
				duration: 5000
			});
			return {
				success: false,
				error: 'rate_limited',
				message: error.detail?.message || 'Rate limit exceeded',
				wait_time: error.detail?.wait_time || config.analysis.statusPollInterval / 1000
			} as QueueSubmissionResponse;
		}
		
		addToast({
			type: 'error',
			title: 'Submission failed',
			message: error instanceof Error ? error.message : 'Failed to submit CT scan for analysis'
		});
		return null;
	}
}

export async function getAnalysisHistory(page: number = 1, pageSize: number = 10): Promise<HistoryResponse | null> {
	try {
		const result = await api.get<HistoryResponse>(`/auth/history?page=${page}&page_size=${pageSize}`);
		return result;
	} catch (error) {
		addToast({
			type: 'error',
			title: 'Failed to load history',
			message: error instanceof Error ? error.message : 'Could not fetch analysis history'
		});
		return null;
	}
}

export async function deleteHistoryItem(historyId: number): Promise<boolean> {
	try {
		await api.delete(`/auth/history/${historyId}`);
		
		addToast({
			type: 'success',
			title: 'Item deleted',
			message: 'History item deleted successfully'
		});
		
		return true;
	} catch (error) {
		addToast({
			type: 'error',
			title: 'Delete failed',
			message: error instanceof Error ? error.message : 'Failed to delete history item'
		});
		return false;
	}
}

export async function getAnalysisStatus(historyId: number): Promise<AnalysisStatusResponse | null> {
	try {
		const result = await api.get<AnalysisStatusResponse>(`/analyze/status/${historyId}`);
		return result;
	} catch (error) {
		addToast({
			type: 'error',
			title: 'Status check failed',
			message: error instanceof Error ? error.message : 'Could not fetch analysis status'
		});
		return null;
	}
}
