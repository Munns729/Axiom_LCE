import React, { useState } from 'react';
import { Send, Sparkles, Loader2 } from 'lucide-react';

export function CustomScenarioInput({ analysisId, onScenarioAdded }) {
    const [scenarioText, setScenarioText] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!scenarioText.trim()) return;

        setIsLoading(true);
        setError(null);

        try {
            const response = await fetch(
                `http://localhost:8000/api/test-custom-scenario/${analysisId}`,
                {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ scenario_text: scenarioText })
                }
            );

            if (!response.ok) throw new Error('Failed to test scenario');

            const result = await response.json();
            onScenarioAdded(result);
            setScenarioText('');
        } catch (err) {
            setError(err.message);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-5 mt-6">
            <div className="flex items-center gap-2 mb-3">
                <Sparkles className="w-5 h-5 text-purple-600" />
                <h3 className="text-sm font-bold text-slate-900">
                    Test Custom Scenario
                </h3>
            </div>

            <form onSubmit={handleSubmit} className="space-y-3">
                <div className="relative">
                    <textarea
                        value={scenarioText}
                        onChange={(e) => setScenarioText(e.target.value)}
                        placeholder="What if I get cancer and need medical leave?&#10;What happens if we only hit 70% of the earnout target?&#10;What if the company relocates to another state?"
                        className="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-purple-500 focus:ring-2 focus:ring-purple-100 resize-none text-sm"
                        rows={3}
                        disabled={isLoading}
                    />
                </div>

                {error && (
                    <div className="text-xs text-red-600 bg-red-50 px-3 py-2 rounded">
                        {error}
                    </div>
                )}

                <button
                    type="submit"
                    disabled={!scenarioText.trim() || isLoading}
                    className={`
            w-full px-4 py-2.5 rounded-lg font-medium text-sm
            flex items-center justify-center gap-2 transition-all
            ${scenarioText.trim() && !isLoading
                            ? 'bg-gradient-to-r from-purple-600 to-blue-600 text-white hover:shadow-lg'
                            : 'bg-slate-100 text-slate-400 cursor-not-allowed'
                        }
          `}
                >
                    {isLoading ? (
                        <>
                            <Loader2 className="w-4 h-4 animate-spin" />
                            Testing Scenario...
                        </>
                    ) : (
                        <>
                            <Send className="w-4 h-4" />
                            Test This Scenario
                        </>
                    )}
                </button>
            </form>

            <div className="mt-4 pt-4 border-t border-slate-100">
                <div className="text-xs text-slate-500 space-y-1">
                    <p className="font-medium">Example scenarios to try:</p>
                    <ul className="list-disc list-inside space-y-0.5 text-slate-400">
                        <li>Medical emergency requiring extended leave</li>
                        <li>Company acquired but my role eliminated</li>
                        <li>Partial achievement of performance milestones</li>
                    </ul>
                </div>
            </div>
        </div>
    );
}
