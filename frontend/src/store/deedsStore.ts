import { create } from 'zustand';
import api from '../api/client';
import type { GoodDeed } from '../types';

interface DeedsState {
    deeds: GoodDeed[];
    isLoading: boolean;
    fetchDeeds: (filters?: { child_id?: number; completed?: boolean }) => Promise<void>;
    createDeed: (childId: number, description: string) => Promise<GoodDeed>;
    completeDeed: (id: number, note?: string) => Promise<void>;
    deleteDeed: (id: number) => Promise<void>;
}

export const useDeedsStore = create<DeedsState>((set) => ({
    deeds: [],
    isLoading: false,

    fetchDeeds: async (filters) => {
        set({ isLoading: true });
        try {
            const params = new URLSearchParams();
            if (filters?.child_id) params.append('child_id', filters.child_id.toString());
            if (filters?.completed !== undefined) params.append('completed', filters.completed.toString());

            const response = await api.get<GoodDeed[]>(`/deeds?${params.toString()}`);
            set({ deeds: response.data, isLoading: false });
        } catch {
            set({ isLoading: false });
        }
    },

    createDeed: async (childId, description) => {
        const response = await api.post<GoodDeed>('/deeds', { child_id: childId, description });
        set((state) => ({ deeds: [response.data, ...state.deeds] }));
        return response.data;
    },

    completeDeed: async (id, note) => {
        const response = await api.post<GoodDeed>(`/deeds/${id}/complete`, { parent_note: note });
        set((state) => ({
            deeds: state.deeds.map((deed) => deed.id === id ? response.data : deed),
        }));
    },

    deleteDeed: async (id) => {
        await api.delete(`/deeds/${id}`);
        set((state) => ({
            deeds: state.deeds.filter((deed) => deed.id !== id),
        }));
    },
}));
