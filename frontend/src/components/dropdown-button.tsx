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
};

export function DropdownMenuDemo({ value, setValue, values }: DropDownProps) {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline">{value}</Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent className="w-56" align="start">
        {values.map((value) => (
          <DropdownMenuItem onClick={() => setValue(value)}>
            {value}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
