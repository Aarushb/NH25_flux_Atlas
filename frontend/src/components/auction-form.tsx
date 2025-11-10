import { useEffect, useState } from "react";

interface AuctionFormProps {
  sellerCountry?: string | null; 
  currentCountry?: string; 
  availableResources?: string[]; 
}

export default function AuctionForm({ sellerCountry, currentCountry, availableResources }: AuctionFormProps) {
  const [resources, setResources] = useState<string[]>(availableResources ?? []);
  const [resource, setResource] = useState(availableResources?.[0] ?? "");
  const [quantity, setQuantity] = useState(0);
  const [basePrice, setBasePrice] = useState<number | undefined>(undefined);
  const [status, setStatus] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    if (availableResources && availableResources.length) {
      setResources(availableResources);
      setResource(availableResources[0]);
      return;
    }

    fetch("/resources")
      .then((r) => r.json())
      .then((data) => {
        if (!mounted) return;
        const list = Array.isArray(data) ? data.map((r: unknown) => {
          const rr = r as Record<string, unknown>;
          return String(rr?.name ?? rr?.id ?? r);
        }) : [];
        const filtered = (list.length ? list : ["Aluminum", "Oil", "Natural Gas", "Uranium"]).filter((name) => {
          if (!currentCountry) return true;
          const low = currentCountry.toLowerCase();
          if (low.includes("united") || low === "world") return true;
          if (low.includes("somalia") || low.includes("chad")) return name !== "Uranium";
          return true;
        });
        setResources(filtered);
        if (filtered.length) setResource(filtered[0]);
      })
      .catch(() => {
        const fallback = ["Aluminum", "Natural Gas"];
        setResources(fallback);
        setResource(fallback[0]);
      });

    return () => {
      mounted = false;
    };
  }, [availableResources, currentCountry]);

  const validate = () => {
    if (!resource) return "Choose a resource";
    if (!quantity || quantity <= 0) return "Quantity must be > 0";
    return null;
  };

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const err = validate();
    if (err) {
      setStatus(err);
      return;
    }

    const body = {
      seller_country: sellerCountry ?? "",
      resource_name: resource,
      total_quantity: Number(quantity),
      base_price: Number(basePrice ?? 0),
    };

    try {
      setStatus("Selling on market...");
      const res = await fetch("/sell", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const data = await res.json();
      setStatus("Listed on market");
      console.debug("sell result", data);
      
      window.dispatchEvent(new CustomEvent("auction:simulated", { detail: data }));
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      setStatus(msg ?? "Error");
    }
  };

  return (
    <form onSubmit={onSubmit} className="auction-form grid grid-cols-1 sm:grid-cols-4 gap-2 items-end">
      <div>
        <label className="text-xs text-muted-foreground">Resource</label>
        <select value={resource} onChange={(e) => setResource(e.target.value)} className="w-full">
          {resources.map((r) => (
            <option key={r} value={r}>{r}</option>
          ))}
        </select>
      </div>
      <div>
        <label className="text-xs text-muted-foreground">Quantity</label>
        <input type="number" min="0" step="0.1" value={quantity} onChange={(e) => setQuantity(Number(e.target.value))} className="w-full" />
      </div>
      <div>
        <label className="text-xs text-muted-foreground">Base Price</label>
        <input type="number" step="0.0001" value={basePrice ?? 0} onChange={(e) => setBasePrice(Number(e.target.value))} className="w-full" />
      </div>
      <div className="sm:col-span-4">
        <button type="submit" className="btn">Sell on market</button>
        {status && <div className="text-xs text-muted-foreground mt-1">{status}</div>}
      </div>
    </form>
  );
}
