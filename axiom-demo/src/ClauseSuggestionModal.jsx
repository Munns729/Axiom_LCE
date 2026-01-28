import { useState } from 'react';
import { X, AlertTriangle, Shield, Scale, Building2, Download, Sparkles } from 'lucide-react';
import { toast } from 'sonner';

export function ClauseSuggestionModal({
    isOpen,
    onClose,
    analysisId,
    scenario
}) {
    const [suggestions, setSuggestions] = useState(null);
    const [loading, setLoading] = useState(false);
    const [selectedType, setSelectedType] = useState(null);
    const [exporting, setExporting] = useState(false);

    // Load suggestions when modal opens
    const loadSuggestions = async () => {
        setLoading(true);
        try {
            const response = await fetch(
                `http://localhost:8000/api/suggest-fixes/${analysisId}?scenario_id=${scenario.id}`,
                { method: 'POST' } // Changed to POST as per backend definition
            );
            const data = await response.json();
            setSuggestions(data);
        } catch (error) {
            console.error('Failed to load suggestions:', error);
            toast.error('Failed to load suggestions');
        } finally {
            setLoading(false);
        }
    };

    // Apply selected fix
    const handleApply = async () => {
        if (!selectedType || !suggestions) return;

        setExporting(true);
        try {
            // Record selection
            await fetch(`http://localhost:8000/api/select-suggestion/${suggestions.suggestion_id}?selected_type=${selectedType}`, {
                method: 'POST'
            });

            toast.success('Fix applied! Use the main Export button to download the revised document.');

            // Call onSuccess prop if available (we will add this prop later)
            if (onClose) onClose();

        } catch (error) {
            console.error('Failed to apply fix:', error);
            toast.error('Failed to apply fix');
        } finally {
            setExporting(false);
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
                {/* Header */}
                <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between bg-gradient-to-r from-blue-50 to-purple-50">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center">
                            <Sparkles className="w-5 h-5 text-white" />
                        </div>
                        <div>
                            <h2 className="text-lg font-semibold text-slate-900">
                                AI-Powered Clause Suggestions
                            </h2>
                            <p className="text-sm text-slate-600">
                                {scenario.name}
                            </p>
                        </div>
                    </div>
                    <button
                        onClick={onClose}
                        className="text-slate-400 hover:text-slate-600 transition-colors"
                    >
                        <X className="w-5 h-5" />
                    </button>
                </div>

                {/* Content */}
                <div className="flex-1 overflow-y-auto p-6 space-y-6">
                    {/* Original Problematic Clause */}
                    {suggestions ? (
                        <div className="bg-red-50 border border-red-200 rounded-xl p-4">
                            <div className="flex items-start gap-3">
                                <AlertTriangle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                                <div className="flex-1">
                                    <div className="text-sm font-medium text-red-900 mb-1">
                                        Original Clause (Section {suggestions.original_section})
                                    </div>
                                    <div className="text-sm text-red-800 font-mono bg-white/50 p-3 rounded border border-red-200">
                                        {suggestions.original_clause}
                                    </div>
                                    <div className="text-xs text-red-700 mt-2">
                                        <strong>Conflict:</strong> {suggestions.conflict_type.replace(/_/g, ' ')}
                                    </div>
                                </div>
                            </div>
                        </div>
                    ) : null}

                    {/* Loading State or Initial State */}
                    {!suggestions && !loading && (
                        <div className="text-center py-12">
                            <button
                                onClick={loadSuggestions}
                                className="px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl font-medium hover:shadow-lg transition-all"
                            >
                                Generate AI Suggestions
                            </button>
                        </div>
                    )}

                    {loading && (
                        <div className="text-center py-12">
                            <div className="inline-block w-8 h-8 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin"></div>
                            <p className="text-sm text-slate-600 mt-4">
                                Generating alternatives with Mistral AI...
                            </p>
                        </div>
                    )}

                    {/* Suggestions */}
                    {suggestions && suggestions.suggestions && (
                        <div className="space-y-4">
                            <div className="text-sm font-medium text-slate-700 mb-3">
                                Select a revision approach:
                            </div>

                            {suggestions.suggestions.map((suggestion, index) => (
                                <SuggestionCard
                                    key={suggestion.type}
                                    suggestion={suggestion}
                                    index={index}
                                    isSelected={selectedType === suggestion.type}
                                    onSelect={() => setSelectedType(suggestion.type)}
                                />
                            ))}
                        </div>
                    )}
                </div>

                {/* Footer */}
                {suggestions && (
                    <div className="px-6 py-4 border-t border-slate-200 bg-slate-50 flex items-center justify-between">
                        <div className="text-xs text-slate-600">
                            {suggestions.cached ? '⚡ Cached result' : `Generated in ${suggestions.generation_time_ms}ms`}
                        </div>
                        <div className="flex gap-3">
                            <button
                                onClick={onClose}
                                className="px-4 py-2 text-sm font-medium text-slate-700 hover:text-slate-900 transition-colors"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={handleApply}
                                disabled={!selectedType || exporting}
                                className={`
                  px-6 py-2 rounded-lg text-sm font-medium flex items-center gap-2 transition-all
                  ${selectedType && !exporting
                                        ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white hover:shadow-lg'
                                        : 'bg-slate-200 text-slate-400 cursor-not-allowed'
                                    }
                `}
                            >
                                <Sparkles className="w-4 h-4" />
                                {exporting ? 'Applying...' : 'Apply Fix to Document'}
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}

function SuggestionCard({ suggestion, index, isSelected, onSelect }) {
    const typeConfig = {
        founder_friendly: {
            icon: Shield,
            color: 'green',
            label: 'Founder-Friendly',
            description: 'Maximum protection for founder'
        },
        market_standard: {
            icon: Scale,
            color: 'blue',
            label: 'Market Standard',
            description: 'Balanced, typical for Series A'
        },
        company_friendly: {
            icon: Building2,
            color: 'amber',
            label: 'Company-Friendly',
            description: 'Prioritizes company interests'
        }
    };

    const config = typeConfig[suggestion.type];
    const Icon = config.icon;

    const riskColors = {
        low: 'text-green-700 bg-green-100',
        medium: 'text-amber-700 bg-amber-100',
        high: 'text-red-700 bg-red-100'
    };

    return (
        <div
            onClick={onSelect}
            className={`
        border-2 rounded-xl p-4 cursor-pointer transition-all
        ${isSelected
                    ? `border-${config.color}-500 bg-${config.color}-50 shadow-lg`
                    : 'border-slate-200 hover:border-slate-300 hover:shadow-md'
                }
      `}
        >
            <div className="flex items-start gap-3">
                <div className={`
          w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0
          bg-${config.color}-100
        `}>
                    <Icon className={`w-5 h-5 text-${config.color}-600`} />
                </div>

                <div className="flex-1 space-y-3">
                    {/* Header */}
                    <div className="flex items-start justify-between">
                        <div>
                            <div className="font-semibold text-slate-900">
                                Option {String.fromCharCode(65 + index)}: {config.label}
                            </div>
                            <div className="text-xs text-slate-600 mt-0.5">
                                {config.description}
                            </div>
                        </div>
                        <span className={`
              text-xs px-2 py-1 rounded-full font-medium
              ${riskColors[suggestion.risk_level] || riskColors.medium}
            `}>
                            {suggestion.risk_level.toUpperCase()} RISK
                        </span>
                    </div>

                    {/* Clause Text */}
                    <div className="text-sm bg-white border border-slate-200 rounded-lg p-3 font-mono text-slate-700">
                        {suggestion.clause_text}
                    </div>

                    {/* Rationale */}
                    <div className="text-sm">
                        <div className="text-xs font-medium text-slate-700 mb-1">
                            Why this works:
                        </div>
                        <div className="text-slate-600">
                            {suggestion.rationale}
                        </div>
                    </div>

                    {/* Changes Summary */}
                    <div className="text-xs bg-slate-50 border border-slate-200 rounded p-2">
                        <strong className="text-slate-700">Changes:</strong>{' '}
                        <span className="text-slate-600">{suggestion.changes_summary}</span>
                    </div>
                </div>
            </div>

            {/* Selection Indicator */}
            {isSelected && (
                <div className={`
          mt-3 pt-3 border-t border-${config.color}-200
          text-xs font-medium text-${config.color}-700 flex items-center gap-2
        `}>
                    <div className={`w-4 h-4 rounded-full bg-${config.color}-500 flex items-center justify-center`}>
                        <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                        </svg>
                    </div>
                    Selected for export
                </div>
            )}
        </div>
    );
}
