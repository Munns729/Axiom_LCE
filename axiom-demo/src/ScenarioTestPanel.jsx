import React, { useState } from 'react';
import { ClauseSuggestionModal } from './ClauseSuggestionModal';
import { CustomScenarioInput } from './CustomScenarioInput';
import { CheckCircle2, AlertTriangle, ChevronDown, Sparkles } from 'lucide-react';

const SourceBadge = ({ sourceType }) => {
    const badges = {
        template: { label: 'Standard', color: 'bg-blue-100 text-blue-700' },
        contract_generated: { label: 'AI Generated', color: 'bg-purple-100 text-purple-700' },
        user_custom: { label: 'Custom', color: 'bg-emerald-100 text-emerald-700' }
    };
    const badge = badges[sourceType] || badges.template;
    return (
        <span className={`text-[10px] px-2 py-0.5 rounded-full font-medium ${badge.color}`}>
            {badge.label}
        </span>
    );
};

const ScenarioTestPanel = ({ scenarios, onScenarioClick, expandedScenarioId, analysisId, onScenarioAdded }) => {
    const [showSuggestions, setShowSuggestions] = useState(false);
    const [selectedScenario, setSelectedScenario] = useState(null);

    const handleSuggestFix = (scenario) => {
        setSelectedScenario(scenario);
        setShowSuggestions(true);
    };

    const passCount = scenarios.filter(s => s.status === 'pass').length;
    const totalCount = scenarios.length;

    return (
        <div className="bg-white rounded-2xl p-5 shadow-sm border border-slate-100">
            {/* Header */}
            <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-bold text-slate-900">📋 Scenario Test Results</h3>
                <span className="text-xs font-medium text-slate-500">
                    {passCount}/{totalCount} passed
                </span>
            </div>

            {/* Scenario List */}
            <div className="space-y-2">
                {scenarios.map(scenario => {
                    const isExpanded = expandedScenarioId === scenario.id;
                    const isFail = scenario.status === 'fail';

                    return (
                        <div key={scenario.id}>
                            <div
                                className={`flex items-center gap-3 p-3 rounded-xl transition-all duration-200 border border-transparent
                                    ${isFail ? 'cursor-pointer hover:bg-amber-50/50' : 'cursor-default'}
                                    ${isExpanded ? 'bg-amber-50/50 border-amber-100' : ''}
                                `}
                                onClick={() => isFail && onScenarioClick(isExpanded ? null : scenario.id)}
                            >
                                <div className="shrink-0">
                                    {isFail ? (
                                        <AlertTriangle className="w-5 h-5 text-amber-600" />
                                    ) : (
                                        <CheckCircle2 className="w-5 h-5 text-emerald-500" />
                                    )}
                                </div>

                                <div className="flex-1 min-w-0">
                                    <div className="flex items-center gap-2 mb-0.5">
                                        <div className={`text-sm font-medium ${isFail ? 'text-slate-800' : 'text-slate-600'}`}>
                                            {scenario.name}
                                        </div>
                                        <SourceBadge sourceType={scenario.source_type} />
                                    </div>
                                    <div className="text-xs text-slate-400 truncate">
                                        {scenario.description}
                                    </div>
                                </div>

                                {isFail && (
                                    <div className={`text-slate-400 transition-transform duration-300 ${isExpanded ? 'rotate-180' : ''}`}>
                                        <ChevronDown className="w-4 h-4" />
                                    </div>
                                )}
                            </div>

                            {isExpanded && isFail && (
                                <div className="mt-2 mx-3 p-4 bg-white/50 rounded-xl border border-amber-200 animate-in slide-in-from-top-2 duration-300">
                                    <div className="space-y-3">
                                        <div>
                                            <div className="text-[10px] uppercase font-bold text-slate-500 mb-1 tracking-wider">Trigger Event</div>
                                            <div className="text-sm text-slate-700">{scenario.trigger_event || scenario.triggerEvent}</div>
                                        </div>

                                        <div className="p-3 bg-amber-50 rounded-lg border border-amber-100">
                                            <div className="text-[10px] uppercase font-bold text-amber-700 mb-1 tracking-wider flex items-center gap-1">
                                                <AlertTriangle className="w-3 h-3" /> Issue Detected
                                            </div>
                                            <div className="text-sm text-amber-900 leading-relaxed rounded">{scenario.conflict}</div>
                                        </div>

                                        <div className="grid grid-cols-2 gap-4 pt-1">
                                            <div>
                                                <div className="text-[10px] uppercase font-bold text-slate-500 mb-1 tracking-wider">Expected</div>
                                                <div className="text-sm text-slate-600 leading-relaxed">{scenario.expected_outcome || scenario.expectedOutcome}</div>
                                            </div>
                                            <div>
                                                <div className="text-[10px] uppercase font-bold text-amber-700 mb-1 tracking-wider">Actual Result</div>
                                                <div className="text-sm text-amber-800 font-medium leading-relaxed bg-amber-50/50 px-2 py-1 -mx-2 rounded">
                                                    {scenario.outcome}
                                                </div>
                                            </div>
                                        </div>

                                        <div className="mt-4 pt-4 border-t border-amber-200">
                                            <button
                                                onClick={(e) => {
                                                    e.stopPropagation();
                                                    handleSuggestFix(scenario);
                                                }}
                                                className="
                                                    px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 
                                                    text-white rounded-lg text-sm font-medium
                                                    hover:shadow-lg transition-all flex items-center gap-2
                                                "
                                            >
                                                <Sparkles className="w-4 h-4" />
                                                Suggest AI Fix
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>
                    );
                })}
            </div>

            {/* Custom Scenario Input */}
            <CustomScenarioInput
                analysisId={analysisId}
                onScenarioAdded={onScenarioAdded}
            />

            {/* Summary footer */}
            <div className="mt-4 pt-4 border-t border-slate-100 text-center">
                <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium ${passCount === totalCount ? 'bg-emerald-50 text-emerald-700' : 'bg-amber-50 text-amber-700'}`}>
                    {passCount === totalCount
                        ? '✅ All scenarios passed'
                        : `⚠️ ${totalCount - passCount} ${totalCount - passCount === 1 ? 'failure' : 'failures'} detected`
                    }
                </span>
            </div>

            <ClauseSuggestionModal
                isOpen={showSuggestions}
                onClose={() => setShowSuggestions(false)}
                analysisId={analysisId}
                scenario={selectedScenario}
            />
        </div>
    );
};

export default ScenarioTestPanel;
