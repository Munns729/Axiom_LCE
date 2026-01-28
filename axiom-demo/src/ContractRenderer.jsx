import React, { useState } from 'react';
import { ChevronDown, ChevronRight, FileText, AlertTriangle } from 'lucide-react';

// Helper to check if node is involved in conflict
const getConflictForNode = (node, conflictAnalysis) => {
    if (!conflictAnalysis?.has_conflict || !conflictAnalysis.affected_sections || !node.an_num) return null;

    // Normalize mapping: check if node.an_num ("4.2") is in affected list
    const isAffected = conflictAnalysis.affected_sections.some(sec => sec === node.an_num);

    if (isAffected) {
        return {
            type: conflictAnalysis.conflict_type,
            details: conflictAnalysis.details,
            severity: conflictAnalysis.severity
        };
    }
    return null;
};

// Warning Banner Component
const WarningBanner = ({ conflict }) => (
    <div className="mb-2 p-2 bg-amber-50 border border-amber-200 rounded flex items-center gap-2 animate-in fade-in zoom-in duration-300">
        <AlertTriangle className="w-4 h-4 text-amber-600" />
        <div className="flex-1">
            <p className="text-[11px] font-bold text-amber-800 uppercase tracking-tight">Logic Conflict: {conflict.type?.replace(/_/g, ' ')}</p>
            <p className="text-xs text-amber-700">{conflict.details}</p>
        </div>
    </div>
);

// Helper to highlight terms (Primitive version)
const renderContentWithHighlights = (text) => {
    if (!text) return null;
    // Highlight anything in quotes that looks like a definition or explicit term
    const parts = text.split(/("[\w\s]+"|“[\w\s]+”)/g);
    return parts.map((part, i) => {
        if (part.startsWith('"') || part.startsWith('“')) {
            return (
                <span
                    key={i}
                    className="font-semibold text-indigo-700 bg-indigo-50 px-1 py-0.5 rounded border border-indigo-100/50 cursor-help hover:bg-indigo-100 transition-colors"
                    title="Defined Term"
                >
                    {part}
                </span>
            );
        }
        return part;
    });
};

// Recursive component to render AST nodes
const ContractNode = ({ node, conflictAnalysis, depth = 0 }) => {
    const [isOpen, setIsOpen] = useState(true); // Default open

    if (!node) return null;

    // Check for conflict
    const conflict = getConflictForNode(node, conflictAnalysis);

    // Render children recursively
    const children = node.children?.map((child, i) => (
        <ContractNode
            key={child.id || i}
            node={child}
            conflictAnalysis={conflictAnalysis}
            depth={depth + 1}
        />
    ));

    const toggleOpen = (e) => {
        e.stopPropagation();
        setIsOpen(!isOpen);
    };

    // Helper for clause styling
    const getClauseStyle = (type) => {
        switch (type) {
            case 'obligation': return 'border-l-4 border-red-400 bg-red-50/50';
            case 'condition': return 'border-l-4 border-amber-400 bg-amber-50/50';
            case 'right': return 'border-l-4 border-emerald-400 bg-emerald-50/50';
            case 'representation': return 'border-l-4 border-blue-400 bg-blue-50/50';
            case 'definition': return 'border-l-4 border-purple-400 bg-purple-50/50';
            default: return 'border-l-2 border-transparent hover:border-slate-200';
        }
    };

    const getClauseLabel = (type) => {
        switch (type) {
            case 'obligation': return 'Obligation';
            case 'condition': return 'Condition';
            case 'right': return 'Right';
            case 'representation': return 'Rep/Warranty';
            case 'definition': return 'Definition';
            default: return null;
        }
    };

    const clauseStyle = node.clause_type ? getClauseStyle(node.clause_type) : '';
    const clauseLabel = node.clause_type ? getClauseLabel(node.clause_type) : null;

    // Render logic based on an_type (Akoma Ntoso Type)
    switch (node.an_type) {
        case 'article':
        case 'chapter':
            return (
                <div className="mb-8 mt-6">
                    <div
                        className="flex items-center gap-3 mb-4 border-b border-indigo-100 pb-2 cursor-pointer hover:bg-slate-50 rounded transition-colors"
                        onClick={toggleOpen}
                    >
                        <button className="text-indigo-400 hover:text-indigo-700">
                            {isOpen ? <ChevronDown className="w-5 h-5" /> : <ChevronRight className="w-5 h-5" />}
                        </button>
                        <span className="text-sm font-sans font-bold text-slate-400">
                            {node.an_num || '00'}
                        </span>
                        <h4 className="font-sans text-sm font-bold text-indigo-900 uppercase tracking-widest flex-1 select-none">
                            {node.text_content || 'SECTION'}
                        </h4>
                        <span className="text-[10px] bg-slate-100 text-slate-500 px-2 py-0.5 rounded-full">
                            Article
                        </span>
                    </div>
                    {conflict && <WarningBanner conflict={conflict} />}
                    {isOpen && (
                        <div className="pl-0 md:pl-2 space-y-4 animate-in fade-in slide-in-from-top-1 duration-200">
                            {children}
                        </div>
                    )}
                </div>
            );

        case 'section':
            // Numbered section (e.g. 4.1)
            return (
                <div className="mb-4">
                    <div className="group">
                        <div
                            className="flex items-baseline gap-3 text-justify leading-relaxed cursor-pointer"
                            onClick={toggleOpen}
                        >
                            <div className="shrink-0 flex items-center gap-1 w-16 -ml-6 justify-end pr-3 opacity-0 group-hover:opacity-100 transition-opacity">
                                <button className="text-slate-400 hover:text-indigo-600">
                                    {isOpen ? <ChevronDown className="w-3 h-3" /> : <ChevronRight className="w-3 h-3" />}
                                </button>
                            </div>
                            <span className="font-bold text-slate-900 shrink-0 select-none hover:text-indigo-700 transition-colors">
                                {node.an_num}
                            </span>
                            <div className="text-slate-800 flex-1">
                                {conflict && <WarningBanner conflict={conflict} />}
                                {/* If text_content repeats num, strip it, else just render */}
                                {node.text_content && node.an_num && node.text_content.startsWith(node.an_num)
                                    ? node.text_content.replace(node.an_num, '').trim()
                                    : node.text_content || ''}
                            </div>
                        </div>
                    </div>
                    {children && isOpen && (
                        <div className="pl-6 mt-3 space-y-3 border-l-2 border-slate-100 ml-2">
                            {children}
                        </div>
                    )}
                </div>
            );

        case 'paragraph':
            // General paragraph
            return (
                <div className={`mb-3 group relative pl-3 pr-2 py-1.5 rounded transition-all ${conflict ? 'bg-amber-50/30' : ''} ${clauseStyle}`}>
                    {conflict && <WarningBanner conflict={conflict} />}
                    <div className="flex justify-between items-start gap-4">
                        <p className="text-justify text-slate-600 leading-relaxed group-hover:text-slate-900 flex-1">
                            {renderContentWithHighlights(node.text_content)}
                        </p>
                        {clauseLabel && (
                            <span className="shrink-0 text-[9px] uppercase tracking-wider font-bold text-slate-400 opacity-0 group-hover:opacity-100 transition-opacity select-none border border-slate-200 px-1 rounded bg-white">
                                {clauseLabel}
                            </span>
                        )}
                    </div>
                    {children}
                </div>
            );

        case 'point':
            // Bullet point / list item
            return (
                <div className={`flex gap-3 mb-2 pl-4 py-1 rounded ${clauseStyle}`}>
                    <span className="font-bold text-slate-500 shrink-0 text-sm mt-0.5">{node.an_num || '•'}</span>
                    <div className="flex-1">
                        {conflict && <WarningBanner conflict={conflict} />}
                        <p className="text-justify text-slate-600 leading-relaxed">
                            {renderContentWithHighlights(node.text_content)}
                        </p>
                        {clauseLabel && (
                            <span className="inline-block mt-1 text-[9px] uppercase tracking-wider font-bold text-slate-400 opacity-60">
                                {clauseLabel}
                            </span>
                        )}
                    </div>
                </div>
            );

        default:
            // Fallback for root or unknown
            return <div className="space-y-4">{children}</div>;
    }
};

const ContractRenderer = ({ tree, conflictAnalysis }) => {
    if (!tree) return null;

    // The root might be a document object or list of nodes
    // Spine returns { root: { ... } } usually
    const rootNode = tree.root || tree;

    return (
        <div className="contract-content pb-20">
            {!rootNode.children?.length ? (
                <div className="text-center py-12 text-slate-400">
                    <FileText className="w-12 h-12 mx-auto mb-3 opacity-20" />
                    <p>Document structure empty or parsing failed.</p>
                </div>
            ) : (
                <ContractNode node={rootNode} conflictAnalysis={conflictAnalysis} />
            )}
        </div>
    );
};

export default ContractRenderer;
