"use client";

import { useState } from "react";

export default function SettingsPage() {
  const [siteUrl, setSiteUrl] = useState("https://cautilyacapital.com");
  const [llmProvider, setLlmProvider] = useState("openai");
  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div className="max-w-2xl">
      <h2 className="text-3xl mb-8">Settings</h2>

      <div className="space-y-8">
        <div className="card p-6 rounded-2xl">
          <h3 className="text-xl font-semibold mb-5">
            Site Configuration
          </h3>
          <div className="space-y-4">
            <div>
              <label className="label block mb-2">Primary Site URL</label>
              <input
                type="url"
                value={siteUrl}
                onChange={(e) => setSiteUrl(e.target.value)}
                className="w-full"
              />
            </div>
          </div>
        </div>

        <div className="card p-6 rounded-2xl">
          <h3 className="text-xl font-semibold mb-5">
            AI Provider
          </h3>
          <div>
            <label className="label block mb-2">LLM Provider</label>
            <select
              value={llmProvider}
              onChange={(e) => setLlmProvider(e.target.value)}
              className="w-full"
            >
              <option value="openai">OpenAI (GPT-4)</option>
              <option value="claude">Anthropic (Claude)</option>
              <option value="together">Together AI</option>
              <option value="ollama">Ollama (Local)</option>
            </select>
          </div>
        </div>

        <button onClick={handleSave} className="btn-primary text-base px-8 py-3">
          {saved ? "Saved!" : "Save Settings"}
        </button>
      </div>
    </div>
  );
}
