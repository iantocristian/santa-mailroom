import { create } from 'zustand';
import api from '../api/client';
import type { ChildrenState, Child, ChildCreate } from '../types';

export const useChildrenStore = create<ChildrenState>((set) => ({
    children: [],
    isLoading: false,

    fetchChildren: async () => {
        set({ isLoading: true });
        try {
            const response = await api.get<Child[]>('/children');
            set({ children: response.data, isLoading: false });
        } catch (error) {
            set({ isLoading: false });
            throw error;
        }
    },

    addChild: async (data: ChildCreate) => {
        const response = await api.post<Child>('/children', data);
        set((state) => ({ children: [...state.children, response.data] }));
        return response.data;
    },

    updateChild: async (id: number, updates: Partial<Child>) => {
        const response = await api.put<Child>(`/children/${id}`, updates);
        set((state) => ({
            children: state.children.map((c) => (c.id === id ? response.data : c)),
        }));
    },

    deleteChild: async (id: number) => {
        await api.delete(`/children/${id}`);
        set((state) => ({
            children: state.children.filter((c) => c.id !== id),
        }));
    },
}));
