import { useState } from "react";

interface LoginPageProps {
  countries: string[];
  onLogin: (name: string, country: string) => void;
}

export default function LoginPage({ countries, onLogin }: LoginPageProps) {
  const [name, setName] = useState("");
  const [country, setCountry] = useState<string>(countries?.[0] ?? "World");

  return (
    <div className="card glass max-w-md mx-auto mt-8">
      <h3 className="text-xl font-semibold mb-4">Representative login</h3>
      <div className="flex flex-col gap-3">
        <label className="text-sm">Representative name</label>
        <input
          className="input"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Your full name"
          aria-label="Representative name"
        />

        <label className="text-sm">Country</label>
        <select
          className="input"
          value={country}
          onChange={(e) => setCountry(e.target.value)}
          aria-label="Country"
        >
          {countries.map((c) => (
            <option key={c} value={c}>
              {c}
            </option>
          ))}
        </select>

        <div className="flex justify-end">
          <button
            className="btn"
            onClick={() => {
              // local-only 'login'
              onLogin(name.trim(), country);
            }}
            disabled={name.trim().length === 0}
          >
            Log in
          </button>
        </div>
      </div>
    </div>
  );
}
