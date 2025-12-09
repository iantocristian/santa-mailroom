import { create } from 'zustand';
import api from '../api/client';
import type { WishItem, WishlistState } from '../types';

export const useWishlistStore = create<WishlistState>((set) => ({
    items: [],
    isLoading: false,

    fetchItems: async (filters?: { child_id?: number; status?: string; year?: number }) => {
        set({ isLoading: true });
        try {
            const params = new URLSearchParams();
            if (filters?.child_id) params.append('child_id', filters.child_id.toString());
            if (filters?.status) params.append('status', filters.status);
            if (filters?.year) params.append('year', filters.year.toString());

            const response = await api.get<WishItem[]>(`/wishlist?${params.toString()}`);
            set({ items: response.data, isLoading: false });
        } catch {
            set({ isLoading: false });
        }
    },

    updateItem: async (id: number, updates: Partial<WishItem>) => {
        const response = await api.put<WishItem>(`/wishlist/${id}`, updates);
        set((state) => ({
            items: state.items.map((item) =>
                item.id === id ? response.data : item
            ),
        }));
    },
}));
