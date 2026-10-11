import { writable } from 'svelte/store';

export const showStudyConsentModal = writable(false);

export function openStudyConsentModal() {
    showStudyConsentModal.set(true);
}

export function closeStudyConsentModal() {
    showStudyConsentModal.set(false);
}