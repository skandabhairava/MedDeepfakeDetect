export interface User {
	id: number;
	account_name: string;
	email: string;
	is_admin: boolean;
	created_at: string;
}

export interface AuthResponse {
	access_token: string;
	token_type: string;
	expires_in: number;
}

export interface LoginCredentials {
	email: string;
	password: string;
}

export interface UserCreate {
	account_name: string;
	email: string;
	password: string;
	is_admin: boolean;
}

export interface PasswordChange {
	current_password: string;
	new_password: string;
}

export interface AnalysisResponse {
	request_id: string;
	model_name: string;
	status: string;
	inference_time: number;
	device: string;
	authenticity: {
		is_real: boolean;
		confidence: number;
		prediction: string;
	};
	arthritis?: {
		severity: string;
		confidence: number;
		classification: string;
	};
	scan_type?: string;
	gradcam?: string; // Base64 encoded GradCAM image
	error?: string;
}

export interface AnalysisHistory {
	id: number;
	analysis_type: string;
	filename: string;
	name: string;
	image_base64?: string;
	results: AnalysisResponse;
	timestamp: string;
	confidence?: number;
}

export interface HistoryResponse {
	history: AnalysisHistory[];
	total: number;
	page: number;
	page_size: number;
	has_more: boolean;
}

export interface ApiResponse<T> {
	data?: T;
	error?: string;
	message?: string;
}

export interface QueueSubmissionResponse {
	success: boolean;
	message: string;
	history_id: number;
	status: string;
	queue_position: number;
	estimated_wait_time: number;
}

export interface AnalysisStatusResponse {
	success: boolean;
	status: {
		id: number;
		status: string;
		queue_position?: number;
		processing_started?: string;
		processing_completed?: string;
		results?: AnalysisResponse;
		confidence?: number;
		queue_stats?: {
			pending_count: number;
			queue_capacity: number;
			worker_threads: number;
			queue_utilization: number;
		};
	};
}
