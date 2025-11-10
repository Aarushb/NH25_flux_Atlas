import { useEffect, useState } from "react";

interface LoginPageProps {
  countries: string[];
  onLogin: (name: string, country: string) => void;
}

export default function LoginPage({ countries, onLogin }: LoginPageProps) {
  const [name, setName] = useState("");
  const [country, setCountry] = useState<string>(countries?.[0] ?? "World");
  const [password, setPassword] = useState("");

  useEffect(() => {
    try {
      const saved = localStorage.getItem("repName");
      const savedCountry = localStorage.getItem("repCountry");
      if (saved) setName(saved);
      if (savedCountry) setCountry(savedCountry);
    } catch {
      void 0;
    }
  }, []);

  const doLogin = (_useFingerprint = false) => {
    const trimmed = name.trim();
    if (trimmed.length === 0) return;
    try {
      localStorage.setItem("repName", trimmed);
      localStorage.setItem("repCountry", country);
    } catch {
      void 0;
    }
    onLogin(trimmed, country);
  };

  console.log(countries)

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

        <label className="text-sm">Password</label>
        <input
          className="input"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Password"
          aria-label="Password"
        />

        <div className="flex items-center justify-end gap-4 mt-2">
          <div className="flex items-center gap-2">
            <button
              className="btn"
              onClick={() => doLogin(false)}
              disabled={name.trim().length === 0}
            >
              Log in
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
