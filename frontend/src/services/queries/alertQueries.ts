import { useMutation, useInfiniteQuery, type InfiniteData } from '@tanstack/react-query';
import { queryClient } from '../../lib/queryClient';
import type { CreateNewAlertData, UpdateAlertFormData, Alert, AlertStatus } from '../../utils/interfaces';
import { createNewAlert, deleteUserAlert, fetchAlertsPaginated, updateUserAlert } from '../api/alertsService';

export const alertKeys = {
  all: ['alerts'] as const,
  lists: () => [...alertKeys.all, 'list'] as const,
};

export const useInfiniteAlerts = () => {
  return useInfiniteQuery({
    queryKey: alertKeys.lists(),
    queryFn: ({ pageParam }) => fetchAlertsPaginated(pageParam as number),
    getNextPageParam: (lastPage, allPages) =>
      lastPage.length === 5 ? allPages.length * 5 : undefined,
    initialPageParam: 0,
  });
};

export const useCreateAlert = () => {
  return useMutation({
    mutationFn: (data: CreateNewAlertData) => createNewAlert(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: alertKeys.lists() });
      queryClient.invalidateQueries({ queryKey: ['assetDetails'] });
    },
  });
};

export const useUpdateAlert = () => {
  return useMutation({
    mutationFn: ({ alertId, data }: { alertId: number; data: UpdateAlertFormData }) =>
      updateUserAlert(alertId, data),
    onSuccess: (updatedAlert: Alert) => {
      queryClient.setQueryData(alertKeys.lists(), (oldData: InfiniteData<Alert[]>) => {
        if (!oldData) return;
        return {
          ...oldData,
          pages: oldData.pages.map((page: Alert[]) =>
            page.map((alert) => (alert.id === updatedAlert.id ? updatedAlert : alert))
          ),
        };
      });
      queryClient.invalidateQueries({ queryKey: ['assetDetails'] });
    },
  });
};

export const useDeleteAlert = () => {
  return useMutation({
    mutationFn: deleteUserAlert,
    onSuccess: (_, alertId: number) => {
      queryClient.setQueryData(alertKeys.lists(), (oldData: InfiniteData<Alert[]>) => {
        if (!oldData) return;
        return {
          ...oldData,
          pages: oldData.pages.map((page: Alert[]) =>
            page.filter((alert) => alert.id !== alertId)
          ),
        };
      });
      queryClient.invalidateQueries({ queryKey: ['assetDetails'] });
    },
  });
};

export const updateAlertInCache = (alertId: number, newStatus: AlertStatus) => {
  queryClient.setQueryData<InfiniteData<Alert[]>>(alertKeys.lists(), (oldData) => {
    if (!oldData) return;

    return {
      ...oldData,
      pages: oldData.pages.map((page: Alert[]) =>
        page.map((alert) => 
          alert.id === alertId 
            ? { ...alert, status: newStatus }
            : alert
        )
      ),
    };
  });
};
