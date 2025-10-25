import React from "react";
import ReactMarkdown from "react-markdown";

export default function MarkdownRenderer({ content }) {
    return (
        <div className="prose prose-slate dark:prose-invert max-w-2xl mx-auto my-24">
            <ReactMarkdown>{content}</ReactMarkdown>
        </div>
    );
}