import { create } from 'zustand';
import api from '../api/client';
import type { NotificationsState, Notification } from '../types';

export const useNotificationsStore = create<NotificationsState>((set) => ({
    notifications: [],
    unreadCount: 0,
    isLoading: false,

    fetchNotifications: async (unreadOnly = false) => {
        set({ isLoading: true });
        try {
            const response = await api.get<Notification[]>('/notifications', {
                params: { unread_only: unreadOnly },
            });
            set({ notifications: response.data, isLoading: false });
        } catch (error) {
            set({ isLoading: false });
            throw error;
        }
    },

    fetchUnreadCount: async () => {
        try {
            const response = await api.get<{ unread_count: number }>('/notifications/count');
            set({ unreadCount: response.data.unread_count });
        } catch (error) {
            console.error('Error fetching notification count:', error);
        }
    },

    markAsRead: async (id: number) => {
        await api.put(`/notifications/${id}/read`);
        set((state) => ({
            notifications: state.notifications.map((n) =>
                n.id === id ? { ...n, read: true } : n
            ),
            unreadCount: Math.max(0, state.unreadCount - 1),
        }));
    },

    markAllAsRead: async () => {
        await api.post('/notifications/read-all');
        set((state) => ({
            notifications: state.notifications.map((n) => ({ ...n, read: true })),
            unreadCount: 0,
        }));
    },
}));
