import { useEffect, useState } from "react";

export default function AuctionForm() {
  const [countries, setCountries] = useState<string[]>([]);
  const [resources, setResources] = useState<{ name: string; base_price?: number }[]>([]);
  const [seller, setSeller] = useState("");
  const [resource, setResource] = useState("");
  const [quantity, setQuantity] = useState(0);
  const [basePrice, setBasePrice] = useState<number | undefined>(undefined);
  const [status, setStatus] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    fetch("/countries")
      .then((r) => r.json())
      .then((data) => {
        if (!mounted) return;
        const names = Array.isArray(data) ? data.map((c: any) => (c?.name ?? c?.country ?? c?.id ?? String(c))) : [];
        setCountries(names);
        if (names.length) setSeller(names[0]);
      })
      .catch(() => {});

    fetch("/resources")
      .then((r) => r.json())
      .then((data) => {
        if (!mounted) return;
        const list = Array.isArray(data)
          ? data.map((res: unknown) => {
              const r = res as Record<string, unknown>;
              return { name: (r.name ?? r.id ?? String(r)) as string, base_price: (r.base_price ?? r.basePrice) as number | undefined };
            })
          : [];
        setResources(list as { name: string; base_price?: number }[]);
        if (list.length) {
          setResource(list[0].name);
          setBasePrice(list[0].base_price as number | undefined);
        }
      })
      .catch(() => {});

    return () => {
      mounted = false;
    };
  }, []);

  useEffect(() => {
    const res = resources.find((r) => r.name === resource);
    setBasePrice(res?.base_price ?? undefined);
  }, [resource, resources]);

  const validate = () => {
    if (!seller) return "Choose a seller";
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
      seller_country: seller,
      resource_name: resource,
      total_quantity: Number(quantity),
      base_price: Number(basePrice ?? 0),
    };

    try {
      setStatus("Simulating auction...");
      const res = await fetch("/simulate-auction", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const data = await res.json();
      setStatus("Simulation complete");
      console.debug("simulate result", data);
      // broadcast an event so dashboard components can react
      window.dispatchEvent(new CustomEvent('auction:simulated', { detail: data }));
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      setStatus(msg ?? "Error");
    }
  };

  return (
    <form onSubmit={onSubmit} className="auction-form grid grid-cols-1 sm:grid-cols-4 gap-2 items-end">
      <div>
        <label className="text-xs text-muted-foreground">Seller</label>
        <select value={seller} onChange={(e) => setSeller(e.target.value)} className="w-full">
          {countries.map((c) => (
            <option key={c} value={c}>{c}</option>
          ))}
        </select>
      </div>
      <div>
        <label className="text-xs text-muted-foreground">Resource</label>
        <select value={resource} onChange={(e) => setResource(e.target.value)} className="w-full">
          {resources.map((r) => (
            <option key={r.name} value={r.name}>{r.name}</option>
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
        <button type="submit" className="btn">Simulate Auction</button>
        {status && <div className="text-xs text-muted-foreground mt-1">{status}</div>}
      </div>
    </form>
  );
}
