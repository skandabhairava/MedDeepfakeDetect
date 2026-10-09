import { api } from './api';
import { user, isAuthenticated, token } from '$lib/stores/auth';
import { addToast } from '$lib/stores/toast';
import type { User, AuthResponse, LoginCredentials, UserCreate, PasswordChange } from '$lib/types';
import { goto } from '$app/navigation';

export async function login(credentials: LoginCredentials): Promise<boolean> {
	try {
		const response = await api.post<AuthResponse>('/auth/login', credentials);
		
		// Store token
		localStorage.setItem('auth_token', response.access_token);
		token.set(response.access_token);
		
		// Get user info
		const userInfo = await getCurrentUser();
		if (userInfo) {
			isAuthenticated.set(true);
			addToast({
				type: 'success',
				title: 'Login successful',
				message: `Welcome back, ${userInfo.account_name}!`
			});
			return true;
		}
		
		return false;
	} catch (error) {
		addToast({
			type: 'error',
			title: 'Login failed',
			message: error instanceof Error ? error.message : 'Invalid credentials'
		});
		return false;
	}
}

export async function logout(): Promise<void> {
	try {
		localStorage.removeItem('auth_token');
		token.set(null);
		user.set(null);
		isAuthenticated.set(false);
		
		addToast({
			type: 'info',
			title: 'Logged out',
			message: 'You have been successfully logged out'
		});

		goto('/');
	} catch (error) {
		console.error('Logout error:', error);
	}
}

export async function getCurrentUser(): Promise<User | null> {
	try {
		const userInfo = await api.get<User>('/auth/me');
		user.set(userInfo);
		return userInfo;
	} catch (error) {
		// Token might be invalid, clear it
		localStorage.removeItem('auth_token');
		token.set(null);
		user.set(null);
		isAuthenticated.set(false);
		return null;
	}
}

export async function checkAuth(): Promise<void> {
	const storedToken = localStorage.getItem('auth_token');
	if (!storedToken) {
		isAuthenticated.set(false);
		return;
	}
	
	token.set(storedToken);
	const userInfo = await getCurrentUser();
	if (userInfo) {
		isAuthenticated.set(true);
	} else {
		isAuthenticated.set(false);
	}
}

export async function createUser(userData: UserCreate): Promise<boolean> {
	try {
		await api.post<User>('/auth/register', userData);
		
		addToast({
			type: 'success',
			title: 'User created',
			message: `User ${userData.account_name} has been created successfully`
		});
		return true;
	} catch (error) {
		addToast({
			type: 'error',
			title: 'Failed to create user',
			message: error instanceof Error ? error.message : 'Unknown error'
		});
		return false;
	}
}

export async function changePassword(passwordData: PasswordChange): Promise<boolean> {
	try {
		await api.post('/auth/change-password', passwordData);
		
		addToast({
			type: 'success',
			title: 'Password changed',
			message: 'Your password has been updated successfully'
		});
		return true;
	} catch (error) {
		addToast({
			type: 'error',
			title: 'Failed to change password',
			message: error instanceof Error ? error.message : 'Current password may be incorrect'
		});
		return false;
	}
}

export async function listUsers(): Promise<User[]> {
	try {
		return await api.get<User[]>('/auth/users');
	} catch (error) {
		addToast({
			type: 'error',
			title: 'Failed to load users',
			message: error instanceof Error ? error.message : 'Could not fetch user list'
		});
		return [];
	}
}

export async function deleteUser(userId: number): Promise<boolean> {
	try {
		await api.delete(`/auth/users/${userId}`);
		addToast({
			type: 'success',
			title: 'User deleted',
			message: 'User account has been deleted successfully'
		});
		return true;
	} catch (error) {
		addToast({
			type: 'error',
			title: 'Failed to delete user',
			message: error instanceof Error ? error.message : 'Could not delete user account'
		});
		return false;
	}
}

export async function deleteCurrentAccount(): Promise<boolean> {
	try {
		await api.delete('/auth/me');
		localStorage.removeItem('auth_token');
		token.set(null);
		user.set(null);
		isAuthenticated.set(false);

		addToast({
			type: 'info',
			title: 'Account deleted',
			message: 'Your account and all associated data have been permanently deleted.'
		});

		goto('/login');
		return true;
	} catch (error) {
		addToast({
			type: 'error',
			title: 'Account deletion failed',
			message: error instanceof Error ? error.message : 'Could not delete your account'
		});
		return false;
	}
}
export async function acceptStudyConsent(): Promise<boolean> {
	try {
		const updatedUser = await api.post<User>('/auth/study-consent', {});
		user.set(updatedUser);
		return true;
	} catch (error) {
		addToast({
			type: 'error',
			title: 'Consent recording failed',
			message: error instanceof Error ? error.message : 'Could not record study agreement. Please try again.'
		});
		return false;
	}
}
