import React, { useState } from "react";
import type { ControllerRenderProps } from "react-hook-form";
import { useAssetSearch } from "../../services/queries/assetQueries";
import type { NewAlertFormValues, SearchedAsset } from "../../utils/interfaces";
import {
  CustomAutocomplete,
  CustomTextField,
} from "../../shared/MuiComponents";

interface AssetSearchBarProps {
  label?: string;
  value?: SearchedAsset | null;
  field?: ControllerRenderProps<NewAlertFormValues, "asset">;
  onChange?: (value: SearchedAsset | null) => void;
}

const AssetSearchBar = ({
  field,
  value,
  onChange,
  label,
}: AssetSearchBarProps) => {
  const currentValue: SearchedAsset | null = field?.value ?? value ?? null;
  const [inputValue, setInputValue] = useState<string>("");
  const [debouncedQuery, setDebouncedQuery] = useState<string>("");
  const { data: assets, isLoading } = useAssetSearch(debouncedQuery);

  const handleSelectionChange = (
    _event: React.SyntheticEvent,
    newValue: SearchedAsset | null,
  ): void => {
    if (field?.onChange) {
      field.onChange(newValue);
    } else if (onChange) {
      onChange(newValue);
    }
  };

  const handleInputChange = (
    _event: React.SyntheticEvent,
    newInputValue: string,
    reason: string,
  ): (() => void) | undefined => {
    setInputValue(newInputValue);

    if (reason === "clear") {
      handleSelectionChange(_event, null);
    }
    if (reason === "reset") return;

    const t = setTimeout(() => setDebouncedQuery(newInputValue), 300);
    return () => clearTimeout(t);
  };

  return (
    <CustomAutocomplete
      value={currentValue}
      inputValue={inputValue}
      onInputChange={handleInputChange}
      onChange={handleSelectionChange}
      options={assets || []}
      loading={isLoading}
      fullWidth
      getOptionLabel={(option) =>
        option ? `${option.name} (${option.symbol})` : ""
      }
      isOptionEqualToValue={(option, val) => option.symbol === val.symbol}
      renderInput={(params) => (
        <CustomTextField {...params} label={label ?? "Search Asset"} />
      )}
    />
  );
};

export default AssetSearchBar;
