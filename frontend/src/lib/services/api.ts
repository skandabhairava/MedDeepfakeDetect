const API_BASE_URL = import.meta.env.VITE_API_URL || '';

class ApiError extends Error {
	constructor(
		message: string,
		public status: number,
		public data?: any
	) {
		super(message);
		this.name = 'ApiError';
	}
}

async function apiRequest<T>(
	endpoint: string,
	options: RequestInit = {}
): Promise<T> {
	const url = `${API_BASE_URL}${endpoint}`;
	
	const defaultHeaders = {
		'Content-Type': 'application/json',
	};
	
	// Add auth token if available
	const token = localStorage.getItem('auth_token');
	if (token) {
		defaultHeaders['Authorization'] = `Bearer ${token}`;
	}
	
	const response = await fetch(url, {
		...options,
		headers: {
			...defaultHeaders,
			...options.headers,
		},
	});
	
	const data = await response.json().catch(() => null);
	
	if (!response.ok) {
		throw new ApiError(
			data?.detail || data?.message || `HTTP ${response.status}`,
			response.status,
			data
		);
	}
	
	return data;
}

export const api = {
	get: <T>(endpoint: string) => apiRequest<T>(endpoint, { method: 'GET' }),
	post: <T>(endpoint: string, body?: any) =>
		apiRequest<T>(endpoint, {
			method: 'POST',
			body: body ? JSON.stringify(body) : undefined,
		}),
	put: <T>(endpoint: string, body?: any) =>
		apiRequest<T>(endpoint, {
			method: 'PUT',
			body: body ? JSON.stringify(body) : undefined,
		}),
	delete: <T>(endpoint: string) => apiRequest<T>(endpoint, { method: 'DELETE' }),
	upload: async <T>(endpoint: string, file: File): Promise<T> => {
		const url = `${API_BASE_URL}${endpoint}`;
		const token = localStorage.getItem('auth_token');
		
		const formData = new FormData();
		formData.append('file', file);
		
		const headers: Record<string, string> = {};
		if (token) {
			headers['Authorization'] = `Bearer ${token}`;
		}
		
		const response = await fetch(url, {
			method: 'POST',
			headers,
			body: formData,
		});
		
		const data = await response.json().catch(() => null);
		
		if (!response.ok) {
			throw new ApiError(
				data?.detail || data?.message || `HTTP ${response.status}`,
				response.status,
				data
			);
		}
		
		return data;
	},
};

export { ApiError };
