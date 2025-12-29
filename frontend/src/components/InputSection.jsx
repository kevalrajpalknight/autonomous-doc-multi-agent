import { Github } from "lucide-react";

export function InputSection({ onGenerate, isLoading }) {
  const [url, setUrl] = React.useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (url.trim()) {
      onGenerate(url);
      setUrl("");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-8">
      <form onSubmit={handleSubmit} className="w-full max-w-2xl">
        {/* Glassmorphism Card */}
        <div className="backdrop-blur-xl bg-white/10 border border-white/20 rounded-3xl p-8 shadow-2xl">
          {/* Header */}
          <div className="flex items-center gap-4 mb-8">
            <div className="p-4 rounded-full bg-gradient-to-br from-blue-500 to-purple-500">
              <Github size={32} className="text-white" />
            </div>
            <div>
              <h1 className="text-4xl font-bold text-white mb-2">Doc Agent</h1>
              <p className="text-gray-300 text-sm">
                Generate beautiful documentation from any GitHub repository
              </p>
            </div>
          </div>

          {/* Input Section */}
          <div className="space-y-4">
            <label className="block text-sm font-medium text-gray-200">
              GitHub Repository URL
            </label>
            <div className="relative">
              <input
                type="url"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="https://github.com/username/repository"
                className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/20 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
              />
            </div>

            {/* Generate Button */}
            <button
              type="submit"
              disabled={isLoading || !url.trim()}
              className="w-full py-3 px-6 rounded-xl font-semibold text-white bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 hover:shadow-lg hover:scale-105 active:scale-95"
            >
              {isLoading ? (
                <div className="flex items-center justify-center gap-2">
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Generating...
                </div>
              ) : (
                "Generate Documentation"
              )}
            </button>
          </div>

          {/* Info */}
          <p className="mt-6 text-xs text-gray-400 text-center">
            The agent will analyze your repository and generate comprehensive
            documentation
          </p>
        </div>
      </form>
    </div>
  );
}

import React from "react";
