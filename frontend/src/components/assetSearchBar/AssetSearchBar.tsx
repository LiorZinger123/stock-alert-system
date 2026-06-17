import React, { useEffect, useState } from "react";
import type { ControllerRenderProps } from "react-hook-form";
import { useAssetSearch } from "../../services/queries/assetQueries";
import type { NewAlertFormValues, SearchedAsset } from "../../utils/interfaces";
import { CustomAutocomplete, CustomTextField } from "../../shared/MuiComponents";

interface AssetSearchBarProps {
    field?: ControllerRenderProps<NewAlertFormValues, "asset">;
    value?: SearchedAsset | null;
    onChange?: (value: SearchedAsset | null) => void;
    label?: string;
}

const AssetSearchBar = ({ field, value, onChange, label }: AssetSearchBarProps) => {
    const currentValue = field?.value ?? value ?? null;
    const [inputValue, setInputValue] = useState('');
    const [debouncedQuery, setDebouncedQuery] = useState('');
    const { data: assets, isLoading } = useAssetSearch(debouncedQuery);

    const handleSelectionChange = (
        _event: React.SyntheticEvent,
        newValue: SearchedAsset | null
    ) => {
        if (field?.onChange) {
            field.onChange(newValue);
        } else if (onChange) {
            onChange(newValue);
        }
    };

    const handleInputChange = (
        _event: React.SyntheticEvent,
        newInputValue: string,
        reason: string
    ) => {
        setInputValue(newInputValue);
        if (reason === 'clear') {
            handleSelectionChange(_event, null);
        }
    };

    useEffect(() => {
        const t = setTimeout(() => setDebouncedQuery(inputValue), 300);
        return () => clearTimeout(t);
    }, [inputValue]);

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
                option ? `${option.name} (${option.symbol})` : ''
            }
            isOptionEqualToValue={(option, val) => option.symbol === val.symbol}
            renderInput={(params) => (
                <CustomTextField {...params} label={label ?? "Search Asset"} />
            )}
        />
    );
};

export default AssetSearchBar;