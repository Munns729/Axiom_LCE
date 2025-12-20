import React from 'react';

// Recursive component to render AST nodes
const ContractNode = ({ node, depth = 0 }) => {
    if (!node) return null;

    // Render children recursively
    const children = node.children?.map((child, i) => (
        <ContractNode key={child.id || i} node={child} depth={depth + 1} />
    ));

    // Render logic based on an_type (Akoma Ntoso Type)
    switch (node.an_type) {
        case 'article':
        case 'chapter':
            return (
                <div className="mb-12 mt-8">
                    <div className="flex items-center gap-4 mb-6 border-b border-indigo-100 pb-3">
                        <span className="text-sm font-sans font-bold text-slate-300">
                            {node.an_num || '00'}
                        </span>
                        <h4 className="font-sans text-sm font-bold text-indigo-900 uppercase tracking-widest flex-1">
                            {node.text_content || 'SECTION'}
                        </h4>
                    </div>
                    <div className="pl-0 md:pl-4 space-y-6">
                        {children}
                    </div>
                </div>
            );

        case 'section':
            // Numbered section (e.g. 4.1)
            return (
                <div className="mb-6">
                    <div className="flex items-baseline gap-3 text-justify leading-relaxed">
                        <span className="font-bold text-slate-900 shrink-0">{node.an_num}</span>
                        <div className="text-slate-700">
                            {/* If text_content repeats num, strip it, else just render */}
                            {node.text_content.startsWith(node.an_num)
                                ? node.text_content.replace(node.an_num, '').trim()
                                : node.text_content}
                        </div>
                    </div>
                    {children && <div className="pl-6 mt-4 space-y-4">{children}</div>}
                </div>
            );

        case 'paragraph':
            // General paragraph
            return (
                <div className="mb-4 group relative">
                    <p className="text-justify text-slate-600 leading-relaxed hover:text-slate-900 transition-colors">
                        {/* Highlight defined terms crudely for demo */}
                        {renderContentWithHighlights(node.text_content)}
                    </p>
                    {children}
                </div>
            );

        case 'point':
            // Bullet point / list item
            return (
                <div className="flex gap-3 mb-3 pl-4">
                    <span className="font-bold text-slate-900 shrink-0">{node.an_num || '•'}</span>
                    <p className="text-justify text-slate-600 leading-relaxed flex-1">
                        {node.text_content}
                    </p>
                </div>
            );

        default:
            // Fallback for root or unknown
            return <div className="space-y-4">{children}</div>;
    }
};

// Helper to highlight terms (Primitive version)
const renderContentWithHighlights = (text) => {
    if (!text) return null;
    // Highlight anything in quotes that looks like a definition
    const parts = text.split(/("[\w\s]+"|“[\w\s]+”)/g);
    return parts.map((part, i) => {
        if (part.startsWith('"') || part.startsWith('“')) {
            return <span key={i} className="font-bold text-slate-900 bg-slate-100 px-1 rounded">{part}</span>;
        }
        return part;
    });
};

const ContractRenderer = ({ tree }) => {
    if (!tree) return null;

    // The root might be a document object or list of nodes
    // Spine returns { root: { ... } } usually
    const rootNode = tree.root || tree;

    return (
        <div className="contract-content">
            <ContractNode node={rootNode} />
        </div>
    );
};

export default ContractRenderer;
