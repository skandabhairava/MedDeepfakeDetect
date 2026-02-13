import { api } from './api';
import { addToast } from '$lib/stores/toast';
import type { AnalysisResponse, HistoryResponse } from '$lib/types';

export async function analyzeXRay(file: File): Promise<AnalysisResponse | null> {
	try {
		addToast({
			type: 'info',
			title: 'Analyzing X-ray',
			message: 'Processing your knee X-ray image...'
		});
		
		const result = await api.upload<AnalysisResponse>('/analyze/xray', file);
		
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

export async function analyzeCTScan(file: File): Promise<AnalysisResponse | null> {
	try {
		addToast({
			type: 'info',
			title: 'Analyzing CT scan',
			message: 'Processing your CT scan image...'
		});
		
		const result = await api.upload<AnalysisResponse>('/analyze/ct', file);
		
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
