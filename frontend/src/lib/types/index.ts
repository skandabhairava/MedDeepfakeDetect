export interface User {
	id: number;
	account_name: string;
	email: string;
	is_admin: boolean;
	created_at: string;
	last_login?: string;
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
		is_authentic: boolean;
		confidence: number;
		prediction: string;
	};
	arthritis?: {
		severity: string;
		confidence: number;
		classification: string;
	};
	scan_type?: string;
	analysis_notes?: string;
	gradcam?: string; // Base64 encoded GradCAM image
	error?: string;
}

export interface AnalysisHistory {
	id: number;
	analysis_type: string;
	filename: string;
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
