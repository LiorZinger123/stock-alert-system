import { useQuery } from '@tanstack/react-query';
import { getAssetsBySearch, getAssetDetails, getAssetPrice } from '../api/assetService';

export const useAssetSearch = (query: string) => {
  return useQuery({
    queryKey: ['assets', query], 
    queryFn: () => getAssetsBySearch(query),
    enabled: query.length >= 2,
    staleTime: 1000 * 60 * 5,
  });
};

export const useAssetDetails = (symbol?: string, name?: string) => {
  return useQuery({
    queryKey: ['assetDetails', symbol],
    queryFn: () => getAssetDetails(symbol!, name),
    enabled: !!symbol,
    staleTime: 1000 * 60 * 60,
  });
};

export const useAssetPrice = (symbol?: string, isAssetLoaded?: boolean) => {
  return useQuery({
    queryKey: ['assetPrice', symbol],
    queryFn: () => getAssetPrice(symbol!),
    enabled: !!symbol && !!isAssetLoaded,
    staleTime: 1000 * 30,
    refetchInterval: 1000 * 60,
  });
};