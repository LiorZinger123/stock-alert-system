import { useQuery } from '@tanstack/react-query';
import { getAssetsBySearch, getAssetDetails } from '../api/assetService';

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