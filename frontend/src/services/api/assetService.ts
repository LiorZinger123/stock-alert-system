import type { SearchedAsset } from "../../utils/interfaces";
import api from "./api";

export const getAssetsBySearch = async (query: string): Promise<SearchedAsset[]> => {
  const res = await api.get(`/assets/search?query=${query}`);
  return res.data?.results ?? [];
};