import { Check, Copy, X } from "lucide-react";
import { useState } from "react";
import Markdown from "react-markdown";

export function MarkdownPreview({ markdown, onClose, isVisible }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(markdown);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error("Failed to copy:", err);
    }
  };

  if (!isVisible) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40 flex items-center justify-center p-4">
      <div className="w-full max-w-4xl max-h-[90vh] bg-white rounded-2xl shadow-2xl flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-2xl font-bold text-gray-900">
            Generated Documentation
          </h2>
          <div className="flex items-center gap-2">
            <button
              onClick={handleCopy}
              className="flex items-center gap-2 px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-colors"
            >
              {copied ? (
                <>
                  <Check size={18} />
                  Copied!
                </>
              ) : (
                <>
                  <Copy size={18} />
                  Copy Markdown
                </>
              )}
            </button>
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <X size={20} className="text-gray-600" />
            </button>
          </div>
        </div>

        {/* Markdown Content */}
        <div className="flex-1 overflow-y-auto p-8">
          <article className="prose prose-lg max-w-none">
            <Markdown
              components={{
                h1: ({ node, ...props }) => (
                  <h1
                    className="text-4xl font-bold mb-6 text-gray-900 mt-8"
                    {...props}
                  />
                ),
                h2: ({ node, ...props }) => (
                  <h2
                    className="text-3xl font-bold mb-4 text-gray-800 mt-8"
                    {...props}
                  />
                ),
                h3: ({ node, ...props }) => (
                  <h3
                    className="text-2xl font-bold mb-3 text-gray-700 mt-6"
                    {...props}
                  />
                ),
                p: ({ node, ...props }) => (
                  <p
                    className="text-gray-700 mb-4 leading-relaxed"
                    {...props}
                  />
                ),
                ul: ({ node, ...props }) => (
                  <ul
                    className="list-disc list-inside mb-4 text-gray-700"
                    {...props}
                  />
                ),
                ol: ({ node, ...props }) => (
                  <ol
                    className="list-decimal list-inside mb-4 text-gray-700"
                    {...props}
                  />
                ),
                li: ({ node, ...props }) => <li className="mb-2" {...props} />,
                code: ({ node, inline, ...props }) =>
                  inline ? (
                    <code
                      className="bg-gray-100 px-2 py-1 rounded text-red-600 font-mono"
                      {...props}
                    />
                  ) : (
                    <code
                      className="bg-gray-900 text-gray-100 p-4 rounded-lg block mb-4 overflow-x-auto"
                      {...props}
                    />
                  ),
                blockquote: ({ node, ...props }) => (
                  <blockquote
                    className="border-l-4 border-gray-300 pl-4 py-2 mb-4 text-gray-600 italic"
                    {...props}
                  />
                ),
                a: ({ node, ...props }) => (
                  <a className="text-blue-600 hover:underline" {...props} />
                ),
                hr: () => <hr className="my-8 border-gray-300" />,
              }}
            >
              {markdown}
            </Markdown>
          </article>
        </div>
      </div>
    </div>
  );
}
