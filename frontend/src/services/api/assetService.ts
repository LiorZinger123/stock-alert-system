import api from "./api";
import type { AssetDetails, SearchedAsset } from "../../utils/interfaces";

export const getAssetsBySearch = async (query: string): Promise<SearchedAsset[]> => {
  const res = await api.get(`/assets/search?query=${query}`);
  return res.data?.results ?? [];
};

export const getAssetDetails = async (symbol: string, name?: string): Promise<AssetDetails> => {
  const res = await api.post(`assets/${symbol}`, { name });
  return res.data;
};

export const getAssetPrice = async (symbol: string): Promise<number> => {
  const res = await api.get(`/assets/${symbol}/price`);
  return res.data?.price;
};