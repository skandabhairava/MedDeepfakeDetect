import { api } from './api';
import { addToast } from '$lib/stores/toast';
import type { AnalysisResponse, HistoryResponse } from '$lib/types';

export async function analyzeXRay(file: File, name: string): Promise<AnalysisResponse | null> {
	try {
		addToast({
			type: 'info',
			title: 'Analyzing X-ray',
			message: 'Processing your knee X-ray image...'
		});
		
		const result = await api.upload<AnalysisResponse>('/analyze/xray', file, { name });
		
		addToast({
			type: 'success',
			title: 'Analysis complete',
			message: 'X-ray analysis completed successfully'
		});
		
		return result;
	} catch (error) {
		addToast({
			type: 'error',
			title: 'Analysis failed',
			message: error instanceof Error ? error.message : 'Failed to analyze X-ray'
		});
		return null;
	}
}

export async function analyzeCTScan(file: File, name: string): Promise<AnalysisResponse | null> {
	try {
		addToast({
			type: 'info',
			title: 'Analyzing CT scan',
			message: 'Processing your CT scan image...'
		});
		
		const result = await api.upload<AnalysisResponse>('/analyze/ct', file, { name });
		
		addToast({
			type: 'success',
			title: 'Analysis complete',
			message: 'CT scan analysis completed successfully'
		});
		
		return result;
	} catch (error) {
		addToast({
			type: 'error',
			title: 'Analysis failed',
			message: error instanceof Error ? error.message : 'Failed to analyze CT scan'
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
