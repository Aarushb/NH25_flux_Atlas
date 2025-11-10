import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import React from "react";

type DropDownProps = {
  value: string | null;
  setValue: React.Dispatch<React.SetStateAction<string | null>>;
  values: string[];
  placeholder:string;
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
