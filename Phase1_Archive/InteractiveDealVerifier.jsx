import React, { useState, useEffect, useRef } from 'react';
import {
    Sparkles,
    CheckCircle2,
    AlertTriangle,
    ChevronRight,
    FileText,
    Zap,
    ArrowRight,
    Search,
    Bot,
    MoreHorizontal,
    XCircle,
    Clock,
    ShieldCheck,
    LayoutTemplate
} from 'lucide-react';

const InteractiveDealVerifier = () => {
    const [isRunning, setIsRunning] = useState(false);
    const [timelineItems, setTimelineItems] = useState([]);
    const [expandedTrace, setExpandedTrace] = useState(false);
    const [scanComplete, setScanComplete] = useState(false);
    const bottomRef = useRef(null);

    // "SaaS" Timeline Items
    const steps = [
        {
            id: 1,
            type: 'system',
            title: 'Analysis Started',
            message: 'Processing "Founder Share Option Agreement" against Series A Standard (v4.2).',
            timestamp: 'Just now',
            delay: 200
        },
        {
            id: 2,
            type: 'success',
            title: 'Definitions Verified',
            message: '14 definitions found. No circular dependencies in Section 1.',
            timestamp: '2ms',
            delay: 1200
        },
        {
            id: 3,
            type: 'loading',
            title: 'Analyzing Termination Clauses',
            message: 'Cross-referencing "Cause" (1.2) and "Good Reason" (1.4)...',
            timestamp: 'Processing...',
            delay: 2200
        },
        {
            id: 4,
            type: 'warning',
            title: 'Conflict Detected: Good Reason Override',
            message: 'Section 4.2 classifies "Voluntary Resignation" as "Bad Leaver" without respecting the "Good Reason" safe harbor defined in Section 1.',
            timestamp: '124ms',
            delay: 3500
        },
        {
            id: 5,
            type: 'complete',
            title: 'Verdict: High Risk',
            message: '1 Critical Issue found requiring manual review.',
            timestamp: 'Done',
            delay: 4500
        }
    ];

    const startVerification = () => {
        setIsRunning(true);
        setTimelineItems([]);
        setExpandedTrace(false);
        setScanComplete(false);

        let currentTime = 0;

        // Simulate the stream
        steps.forEach((step, index) => {
            setTimeout(() => {
                if (step.type === 'complete') {
                    setScanComplete(true);
                    setIsRunning(false);
                }

                setTimelineItems(prev => {
                    return [...prev, step];
                });

            }, currentTime + step.delay);
        });
    };

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [timelineItems, expandedTrace]);

    return (
        <div className="flex h-screen w-full bg-slate-50 font-sans text-slate-900 overflow-hidden selection:bg-indigo-100 selection:text-indigo-900">

            {/* LEFT SIDE: Document / Workspace (Modern Word) */}
            <div className="flex-1 flex flex-col border-r border-slate-200 bg-[#F9FAFB] relative transition-all duration-500 linear">

                {/* Modern Word Header */}
                <header className="h-16 bg-white/80 backdrop-blur-md border-b border-slate-200/60 flex items-center justify-between px-8 z-20 sticky top-0">
                    <div className="flex items-center gap-4">
                        <div className="w-10 h-10 bg-indigo-600 rounded-xl flex items-center justify-center shadow-lg shadow-indigo-200">
                            <Sparkles className="w-5 h-5 text-white" />
                        </div>
                        <div className="flex flex-col">
                            <span className="font-bold text-lg text-slate-900 tracking-tight leading-tight">Axiom</span>
                            <span className="text-[11px] font-medium text-slate-400 uppercase tracking-wider">Contract Intelligence</span>
                        </div>
                        <div className="h-6 w-px bg-slate-200 mx-2"></div>
                        <div className="flex items-center gap-2 text-sm text-slate-600 font-medium bg-slate-50 px-3 py-1.5 rounded-lg border border-slate-100">
                            <FileText className="w-4 h-4 text-indigo-500" />
                            Founder_Agreement_v4.docx
                        </div>
                    </div>

                    <div className="flex items-center gap-4">
                        <div className="flex items-center gap-2 text-xs font-medium text-slate-400">
                            <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
                            Autosaved
                        </div>
                        <div className="flex -space-x-2">
                            <div className="w-8 h-8 rounded-full bg-slate-200 border-2 border-white"></div>
                            <div className="w-8 h-8 rounded-full bg-indigo-100 border-2 border-white flex items-center justify-center text-xs font-bold text-indigo-600">+2</div>
                        </div>
                    </div>
                </header>

                {/* Document Canvas */}
                <div className="flex-1 overflow-y-auto relative flex justify-center py-12 px-8 custom-scrollbar">
                    {isRunning && (
                        <div className="fixed top-16 left-0 right-[500px] h-0.5 bg-indigo-500/20 overflow-hidden z-50 pointer-events-none">
                            <div className="h-full bg-gradient-to-r from-transparent via-indigo-600 to-transparent w-1/3 animate-[scanning_1.5s_ease-in-out_infinite]" />
                        </div>
                    )}

                    <div className="w-full max-w-[850px] bg-white shadow-2xl shadow-slate-200/40 border border-slate-100 min-h-[1100px] p-[96px] relative text-slate-800 font-serif leading-8 text-[1.05rem] rounded-lg transition-all duration-700">

                        {/* Document Header */}
                        <div className="mb-20 text-center border-b pb-8 border-slate-100">
                            <h1 className="text-3xl font-bold text-slate-900 mb-3 tracking-tight">Founder Share Option Agreement</h1>
                            <p className="text-slate-400 font-sans text-xs font-medium uppercase tracking-[0.2em]">Execution Version 1.0 • Confidential</p>
                        </div>

                        <div className="space-y-12">
                            <p className="text-justify text-slate-600 first-letter:text-5xl first-letter:font-bold first-letter:text-slate-900 first-letter:mr-2 float-none">
                                <span className="font-semibold text-slate-900">THIS AGREEMENT</span> is made on this day between <span className="font-semibold text-slate-900">[Company Name]</span>, a Delaware corporation (the "Company"), and <span className="font-semibold text-slate-900">[Founder Name]</span> (the "Founder").
                            </p>

                            <div>
                                <div className="flex items-center gap-4 mb-6">
                                    <span className="text-xs font-sans font-bold text-slate-300">01</span>
                                    <h4 className="font-sans text-xs font-bold text-indigo-600 uppercase tracking-widest border-b border-indigo-100 pb-2 flex-1">Definitions</h4>
                                </div>
                                <div className="pl-8 space-y-6">
                                    <p><span className="font-bold text-slate-900">"Cause"</span> shall mean fraud, embezzlement, or gross negligence resulting in material harm to the Company.</p>
                                    <div className="group relative">
                                        <p className="relative z-10 p-2 -mx-2 rounded-lg transition-colors hover:bg-slate-50">
                                            <span className="font-bold text-slate-900">"Good Reason"</span> shall mean a material reduction in base salary or forced relocation of more than 50 miles.
                                        </p>
                                    </div>
                                </div>
                            </div>

                            <div>
                                <div className="flex items-center gap-4 mb-6">
                                    <span className="text-xs font-sans font-bold text-slate-300">04</span>
                                    <h4 className="font-sans text-xs font-bold text-indigo-600 uppercase tracking-widest border-b border-indigo-100 pb-2 flex-1">Termination and Forfeiture</h4>
                                </div>
                                <div className="pl-8 space-y-6">
                                    <p><span className="font-bold text-slate-900">4.1</span> In the event of termination for Cause, all unvested shares shall be forfeited automatically.</p>

                                    <div className={`transition-all duration-700 -mx-6 px-6 py-4 rounded-xl border ${scanComplete
                                            ? 'bg-amber-50/60 border-amber-200 shadow-sm'
                                            : 'border-transparent'
                                        }`}>
                                        <div className="flex gap-4">
                                            <div className="flex-1">
                                                <p className="items-start">
                                                    <span className="font-bold text-slate-900 mr-2">4.2</span>
                                                    If the Founder voluntarily resigns without <span className="font-bold text-slate-900">Good Reason</span>, they shall be considered a <span className="font-bold text-amber-700 bg-amber-100/50 px-1 rounded">Bad Leaver</span> and shall forfeit all vested and unvested shares immediately.
                                                </p>
                                            </div>
                                            {scanComplete && (
                                                <div className="animate-in fade-in slide-in-from-right-4 duration-500 flex items-start pt-1">
                                                    <button
                                                        onClick={() => setExpandedTrace(true)}
                                                        className="group flex items-center gap-2 bg-white pl-2 pr-3 py-1.5 rounded-full border border-amber-200 shadow-sm hover:shadow-md hover:border-amber-300 transition-all"
                                                    >
                                                        <div className="w-5 h-5 rounded-full bg-amber-100 text-amber-600 flex items-center justify-center">
                                                            <AlertTriangle className="w-3 h-3" />
                                                        </div>
                                                        <span className="text-xs font-semibold text-amber-700 group-hover:text-amber-800">Review</span>
                                                    </button>
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

            </div>

            {/* RIGHT SIDE: Validation Assistant (Lovable SaaS) */}
            <div className="w-[500px] bg-gradient-to-br from-slate-50 to-indigo-50/30 border-l border-white/50 shadow-[0_0_50px_rgba(0,0,0,0.04)] ring-1 ring-slate-200/60 flex flex-col z-30 backdrop-blur-sm">

                {/* Assistant Header */}
                <div className="h-20 flex items-center justify-between px-8 bg-white/60 backdrop-blur sticky top-0 z-20 border-b border-slate-100">
                    <div>
                        <h2 className="text-lg font-bold text-slate-800 tracking-tight">Validation Assistant</h2>
                        <p className="text-xs text-slate-500 font-medium mt-0.5">Series A Playbook v3.0</p>
                    </div>
                    <button
                        onClick={startVerification}
                        disabled={isRunning}
                        className={`
                   relative overflow-hidden group
                   px-5 py-2.5 rounded-xl font-medium text-sm transition-all duration-300 flex items-center gap-2 shadow-lg
                   ${isRunning
                                ? 'bg-slate-100 text-slate-400 cursor-not-allowed shadow-none'
                                : 'bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white shadow-blue-500/25 hover:shadow-blue-500/40 hover:-translate-y-0.5'
                            }
                `}
                    >
                        {isRunning ? (
                            <>
                                <Clock className="w-4 h-4 animate-spin" />
                                <span>Running...</span>
                            </>
                        ) : (
                            <>
                                <Sparkles className="w-4 h-4 text-blue-100 group-hover:text-white transition-colors" />
                                <span>Run Check</span>
                            </>
                        )}
                    </button>
                </div>

                {/* Timeline Stream */}
                <div className="flex-1 overflow-y-auto p-8 scroll-smooth custom-scrollbar">
                    <div className="relative space-y-8">

                        {/* Continuous Line */}
                        <div className="absolute left-[15px] top-4 bottom-4 w-0.5 bg-slate-200/60 rounded-full"></div>

                        {timelineItems.length === 0 && !isRunning && (
                            <div className="flex flex-col items-center justify-center h-[400px] text-center px-8 animate-in fade-in duration-700">
                                <div className="w-20 h-20 bg-white rounded-2xl shadow-xl shadow-indigo-100 flex items-center justify-center mb-6 rotate-3 hover:rotate-6 transition-transform duration-500">
                                    <Bot className="w-10 h-10 text-indigo-600" />
                                </div>
                                <h3 className="text-xl font-bold text-slate-900 mb-2">Ready to assist</h3>
                                <p className="text-sm text-slate-500 leading-relaxed max-w-[280px]">
                                    I can analyze this document for logical inconsistencies, definition loops, and risk factors.
                                </p>
                            </div>
                        )}

                        {timelineItems.map((item, idx) => (
                            <div key={item.id} className="relative flex gap-6 animate-in slide-in-from-bottom-4 fade-in duration-500 group">

                                {/* Status Icon */}
                                <div className="relative z-10 shrink-0">
                                    <div className={`
                                w-8 h-8 rounded-full border-[3px] border-white shadow-md flex items-center justify-center transition-transform group-hover:scale-110 duration-300
                                ${item.type === 'warning' ? 'bg-amber-100 text-amber-600' :
                                            item.type === 'success' ? 'bg-emerald-100 text-emerald-600' :
                                                item.type === 'loading' ? 'bg-blue-50 text-blue-600' :
                                                    item.type === 'system' ? 'bg-slate-100 text-slate-500' :
                                                        'bg-indigo-600 text-white'}
                            `}>
                                        {item.type === 'warning' ? <AlertTriangle className="w-4 h-4" /> :
                                            item.type === 'success' ? <CheckCircle2 className="w-4 h-4" /> :
                                                item.type === 'loading' ? <div className="w-2 h-2 rounded-full bg-blue-600 animate-ping" /> :
                                                    <div className="w-2 h-2 rounded-full bg-current opacity-60" />}
                                    </div>
                                </div>

                                {/* Content Card */}
                                <div className="flex-1 min-w-0">
                                    <div className="bg-white rounded-2xl p-5 shadow-sm border border-slate-100 hover:shadow-md transition-all duration-300 group-hover:border-slate-200">
                                        <div className="flex items-center justify-between mb-2">
                                            <h4 className={`text-sm font-bold tracking-tight ${item.type === 'warning' ? 'text-amber-700' : 'text-slate-900'
                                                }`}>
                                                {item.title}
                                            </h4>
                                            <span className="text-[10px] font-medium text-slate-400 bg-slate-50 px-2 py-0.5 rounded-full border border-slate-100">{item.timestamp}</span>
                                        </div>

                                        <p className="text-sm text-slate-500 leading-relaxed font-medium">
                                            {item.message}
                                        </p>

                                        {/* Inline Logic Story Expansion */}
                                        {item.type === 'warning' && (
                                            <div className={`mt-4 border-t border-slate-100/60 overflow-hidden transition-all duration-500 ease-in-out ${expandedTrace ? 'opacity-100' : 'opacity-80'}`}>

                                                {!expandedTrace ? (
                                                    <button
                                                        onClick={() => setExpandedTrace(true)}
                                                        className="w-full mt-2 py-2 flex items-center justify-center gap-2 text-xs font-semibold text-indigo-600 bg-indigo-50/50 hover:bg-indigo-50 rounded-lg transition-colors group/btn"
                                                    >
                                                        <LayoutTemplate className="w-3.5 h-3.5" />
                                                        Analyze Logic Flow
                                                        <ChevronRight className="w-3.5 h-3.5 transition-transform group-hover/btn:translate-x-0.5" />
                                                    </button>
                                                ) : (
                                                    <div className="pt-4 animate-in fade-in slide-in-from-top-2">
                                                        <div className="flex items-end justify-between mb-4">
                                                            <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Causality Trace</span>
                                                            <button onClick={() => setExpandedTrace(false)} className="text-slate-400 hover:text-slate-600 transition-colors">
                                                                <XCircle className="w-4 h-4" />
                                                            </button>
                                                        </div>

                                                        <div className="relative space-y-0">
                                                            <div className="absolute left-[15px] top-2 bottom-6 w-0.5 bg-indigo-100"></div>

                                                            {/* Step 1 */}
                                                            <div className="relative flex gap-4 pb-6">
                                                                <div className="relative z-10 w-8 h-8 rounded-full bg-white border-2 border-slate-200 flex items-center justify-center shrink-0">
                                                                    <div className="w-2 h-2 rounded-full bg-slate-300"></div>
                                                                </div>
                                                                <div>
                                                                    <div className="text-xs font-bold text-slate-700 mb-0.5">Trigger Event</div>
                                                                    <div className="text-sm font-medium text-slate-900 bg-slate-50 px-2 py-1 rounded inline-block border border-slate-100">
                                                                        Founder Resigns Voluntarily
                                                                    </div>
                                                                </div>
                                                            </div>

                                                            {/* Step 2 */}
                                                            <div className="relative flex gap-4 pb-6">
                                                                <div className="relative z-10 w-8 h-8 rounded-full bg-amber-50 border-2 border-amber-200 flex items-center justify-center shrink-0">
                                                                    <AlertTriangle className="w-3.5 h-3.5 text-amber-500" />
                                                                </div>
                                                                <div>
                                                                    <div className="text-xs font-bold text-amber-600 mb-0.5">Definition Trap</div>
                                                                    <div className="text-sm text-slate-600">
                                                                        Categorized as <span className="font-bold text-amber-700">"Bad Leaver"</span>
                                                                    </div>
                                                                    <div className="text-xs text-amber-600/80 mt-1 pl-2 border-l-2 border-amber-200">
                                                                        ⚠ Bypasses Section 1.4 Protection
                                                                    </div>
                                                                </div>
                                                            </div>

                                                            {/* Step 3 */}
                                                            <div className="relative flex gap-4">
                                                                <div className="relative z-10 w-8 h-8 rounded-full bg-indigo-600 border-4 border-indigo-100 flex items-center justify-center shrink-0 shadow-sm">
                                                                    <CheckCircle2 className="w-3.5 h-3.5 text-white" />
                                                                </div>
                                                                <div>
                                                                    <div className="text-xs font-bold text-indigo-600 mb-0.5">Outcome</div>
                                                                    <div className="text-sm font-bold text-slate-900 shadow-sm bg-white px-3 py-1.5 rounded-lg border border-slate-100 ring-1 ring-indigo-50 inline-block">
                                                                        Forfeit All Shares
                                                                    </div>
                                                                </div>
                                                            </div>
                                                        </div>
                                                    </div>
                                                )}
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </div>
                        ))}
                        <div ref={bottomRef} />
                    </div>
                </div>
            </div>
            <style>{`
        @keyframes scanning {
          0% { left: -10%; opacity: 0; }
          20% { opacity: 1; }
          80% { opacity: 1; }
          100% { left: 110%; opacity: 0; }
        }
      `}</style>
        </div>
    );
};

export default InteractiveDealVerifier;
