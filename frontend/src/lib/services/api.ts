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

/**
 * Force the user out of the session.
 *
 * Imported lazily (inside the function) to break the circular dependency
 * between api.ts ← services/auth.ts ← api.ts.  We also accept an optional
 * reason string that is shown in a toast before redirecting to /login.
 */
async function forceLogout(reason: string): Promise<void> {
	// Lazy import avoids circular-dependency at module load time
	const { logout } = await import('$lib/services/auth');
	const { addToast } = await import('$lib/stores/toast');

	addToast({
		type: 'warning',
		title: 'Session expired',
		message: reason,
	});

	await logout();
}

async function apiRequest<T>(
	endpoint: string,
	options: RequestInit = {}
): Promise<T> {
	const url = `${API_BASE_URL}${endpoint}`;
	
	const defaultHeaders: Record<string, string> = {
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
		// ----------------------------------------------------------------
		// Forced logout cases
		// ----------------------------------------------------------------

		if (response.status === 401) {
			const errorCode = data?.detail?.error_code ?? data?.error_code;

			if (errorCode === 'encryption_key_expired') {
				// Session key evicted from server memory — re-login required
				// to re-derive the AES key from the user's password.
				forceLogout(
					'Your session encryption key has expired. Please log in again to access your encrypted data.'
				);
				// Still throw so any awaiting call-site can bail out cleanly
				throw new ApiError('encryption_key_expired', 401, data);
			}

			// Generic 401 — JWT invalid or expired
			if (localStorage.getItem('auth_token')) {
				forceLogout('Your session has expired. Please log in again.');
				throw new ApiError(
					data?.detail || data?.message || 'Unauthorized',
					401,
					data
				);
			}
		}

		throw new ApiError(
			data?.detail?.message || data?.detail || data?.message || `HTTP ${response.status}`,
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
	upload: async <T>(endpoint: string, file: File, additionalData?: Record<string, string>): Promise<T> => {
		const url = `${API_BASE_URL}${endpoint}`;
		const token = localStorage.getItem('auth_token');
		
		const formData = new FormData();
		formData.append('file', file);
		
		// Add additional form data if provided
		if (additionalData) {
			for (const [key, value] of Object.entries(additionalData)) {
				formData.append(key, value);
			}
		}
		
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
			if (response.status === 401) {
				// ----------------------------------------------------------------
				// Forced logout cases
				// ----------------------------------------------------------------
				const errorCode = data?.detail?.error_code ?? data?.error_code;

				if (errorCode === 'encryption_key_expired') {
					// Session key evicted from server memory — re-login required
					// to re-derive the AES key from the user's password.
					forceLogout(
						'Your session encryption key has expired. Please log in again to access your encrypted data.'
					);
					// Still throw so any awaiting call-site can bail out cleanly
					throw new ApiError('encryption_key_expired', 401, data);
				}

				// Generic 401 — JWT invalid or expired
				if (localStorage.getItem('auth_token')) {
					forceLogout('Your session has expired. Please log in again.');
					throw new ApiError(
						data?.detail || data?.message || 'Unauthorized',
						401,
						data
					);
				}
			}

			throw new ApiError(
				data?.detail?.message || data?.detail || data?.message || `HTTP ${response.status}`,
				response.status,
				data
			);
		}
		
		return data;
	},
};

export { ApiError };

