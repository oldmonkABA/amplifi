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
      <h2 className="text-2xl font-semibold mb-6">Settings</h2>

      <div className="space-y-6">
        <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
          <h3 className="text-sm font-medium mb-3">Site Configuration</h3>
          <div className="space-y-3">
            <div>
              <label className="block text-xs text-gray-400 mb-1">Primary Site URL</label>
              <input
                type="url"
                value={siteUrl}
                onChange={(e) => setSiteUrl(e.target.value)}
                className="w-full bg-gray-950 border border-gray-800 rounded-lg px-3 py-2 text-sm"
              />
            </div>
          </div>
        </div>

        <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
          <h3 className="text-sm font-medium mb-3">AI Provider</h3>
          <div>
            <label className="block text-xs text-gray-400 mb-1">LLM Provider</label>
            <select
              value={llmProvider}
              onChange={(e) => setLlmProvider(e.target.value)}
              className="bg-gray-950 border border-gray-800 rounded-lg px-3 py-2 text-sm"
            >
              <option value="openai">OpenAI (GPT-4)</option>
              <option value="claude">Anthropic (Claude)</option>
              <option value="together">Together AI</option>
              <option value="ollama">Ollama (Local)</option>
            </select>
          </div>
        </div>

        <button
          onClick={handleSave}
          className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium transition"
        >
          {saved ? "Saved!" : "Save Settings"}
        </button>
      </div>
    </div>
  );
}
