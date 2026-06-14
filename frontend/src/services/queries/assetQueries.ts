import { useQuery } from '@tanstack/react-query';
import { getAssetsBySearch } from '../api/assetService';

export const useAssetSearch = (query: string) => {
  return useQuery({
    queryKey: ['assets', query], 
    queryFn: () => getAssetsBySearch(query),
    enabled: query.length >= 2,
    staleTime: 1000 * 60 * 5,
  });
};