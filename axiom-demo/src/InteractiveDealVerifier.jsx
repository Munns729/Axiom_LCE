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
    LayoutTemplate,
    FileUp
} from 'lucide-react';
import { toast } from 'sonner';
import ScenarioTestPanel from './ScenarioTestPanel';
import ContractRenderer from './ContractRenderer';

const InteractiveDealVerifier = () => {
    const [isRunning, setIsRunning] = useState(false);
    const [timelineItems, setTimelineItems] = useState([]);
    const [expandedTrace, setExpandedTrace] = useState(false);
    const [scanComplete, setScanComplete] = useState(false);
    const [expandedScenario, setExpandedScenario] = useState(null);
    const [analyzedDoc, setAnalyzedDoc] = useState(null); // { id, title, tree, analysisId }

    // Tabs state: 'validation' | 'scenarios'
    const [activeTab, setActiveTab] = useState('validation');

    // New state for file upload
    const [file, setFile] = useState(null);
    const [isUploading, setIsUploading] = useState(false);
    const [uploadError, setUploadError] = useState(null);

    const bottomRef = useRef(null);

    // Initial scenario tests - Start Empty
    const [scenarioTestsState, setScenarioTestsState] = useState([]);

    const [progress, setProgress] = useState(0);
    const [progressStatus, setProgressStatus] = useState("Initializing...");

    // Real Analysis Logic
    const startVerification = async () => {
        setIsRunning(true);
        setTimelineItems([]);
        setScenarioTestsState([]);
        setExpandedTrace(false);
        setScanComplete(false);
        setUploadError(null);
        setProgress(0);
        setProgressStatus("Starting...");
        setActiveTab('validation'); // Switch to validation view on start

        toast.info('Starting contract analysis...');

        try {
            if (file) {
                // Use uploaded file - call real STREAMING API
                setIsUploading(true);
                const formData = new FormData();
                formData.append('file', file);

                // Call FastAPI backend
                const response = await fetch('http://localhost:8000/api/analyze-quick-stream', {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.detail || 'Analysis failed');
                }

                setIsUploading(false); // Upload done, now streaming analysis

                // Consume stream
                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                let buffer = '';

                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;

                    const chunk = decoder.decode(value, { stream: true });
                    buffer += chunk;

                    const lines = buffer.split('\n');
                    buffer = lines.pop(); // Keep last partial line

                    for (const line of lines) {
                        if (!line.trim()) continue;

                        try {
                            const event = JSON.parse(line);

                            if (event.type === 'progress') {
                                setProgress(event.percent);
                                setProgressStatus(event.stage);
                            } else if (event.type === 'timeline_step') {
                                setTimelineItems(prev => [...prev, event.data]);
                            } else if (event.type === 'doc_info') {
                                setAnalyzedDoc({
                                    title: event.data.filename,
                                    id: event.data.document_id,
                                    tree: event.data.tree
                                });
                            } else if (event.type === 'result') {
                                const data = event.data;
                                setAnalyzedDoc(prev => ({ ...prev, analysisId: data.analysis_id }));
                                setScenarioTestsState(data.scenarios);
                                setScanComplete(true);
                                setIsRunning(false);
                                toast.success('Analysis complete!');
                            }
                        } catch (e) {
                            console.error("Error parsing JSON line", e);
                        }
                    }
                }

            } else {
                // Demo Mode Removed or Simplified for consistency with user request to remove "draft/fake" analysis
                toast.error("Please upload a document to analyze.");
                setIsRunning(false);
            }

        } catch (error) {
            console.error('Analysis error:', error);
            setUploadError(error.message);
            setIsRunning(false);
            setIsUploading(false);
            toast.error(`Analysis failed: ${error.message}`);
        }
    };

    useEffect(() => {
        if (activeTab === 'validation') {
            bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
        }
    }, [timelineItems, expandedTrace, scanComplete, activeTab]);

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

                        <div className="flex items-center gap-2">
                            <input
                                type="file"
                                accept=".docx,.pdf,.txt"
                                onChange={(e) => {
                                    setFile(e.target.files[0]);
                                    setUploadError(null);
                                    setAnalyzedDoc(null);
                                    setTimelineItems([]);
                                    setScenarioTestsState([]);
                                    setScanComplete(false);
                                    setIsRunning(false);
                                }}
                                className="hidden"
                                id="file-upload"
                            />
                            <label
                                htmlFor="file-upload"
                                className="px-4 py-2 text-sm font-medium text-slate-700 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 cursor-pointer transition-colors"
                            >
                                {file ? `📄 ${file.name.substring(0, 20)}${file.name.length > 20 ? '...' : ''}` : '📁 Upload'}
                            </label>

                            <button
                                onClick={startVerification}
                                disabled={isRunning || isUploading || !file}
                                className={`
                                        relative overflow-hidden group
                                        px-5 py-2.5 rounded-xl font-medium text-sm transition-all duration-300 flex items-center gap-2 shadow-lg
                                        ${isRunning || isUploading || !file
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
                                ) : isUploading ? (
                                    <>
                                        <Clock className="w-4 h-4 animate-spin" />
                                        <span>Uploading...</span>
                                    </>
                                ) : (
                                    <>
                                        <Sparkles className="w-4 h-4 text-blue-100 group-hover:text-white transition-colors" />
                                        <span>Analyze</span>
                                    </>
                                )}
                            </button>
                        </div>
                        {uploadError && (
                            <div className="mt-2 text-xs text-red-600 bg-red-50 px-3 py-1 rounded">
                                ⚠️ {uploadError}
                            </div>
                        )}
                    </div>
                </header>

                {/* Document Canvas */}
                <div className="flex-1 overflow-y-auto relative flex justify-center py-12 px-8 custom-scrollbar bg-slate-100/50">
                    {/* Progress Overlay */}
                    {isRunning && (
                        <div className="fixed top-24 left-1/2 -translate-x-1/2 z-50 bg-white/90 backdrop-blur-md px-6 py-4 rounded-2xl shadow-xl border border-indigo-100 flex flex-col items-center gap-2 min-w-[300px] animate-in fade-in slide-in-from-top-4">
                            <div className="flex items-center justify-between w-full text-xs font-bold text-slate-500 uppercase tracking-wider mb-1">
                                <span>{progressStatus}</span>
                                <span>{Math.round(progress)}%</span>
                            </div>
                            <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
                                <div
                                    className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 transition-all duration-300 ease-out"
                                    style={{ width: `${progress}%` }}
                                />
                            </div>
                        </div>
                    )}

                    {!analyzedDoc ? (
                        // Empty State
                        <div className="flex flex-col items-center justify-center w-full max-w-[850px] min-h-[600px] border-2 border-dashed border-slate-300 rounded-2xl bg-white/50 hover:bg-white transition-colors mt-8">
                            <div className="w-16 h-16 bg-white rounded-full shadow-lg flex items-center justify-center mb-6">
                                <FileUp className="w-8 h-8 text-indigo-500" />
                            </div>
                            <h3 className="text-xl font-bold text-slate-900 mb-2">Upload a Contract to Begin</h3>
                            <p className="text-slate-500 mb-8 text-center max-w-sm">
                                Supported formats: .docx, .pdf, .txt
                            </p>
                            <label
                                htmlFor="file-upload"
                                className="px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-xl shadow-lg shadow-indigo-200 transition-all hover:-translate-y-0.5 cursor-pointer block text-center"
                            >
                                Select Document
                            </label>
                        </div>
                    ) : (
                        // Real Document View - IMPROVED CONTAINER
                        <div className="w-full max-w-[850px] bg-white shadow-lg shadow-slate-200/50 border border-slate-200 min-h-[100vh] p-12 md:p-[96px] relative text-slate-800 font-serif leading-8 text-[1.1rem] rounded-sm transition-all duration-700 mb-20">
                            {/* Document Header */}
                            <div className="mb-16 text-center border-b pb-8 border-slate-100">
                                <h1 className="text-3xl font-bold text-slate-900 mb-3 tracking-tight">{analyzedDoc.title}</h1>
                                <p className="text-slate-400 font-sans text-xs font-medium uppercase tracking-[0.2em]">Analyzed via Axiom Spine</p>
                            </div>

                            <ContractRenderer tree={analyzedDoc.tree} />
                        </div>
                    )}
                </div>
            </div>

            {/* RIGHT SIDE: Validation Assistant (Tabs) */}
            <div className="w-[500px] bg-white border-l border-slate-200 shadow-xl flex flex-col z-30">

                {/* Assistant Header */}
                <div className="h-20 flex items-center justify-between px-6 border-b border-slate-100 bg-white">
                    <div>
                        <h2 className="text-lg font-bold text-slate-800 tracking-tight">Validation Assistant</h2>
                        <p className="text-xs text-slate-500 font-medium mt-0.5">Series A Playbook v3.0</p>
                    </div>
                </div>

                {/* TABS HEADER */}
                <div className="px-6 pt-4 pb-0 border-b border-slate-100 bg-slate-50/50 flex items-center gap-6">
                    <button
                        onClick={() => setActiveTab('validation')}
                        className={`pb-3 text-sm font-medium border-b-2 transition-all ${activeTab === 'validation'
                                ? 'text-indigo-600 border-indigo-600'
                                : 'text-slate-500 border-transparent hover:text-slate-700'
                            }`}
                    >
                        Timeline & Checks
                    </button>
                    <button
                        onClick={() => setActiveTab('scenarios')}
                        className={`pb-3 text-sm font-medium border-b-2 transition-all ${activeTab === 'scenarios'
                                ? 'text-indigo-600 border-indigo-600'
                                : 'text-slate-500 border-transparent hover:text-slate-700'
                            }`}
                    >
                        Scenario Tests
                        {scenarioTestsState.length > 0 && (
                            <span className="ml-2 bg-slate-200 text-slate-600 text-[10px] px-1.5 py-0.5 rounded-full">
                                {scenarioTestsState.length}
                            </span>
                        )}
                    </button>
                </div>

                {/* TAB CONTENT: VALIDATION */}
                {activeTab === 'validation' && (
                    <div className="flex-1 overflow-y-auto p-6 scroll-smooth custom-scrollbar bg-slate-50/30">
                        <div className="relative space-y-6">
                            {/* Continuous Line */}
                            <div className="absolute left-[15px] top-4 bottom-4 w-0.5 bg-slate-200/60 rounded-full"></div>

                            {timelineItems.length === 0 && !isRunning && (
                                <div className="flex flex-col items-center justify-center h-[300px] text-center px-8 text-slate-400">
                                    <Bot className="w-12 h-12 mb-4 opacity-20" />
                                    <p className="text-sm">Upload a document to start validation.</p>
                                </div>
                            )}

                            {timelineItems.map((item) => (
                                <div key={item.id} className="relative flex gap-5 animate-in slide-in-from-bottom-2 fade-in duration-500">
                                    {/* Status Icon */}
                                    <div className="relative z-10 shrink-0">
                                        <div className={`
                                            w-8 h-8 rounded-full border-[3px] border-white shadow-sm flex items-center justify-center
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
                                        <div className="bg-white rounded-xl p-4 shadow-sm border border-slate-100">
                                            <div className="flex items-center justify-between mb-1.5">
                                                <h4 className={`text-sm font-bold ${item.type === 'warning' ? 'text-amber-700' : 'text-slate-900'}`}>{item.title}</h4>
                                                <span className="text-[10px] text-slate-400">{item.timestamp}</span>
                                            </div>
                                            <p className="text-sm text-slate-500 leading-relaxed">
                                                {item.message}
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            ))}
                            <div ref={bottomRef} />
                        </div>
                    </div>
                )}

                {/* TAB CONTENT: SCENARIOS */}
                {activeTab === 'scenarios' && (
                    <div className="flex-1 overflow-y-auto bg-slate-50/30">
                        {scenarioTestsState.length === 0 ? (
                            <div className="flex flex-col items-center justify-center h-full text-center px-8 text-slate-400">
                                <ShieldCheck className="w-12 h-12 mb-4 opacity-20" />
                                <p className="text-sm">Scenarios will be generated after initial analysis.</p>
                            </div>
                        ) : (
                            <div className="p-6">
                                <ScenarioTestPanel
                                    scenarios={scenarioTestsState}
                                    onScenarioClick={setExpandedScenario}
                                    expandedScenarioId={expandedScenario}
                                    analysisId={analyzedDoc?.analysisId}
                                />
                            </div>
                        )}
                    </div>
                )}
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
