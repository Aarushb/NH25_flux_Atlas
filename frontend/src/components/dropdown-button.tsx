import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuPortal,
  DropdownMenuSeparator,
  DropdownMenuShortcut,
  DropdownMenuSub,
  DropdownMenuSubContent,
  DropdownMenuSubTrigger,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

type DropDownProps = {
  value: string;
  setValue: React.Dispatch<React.SetStateAction<string>>;
  values: string[];
  itemsWithIndicator?: Set<string>;
  indicatorColor?: string;
  indicatorLabel?: string;
};

export function DropdownMenuDemo({
  value,
  setValue,
  values,
  itemsWithIndicator,
  indicatorColor = "bg-green-500",
  indicatorLabel = "Active",
}: DropDownProps) {
  const hasIndicator = itemsWithIndicator && itemsWithIndicator.has(value);

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="outline"
          className="flex items-center gap-2 min-w-[180px] justify-between px-4"
        >
          <span className="truncate">{value}</span>
          {hasIndicator && (
            <span
              className={`inline-flex h-2 w-2 rounded-full shrink-0 ${indicatorColor}`}
              title={indicatorLabel}
            ></span>
          )}
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent className="w-64" align="start">
        {values.map((item) => (
          <DropdownMenuItem
            key={item}
            onClick={() => setValue(item)}
            className="flex items-center justify-between gap-3 py-2 px-3"
          >
            <span className="grow truncate">{item}</span>
            {itemsWithIndicator && itemsWithIndicator.has(item) && (
              <span
                className={`inline-flex h-2 w-2 rounded-full shrink-0 ${indicatorColor}`}
                title={indicatorLabel}
              ></span>
            )}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
