import { useMutation, useQuery } from '@tanstack/react-query';
import { queryClient } from '../../lib/queryClient';
import type { CreateNewAlertData, UpdateAlertFormData } from '../../utils/interfaces';
import { createNewAlert, deleteUserAlert, getUserAlerts, updateUserAlert } from '../api/alertsService';

export const alertKeys = {
  all: ['alerts'] as const,
  lists: () => [...alertKeys.all, 'list'] as const,
};

export const useGetAlerts = () => {
  return useQuery({
    queryKey: alertKeys.lists(),
    queryFn: getUserAlerts,
    staleTime: 1000 * 60,
    refetchInterval: 1000 * 30,
  });
};

export const useCreateAlert = () => {
  return useMutation({
    mutationFn: (data: CreateNewAlertData) => createNewAlert(data),

    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: alertKeys.lists() });
    },
  });
};

export const useUpdateAlert = () => {
  return useMutation({
    mutationFn: ({ alertId, data }: {alertId: number, data: UpdateAlertFormData}) =>
      updateUserAlert(alertId, data),

    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: alertKeys.lists(),
      });
    },
  });
};

export const useDeleteAlert = () => {
  return useMutation({
    mutationFn: deleteUserAlert,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: alertKeys.lists() });
    },
  });
};