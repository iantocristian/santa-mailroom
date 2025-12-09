import { create } from 'zustand';
import api from '../api/client';
import type { FamilyState, Family, FamilyStats } from '../types';

export const useFamilyStore = create<FamilyState>((set) => ({
    family: null,
    stats: null,
    isLoading: false,

    fetchFamily: async () => {
        set({ isLoading: true });
        try {
            const response = await api.get<Family>('/family');
            set({ family: response.data, isLoading: false });
        } catch (error: unknown) {
            // Family might not exist yet
            const err = error as { response?: { status?: number } };
            if (err.response?.status === 404) {
                set({ family: null, isLoading: false });
            } else {
                set({ isLoading: false });
                throw error;
            }
        }
    },

    createFamily: async (name?: string) => {
        set({ isLoading: true });
        try {
            const response = await api.post<Family>('/family', { name });
            set({ family: response.data, isLoading: false });
        } catch (error) {
            set({ isLoading: false });
            throw error;
        }
    },

    updateFamily: async (updates: Partial<Family>) => {
        const response = await api.put<Family>('/family', updates);
        set({ family: response.data });
    },

    fetchStats: async () => {
        try {
            const response = await api.get<FamilyStats>('/family/stats');
            set({ stats: response.data });
        } catch (error) {
            console.error('Error fetching stats:', error);
        }
    },
}));
