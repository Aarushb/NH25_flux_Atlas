import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";

type DialogProps = {
  buttonText: string;
};

export function DialogDemo({ buttonText }: DialogProps) {
  return (
    <Dialog>
      <form>
        <DialogTrigger asChild>
          <Button variant="outline">{buttonText}</Button>
        </DialogTrigger>
  <DialogContent className="sm:max-w-[325px] glass">
          <DialogHeader>
            <DialogTitle>Place your Bid</DialogTitle>
          </DialogHeader>
          <div className="grid gap-4">
            <div className="grid gap-3">
              <Input
                id="bid-amount"
                name="bid-amount"
                type="number"
                defaultValue="8"
              />
            </div>
          </div>
          <DialogFooter>
            <DialogClose asChild>
              <Button variant="outline">Cancel</Button>
            </DialogClose>
            <Button type="submit">Place Bid</Button>
          </DialogFooter>
        </DialogContent>
      </form>
    </Dialog>
  );
}