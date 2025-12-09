import { create } from 'zustand';
import api from '../api/client';
import type { Letter, LettersState } from '../types';

export const useLettersStore = create<LettersState>((set) => ({
    letters: [],
    isLoading: false,

    fetchLetters: async (filters?: { child_id?: number; year?: number }) => {
        set({ isLoading: true });
        try {
            const params = new URLSearchParams();
            if (filters?.child_id) params.append('child_id', filters.child_id.toString());
            if (filters?.year) params.append('year', filters.year.toString());

            const response = await api.get<Letter[]>(`/letters?${params.toString()}`);
            set({ letters: response.data, isLoading: false });
        } catch {
            set({ isLoading: false });
        }
    },

    fetchLetter: async (id: number) => {
        const response = await api.get<Letter>(`/letters/${id}`);
        return response.data;
    },
}));
