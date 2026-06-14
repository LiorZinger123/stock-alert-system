import { useEffect, useState } from "react"
import type { ControllerRenderProps } from "react-hook-form";
import { useAssetSearch } from "../../services/queries/assetQueries";
import { CustomAutocomplete, CustomTextField } from "../../shared/MuiComponents";
import type { NewAlertFormValues, NewAlertFromAsset } from "../../utils/interfaces";

interface AssetSearchBarProps {
    field?: ControllerRenderProps<NewAlertFormValues, "asset">;
    value?: NewAlertFromAsset | null;
    onChange?: (value: NewAlertFromAsset | null) => void;
    label?: string;
}

const AssetSearchBar = ({ field, value, onChange, label }: AssetSearchBarProps) => {
    const [inputValue, setInputValue] = useState('');
    const [debouncedQuery, setDebouncedQuery] = useState('');
    const { data: assets, isLoading } = useAssetSearch(debouncedQuery);

    const handleChange = (_: any, value: any) => {
        if (field?.onChange) {
            field.onChange(value);
        } else if (onChange) {
            onChange(value);
        }
    }

    useEffect(() => {
        const t = setTimeout(() => setDebouncedQuery(inputValue), 300);
        return () => clearTimeout(t);
    }, [inputValue]);

    return (
        <CustomAutocomplete
            value={field?.value !== undefined ? field.value : (value ?? null)}
            inputValue={inputValue}
            onInputChange={(_, v) => setInputValue(v)}
            options={assets || []}
            loading={isLoading}
            fullWidth
            getOptionLabel={(option: any) =>
                option ? `${option.name} (${option.symbol})` : ''
            }
            isOptionEqualToValue={(option, value) =>
                option?.symbol === value?.symbol
            }
            onChange={handleChange}
            renderInput={(params) => (
                <CustomTextField {...params} label={label ?? "Search Asset"} />
            )}
        />
    )
}

export default AssetSearchBar
