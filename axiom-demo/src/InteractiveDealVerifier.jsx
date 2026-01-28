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
    FileUp,
    Download,
    BookOpen,
    Send
} from 'lucide-react';
import { toast } from 'sonner';
import ScenarioTestPanel from './ScenarioTestPanel';
import ContractRenderer from './ContractRenderer';
import LogicCircuit from './LogicCircuit';
import AssertionInput from './AssertionInput';
import LogicTraceVisualization from './LogicTraceVisualization';

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
    const [isExporting, setIsExporting] = useState(false);
    const [isDragging, setIsDragging] = useState(false);

    const bottomRef = useRef(null);

    // Initial scenario tests - Start Empty
    const [scenarioTestsState, setScenarioTestsState] = useState([]);
    const [definitionsState, setDefinitionsState] = useState([]);

    // Chat state
    const [chatHistory, setChatHistory] = useState([]);
    const [chatInput, setChatInput] = useState('');
    const [isChatLoading, setIsChatLoading] = useState(false);
    const chatEndRef = useRef(null);

    // Verification state
    const [isVerifying, setIsVerifying] = useState(false);
    const [verificationResult, setVerificationResult] = useState(null);
    const [verificationTimeline, setVerificationTimeline] = useState([]);

    const scrollToBottom = () => {
        chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [chatHistory, activeTab]);

    const handleSendMessage = async (e) => {
        e.preventDefault();
        if (!chatInput.trim() || isChatLoading) return;

        const userMessage = { role: 'user', content: chatInput };
        setChatHistory(prev => [...prev, userMessage]);
        setChatInput('');
        setIsChatLoading(true);

        try {
            const response = await fetch('http://localhost:8000/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    question: userMessage.content,
                    document_id: analyzedDoc?.id,
                    analysis_id: analyzedDoc?.analysisId,
                    chat_history: chatHistory.map(msg => ({
                        question: msg.role === 'user' ? msg.content : '',
                        answer: msg.role === 'assistant' ? msg.content : ''
                    })).filter(msg => msg.question || msg.answer)
                })
            });

            if (!response.ok) throw new Error('Failed to get answer');

            const data = await response.json();
            const botMessage = {
                role: 'assistant',
                content: data.answer,
                sections: data.sections,
                confidence: data.confidence
            };
            setChatHistory(prev => [...prev, botMessage]);
        } catch (error) {
            console.error('Chat error:', error);
            setChatHistory(prev => [...prev, {
                role: 'assistant',
                content: 'I apologize, but I encountered an error while analyzing the document using Berty AI. Please try again.',
                isError: true
            }]);
        } finally {
            setIsChatLoading(false);
        }
    };

    // Verification Handler
    const handleVerifyAssertion = async (assertionText) => {
        if (!analyzedDoc?.id) {
            toast.error('Please analyze a document first');
            return;
        }

        setIsVerifying(true);
        setVerificationTimeline([]);
        setVerificationResult(null);
        setActiveTab('verify');

        toast.info('Verifying assertion...');

        try {
            const response = await fetch(`http://localhost:8000/api/verify-assertion/${analyzedDoc.id}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ assertion_text: assertionText })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Verification failed');
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value, { stream: true });
                buffer += chunk;

                const lines = buffer.split('\n');
                buffer = lines.pop();

                for (const line of lines) {
                    if (!line.trim()) continue;

                    try {
                        const event = JSON.parse(line);

                        if (event.type === 'error') {
                            throw new Error(event.message || 'Verification error');
                        } else if (event.type === 'thinking') {
                            setVerificationTimeline(prev => [...prev, {
                                type: 'thinking',
                                message: event.message,
                                timestamp: event.timestamp
                            }]);
                        } else if (event.type === 'entity_found') {
                            setVerificationTimeline(prev => [...prev, {
                                type: 'entity',
                                entity: event.entity,
                                location: event.location,
                                timestamp: event.timestamp
                            }]);
                        } else if (event.type === 'trace') {
                            setVerificationResult(prev => ({
                                ...prev,
                                logicTrace: event.chain
                            }));
                        } else if (event.type === 'conflict') {
                            setVerificationResult(prev => ({
                                ...prev,
                                hasConflict: true,
                                conflictDetails: event.details,
                                conflictSeverity: event.severity,
                                conflictingClauses: event.conflicting_clauses
                            }));
                            toast.warning('Logic conflict detected!');
                        } else if (event.type === 'complete') {
                            setVerificationResult(prev => ({
                                ...prev,
                                verdict: event.verdict,
                                summary: event.summary,
                                details: event.details,
                                actualOutcome: event.actual_outcome,
                                expectedOutcome: event.expected_outcome,
                                logicTrace: event.logic_trace,
                                parsedAssertion: event.parsed_assertion,
                                verificationId: event.verification_id
                            }));
                            setIsVerifying(false);

                            if (event.verdict === 'pass') {
                                toast.success('Assertion verified successfully!');
                            } else if (event.verdict === 'warning') {
                                toast.warning('Verified with caveats');
                            } else if (event.verdict === 'fail') {
                                toast.error('Assertion failed verification');
                            } else {
                                toast.info('Verification complete');
                            }
                        }
                    } catch (e) {
                        console.error("Error parsing verification event", e);
                    }
                }
            }

        } catch (error) {
            console.error('Verification error:', error);
            toast.error(`Verification failed: ${error.message}`);
            setIsVerifying(false);
        }
    };


    const [progress, setProgress] = useState(0);
    const [progressStatus, setProgressStatus] = useState("Initializing...");

    const handleScenarioAdded = (newScenario) => {
        setScenarioTestsState(prev => [...prev, newScenario]);
        toast.success('Custom scenario added!');
    };

    // Drag and drop handlers
    const handleDragEnter = (e) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(true);
    };

    const handleDragLeave = (e) => {
        e.preventDefault();
        e.stopPropagation();
        // Only set to false if we're leaving the drop zone entirely
        if (e.currentTarget.contains(e.relatedTarget)) return;
        setIsDragging(false);
    };

    const handleDragOver = (e) => {
        e.preventDefault();
        e.stopPropagation();
    };

    const handleDrop = (e) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(false);

        const files = e.dataTransfer.files;
        if (files && files.length > 0) {
            const droppedFile = files[0];
            const validTypes = ['.docx', '.pdf', '.txt'];
            const fileExt = '.' + droppedFile.name.split('.').pop().toLowerCase();

            if (!validTypes.includes(fileExt)) {
                toast.error('Please upload a .docx, .pdf, or .txt file');
                return;
            }

            setFile(droppedFile);
            setUploadError(null);
            setAnalyzedDoc(null);
            setTimelineItems([]);
            setScenarioTestsState([]);
            setScanComplete(false);
            setIsRunning(false);
            toast.success(`File "${droppedFile.name}" ready for analysis`);
        }
    };

    // Export handler
    const handleExport = async () => {
        if (!analyzedDoc?.id) {
            toast.error('No document to export');
            return;
        }

        setIsExporting(true);
        try {
            const response = await fetch(`http://localhost:8000/api/documents/${analyzedDoc.id}/export`);

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Export failed');
            }

            // Get the blob and download
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = analyzedDoc.title || 'document.docx';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            toast.success('Document exported successfully!');
        } catch (error) {
            console.error('Export error:', error);
            toast.error(`Export failed: ${error.message}`);
        } finally {
            setIsExporting(false);
        }
    };

    // Real Analysis Logic
    const startVerification = async () => {
        setIsRunning(true);
        setTimelineItems([]);
        setScenarioTestsState([]);
        setDefinitionsState([]);
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

                            if (event.type === 'error') {
                                throw new Error(event.message || 'Analysis reported an error');
                            } else if (event.type === 'progress') {
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
                                setAnalyzedDoc(prev => ({
                                    ...prev,
                                    analysisId: data.analysis_id,
                                    conflictAnalysis: data.conflict_analysis
                                }));
                                setScenarioTestsState(data.scenarios || []);
                                setDefinitionsState(data.definitions || []);
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

                            {/* Export Button */}
                            {analyzedDoc && (
                                <button
                                    onClick={handleExport}
                                    disabled={isExporting || isRunning}
                                    className={`
                                        px-4 py-2.5 rounded-xl font-medium text-sm transition-all duration-300 flex items-center gap-2
                                        ${isExporting || isRunning
                                            ? 'bg-slate-100 text-slate-400 cursor-not-allowed'
                                            : 'bg-emerald-600 hover:bg-emerald-700 text-white shadow-lg shadow-emerald-200 hover:-translate-y-0.5'
                                        }
                                    `}
                                >
                                    {isExporting ? (
                                        <>
                                            <Clock className="w-4 h-4 animate-spin" />
                                            <span>Exporting...</span>
                                        </>
                                    ) : (
                                        <>
                                            <Download className="w-4 h-4" />
                                            <span>Export</span>
                                        </>
                                    )}
                                </button>
                            )}
                        </div>
                        {uploadError && (
                            <div className="mt-2 text-xs text-red-600 bg-red-50 px-3 py-1 rounded">
                                ⚠️ {uploadError}
                            </div>
                        )}
                    </div>
                </header>

                {/* Document Canvas */}
                <div className="flex-1 overflow-y-auto relative py-6 px-4 custom-scrollbar bg-slate-100/50">
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
                        // Empty State - Drop Zone
                        <div
                            className={`flex flex-col items-center justify-center w-full max-w-[900px] mx-auto min-h-[500px] border-2 border-dashed rounded-2xl transition-all duration-200 mt-4 ${isDragging
                                ? 'border-indigo-500 bg-indigo-50 scale-[1.02]'
                                : 'border-slate-300 bg-white/50 hover:bg-white hover:border-slate-400'
                                }`}
                            onDragEnter={handleDragEnter}
                            onDragLeave={handleDragLeave}
                            onDragOver={handleDragOver}
                            onDrop={handleDrop}
                        >
                            <div className={`w-16 h-16 rounded-full shadow-lg flex items-center justify-center mb-6 transition-colors ${uploadError ? 'bg-red-100' : isDragging ? 'bg-indigo-100' : 'bg-white'}`}>
                                {uploadError ? (
                                    <AlertTriangle className="w-8 h-8 text-red-500" />
                                ) : (
                                    <FileUp className={`w-8 h-8 transition-colors ${isDragging ? 'text-indigo-600' : 'text-indigo-500'}`} />
                                )}
                            </div>

                            {uploadError ? (
                                <>
                                    <h3 className="text-xl font-bold text-red-700 mb-2">
                                        Analysis Failed
                                    </h3>
                                    <p className="text-red-600/80 mb-8 text-center max-w-sm">
                                        {uploadError}
                                    </p>
                                    <div className="flex gap-3">
                                        <button
                                            onClick={() => { setUploadError(null); setFile(null); }}
                                            className="px-6 py-3 bg-white hover:bg-slate-50 text-slate-700 font-bold rounded-xl border border-slate-200 shadow-sm transition-all"
                                        >
                                            Reset
                                        </button>
                                        {file && (
                                            <button
                                                onClick={startVerification}
                                                className="px-6 py-3 bg-red-600 hover:bg-red-700 text-white font-bold rounded-xl shadow-lg shadow-red-200 transition-all hover:-translate-y-0.5"
                                            >
                                                Retry Analysis
                                            </button>
                                        )}
                                    </div>
                                </>
                            ) : (
                                <>
                                    <h3 className="text-xl font-bold text-slate-900 mb-2">
                                        {isDragging ? 'Drop your file here!' : 'Upload a Contract to Begin'}
                                    </h3>
                                    <p className="text-slate-500 mb-8 text-center max-w-sm">
                                        {isDragging ? 'Release to upload' : 'Drag & drop or click to select • .docx, .pdf, .txt'}
                                    </p>
                                    {!isDragging && (
                                        <label
                                            htmlFor="file-upload"
                                            className="px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-xl shadow-lg shadow-indigo-200 transition-all hover:-translate-y-0.5 cursor-pointer block text-center"
                                        >
                                            Select Document
                                        </label>
                                    )}
                                </>
                            )}
                        </div>
                    ) : (
                        // Real Document View - IMPROVED CONTAINER
                        <div className="w-full max-w-[1000px] mx-auto bg-white shadow-lg shadow-slate-200/50 border border-slate-200 min-h-full p-6 md:p-10 relative text-slate-800 font-serif leading-7 text-base rounded-sm transition-all duration-700 mb-8">
                            {/* Document Header */}
                            <div className="mb-8 text-center border-b pb-4 border-slate-100">
                                <h1 className="text-2xl font-bold text-slate-900 mb-2 tracking-tight">{analyzedDoc.title}</h1>
                                <p className="text-slate-400 font-sans text-xs font-medium uppercase tracking-[0.2em]">Analyzed via Axiom Spine</p>
                            </div>

                            <ContractRenderer
                                tree={analyzedDoc.tree}
                                conflictAnalysis={analyzedDoc.conflictAnalysis}
                            />
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
                    <button
                        onClick={() => setActiveTab('definitions')}
                        className={`pb-3 text-sm font-medium border-b-2 transition-all ${activeTab === 'definitions'
                            ? 'text-indigo-600 border-indigo-600'
                            : 'text-slate-500 border-transparent hover:text-slate-700'
                            }`}
                    >
                        Definitions
                        {definitionsState.length > 0 && (
                            <span className="ml-2 bg-emerald-100 text-emerald-600 text-[10px] px-1.5 py-0.5 rounded-full">
                                {definitionsState.length}
                            </span>
                        )}
                    </button>
                    <button
                        onClick={() => setActiveTab('chat')}
                        className={`pb-3 text-sm font-medium border-b-2 transition-all ${activeTab === 'chat'
                            ? 'text-indigo-600 border-indigo-600'
                            : 'text-slate-500 border-transparent hover:text-slate-700'
                            }`}
                    >
                        Berty AI
                        <span className="ml-2 bg-indigo-100 text-indigo-600 text-[10px] px-1.5 py-0.5 rounded-full">
                            Beta
                        </span>
                    </button>
                    <button
                        onClick={() => setActiveTab('circuit')}
                        className={`pb-3 text-sm font-medium border-b-2 transition-all ${activeTab === 'circuit'
                            ? 'text-indigo-600 border-indigo-600'
                            : 'text-slate-500 border-transparent hover:text-slate-700'
                            }`}
                    >
                        Logic Circuit
                        {analyzedDoc?.conflictAnalysis?.has_conflict && (
                            <span className="ml-2 bg-amber-100 text-amber-600 text-[10px] px-1.5 py-0.5 rounded-full">
                                ⚡
                            </span>
                        )}
                    </button>
                    <button
                        onClick={() => setActiveTab('verify')}
                        className={`pb-3 text-sm font-medium border-b-2 transition-all ${activeTab === 'verify'
                            ? 'text-indigo-600 border-indigo-600'
                            : 'text-slate-500 border-transparent hover:text-slate-700'
                            }`}
                    >
                        Verify Assertion
                        {verificationResult?.verdict && (
                            <span className={`ml-2 text-[10px] px-1.5 py-0.5 rounded-full ${verificationResult.verdict === 'pass'
                                ? 'bg-emerald-100 text-emerald-600'
                                : 'bg-red-100 text-red-600'
                                }`}>
                                {verificationResult.verdict === 'pass' ? '✓' : '✗'}
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
                                    onScenarioAdded={handleScenarioAdded}
                                />
                            </div>
                        )}
                    </div>
                )}

                {/* TAB CONTENT: DEFINITIONS */}
                {activeTab === 'definitions' && (
                    <div className="flex-1 overflow-y-auto p-6 bg-slate-50/30 custom-scrollbar">
                        {definitionsState.length === 0 ? (
                            <div className="flex flex-col items-center justify-center h-full text-center px-8 text-slate-400">
                                <BookOpen className="w-12 h-12 mb-4 opacity-20" />
                                <p className="text-sm">Definitions will be extracted after analysis.</p>
                            </div>
                        ) : (() => {
                            // Group definitions by category
                            const categoryConfig = {
                                parties: { label: 'Parties & Entities', icon: '👥', color: 'blue' },
                                financial: { label: 'Financial Terms', icon: '💰', color: 'green' },
                                time: { label: 'Time & Deadlines', icon: '⏰', color: 'orange' },
                                conditions: { label: 'Conditions & Events', icon: '⚡', color: 'purple' },
                                equity: { label: 'Equity & Ownership', icon: '📊', color: 'indigo' },
                                general: { label: 'General Terms', icon: '📋', color: 'slate' }
                            };

                            const grouped = definitionsState.reduce((acc, def) => {
                                const cat = def.category || 'general';
                                if (!acc[cat]) acc[cat] = [];
                                acc[cat].push(def);
                                return acc;
                            }, {});

                            const categoryOrder = ['parties', 'conditions', 'equity', 'financial', 'time', 'general'];

                            return (
                                <div className="space-y-6">
                                    <div className="flex items-center gap-2 mb-2">
                                        <BookOpen className="w-5 h-5 text-emerald-600" />
                                        <h3 className="font-bold text-slate-800">Contract Glossary</h3>
                                        <span className="text-xs text-slate-500">({definitionsState.length} terms)</span>
                                    </div>

                                    {categoryOrder.map(category => {
                                        const defs = grouped[category];
                                        if (!defs || defs.length === 0) return null;

                                        const config = categoryConfig[category] || categoryConfig.general;

                                        return (
                                            <div key={category} className="space-y-2">
                                                <div className="flex items-center gap-2 py-2 border-b border-slate-200">
                                                    <span className="text-lg">{config.icon}</span>
                                                    <h4 className="font-semibold text-slate-700 text-sm">{config.label}</h4>
                                                    <span className="text-xs bg-slate-100 text-slate-600 px-2 py-0.5 rounded-full">{defs.length}</span>
                                                </div>

                                                <div className="space-y-2 pl-1">
                                                    {defs.map((def, index) => (
                                                        <div key={index} className="bg-white rounded-lg p-3 shadow-sm border border-slate-100 hover:border-slate-200 transition-colors">
                                                            <div className="flex items-start gap-2">
                                                                <div className="flex-1 min-w-0">
                                                                    <h5 className="font-bold text-slate-900 text-sm">
                                                                        "{def.term || 'Unknown Term'}"
                                                                    </h5>
                                                                    <p className="text-sm text-slate-600 leading-relaxed mt-1">
                                                                        {def.definition || def.meaning || 'No definition provided'}
                                                                    </p>
                                                                    {def.section && (
                                                                        <p className="text-xs text-slate-400 mt-1.5">
                                                                            §{def.section}
                                                                        </p>
                                                                    )}
                                                                </div>
                                                            </div>
                                                        </div>
                                                    ))}
                                                </div>
                                            </div>
                                        );
                                    })}
                                </div>
                            );
                        })()}
                    </div>
                )}

                {/* TAB CONTENT: BERTY AI CHAT */}
                {activeTab === 'chat' && (
                    <div className="flex-1 flex flex-col bg-slate-50/30 h-full overflow-hidden">
                        {/* Chat Messages */}
                        <div className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar">
                            {chatHistory.length === 0 ? (
                                <div className="flex flex-col items-center justify-center h-full text-center px-8 text-slate-400">
                                    <Bot className="w-12 h-12 mb-4 opacity-20 text-indigo-500" />
                                    <h4 className="text-slate-700 font-semibold mb-1">Ask Berty AI</h4>
                                    <p className="text-sm">Ask questions about clauses, risks, or terms.</p>
                                    <div className="mt-6 space-y-2 w-full max-w-xs">
                                        <button
                                            onClick={() => setChatInput("What are the termination conditions?")}
                                            className="w-full p-2 text-xs bg-white border border-slate-200 rounded-lg hover:border-indigo-300 hover:text-indigo-600 transition-colors text-left"
                                        >
                                            "What are the termination conditions?"
                                        </button>
                                        <button
                                            onClick={() => setChatInput("Identify any unusual liability caps.")}
                                            className="w-full p-2 text-xs bg-white border border-slate-200 rounded-lg hover:border-indigo-300 hover:text-indigo-600 transition-colors text-left"
                                        >
                                            "Identify any unusual liability caps."
                                        </button>
                                    </div>
                                </div>
                            ) : (
                                chatHistory.map((msg, idx) => (
                                    <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                                        <div className={`max-w-[85%] rounded-2xl p-3.5 shadow-sm text-sm leading-relaxed ${msg.role === 'user'
                                            ? 'bg-indigo-600 text-white rounded-tr-sm'
                                            : 'bg-white border border-slate-100 text-slate-700 rounded-tl-sm'
                                            }`}>
                                            <p className="whitespace-pre-wrap">{msg.content}</p>
                                            {msg.sections && msg.sections.length > 0 && (
                                                <div className="mt-3 flex flex-wrap gap-1.5">
                                                    {msg.sections.map(sec => (
                                                        <span key={sec} className="bg-slate-100 text-slate-500 text-[10px] px-1.5 py-0.5 rounded border border-slate-200">
                                                            §{sec}
                                                        </span>
                                                    ))}
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                ))
                            )}
                            {isChatLoading && (
                                <div className="flex justify-start">
                                    <div className="bg-white border border-slate-100 rounded-2xl rounded-tl-sm p-4 shadow-sm flex items-center gap-2">
                                        <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                                        <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                                        <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce"></div>
                                    </div>
                                </div>
                            )}
                            <div ref={chatEndRef} />
                        </div>

                        {/* Chat Input */}
                        <div className="p-4 bg-white border-t border-slate-100">
                            <form onSubmit={handleSendMessage} className="relative">
                                <input
                                    type="text"
                                    value={chatInput}
                                    onChange={(e) => setChatInput(e.target.value)}
                                    placeholder="Ask anything about this document..."
                                    className="w-full pl-4 pr-12 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 transition-all text-sm placeholder:text-slate-400"
                                    disabled={isChatLoading || !analyzedDoc}
                                />
                                <button
                                    type="submit"
                                    disabled={!chatInput.trim() || isChatLoading || !analyzedDoc}
                                    className="absolute right-2 top-2 p-1.5 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:hover:bg-indigo-600 transition-colors"
                                >
                                    <Send className="w-4 h-4" />
                                </button>
                            </form>
                        </div>
                    </div>
                )}

                {/* TAB CONTENT: LOGIC CIRCUIT */}
                {activeTab === 'circuit' && (
                    <div className="flex-1 overflow-hidden">
                        <LogicCircuit
                            conflictAnalysis={analyzedDoc?.conflictAnalysis}
                            onNodeClick={(sectionRef) => {
                                // Scroll to clause in document
                                const element = document.getElementById(`clause_${sectionRef.replace('.', '_')}`);
                                if (element) {
                                    element.scrollIntoView({ behavior: 'smooth', block: 'center' });
                                }
                            }}
                        />
                    </div>
                )}

                {/* TAB CONTENT: VERIFY ASSERTION */}
                {activeTab === 'verify' && (
                    <div className="flex-1 overflow-y-auto p-6 bg-slate-50/30">
                        <AssertionInput
                            onVerify={handleVerifyAssertion}
                            isVerifying={isVerifying}
                            documentId={analyzedDoc?.id}
                        />

                        {/* Verification Timeline */}
                        {verificationTimeline.length > 0 && (
                            <div className="mt-6 bg-white rounded-lg p-4 shadow-sm">
                                <h4 className="text-sm font-semibold text-slate-700 mb-3">Verification Progress</h4>
                                <div className="space-y-2">
                                    {verificationTimeline.map((item, idx) => (
                                        <div key={idx} className="flex items-start gap-2 text-sm">
                                            {item.type === 'thinking' && (
                                                <>
                                                    <span className="text-indigo-500 mt-0.5">💭</span>
                                                    <span className="text-slate-600">{item.message}</span>
                                                </>
                                            )}
                                            {item.type === 'entity' && (
                                                <>
                                                    <span className="text-emerald-500 mt-0.5">✓</span>
                                                    <span className="text-slate-700">
                                                        Found <strong>{item.entity}</strong> → {item.location?.substring(0, 60)}
                                                    </span>
                                                </>
                                            )}
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Verification Result Summary */}
                        {verificationResult?.verdict && (
                            <div className={`mt-6 rounded-lg p-4 shadow-sm ${verificationResult.verdict === 'pass'
                                ? 'bg-emerald-50 border border-emerald-200'
                                : verificationResult.verdict === 'warning'
                                    ? 'bg-amber-50 border border-amber-200'
                                    : 'bg-red-50 border border-red-200'
                                }`}>
                                <div className="flex items-start gap-3">
                                    <span className="text-2xl">
                                        {verificationResult.verdict === 'pass' ? '✅' :
                                            verificationResult.verdict === 'warning' ? '⚠️' : '❌'}
                                    </span>
                                    <div className="flex-1">
                                        <h4 className={`font-semibold mb-1 ${verificationResult.verdict === 'pass' ? 'text-emerald-900' :
                                            verificationResult.verdict === 'warning' ? 'text-amber-900' : 'text-red-900'
                                            }`}>
                                            {verificationResult.verdict === 'pass' ? 'Assertion Verified' :
                                                verificationResult.verdict === 'warning' ? 'Verified with Caveats' : 'Assertion Failed'}
                                        </h4>
                                        <p className={`text-sm ${verificationResult.verdict === 'pass' ? 'text-emerald-700' :
                                                verificationResult.verdict === 'warning' ? 'text-amber-700' : 'text-red-700'
                                            }`}>
                                            {verificationResult.summary}
                                        </p>

                                        {(verificationResult.details || verificationResult.actualOutcome) && (
                                            <div className="mt-3 pt-3 border-t border-black/5 space-y-3">
                                                {verificationResult.details && (
                                                    <div>
                                                        <h5 className="text-xs font-bold uppercase tracking-wider opacity-60 mb-1">Detailed Reasoning</h5>
                                                        <p className="text-sm italic">{verificationResult.details}</p>
                                                    </div>
                                                )}

                                                <div className="grid grid-cols-2 gap-4 pt-2">
                                                    {verificationResult.expectedOutcome && (
                                                        <div className="bg-white/40 rounded p-2">
                                                            <h5 className="text-[10px] font-bold uppercase tracking-wider opacity-50 mb-1 text-slate-500">Assertion Expected</h5>
                                                            <p className="text-xs font-semibold text-slate-700">{verificationResult.expectedOutcome}</p>
                                                        </div>
                                                    )}
                                                    {verificationResult.actualOutcome && (
                                                        <div className="bg-white/60 rounded p-2 border border-black/5">
                                                            <h5 className="text-[10px] font-bold uppercase tracking-wider opacity-50 mb-1 text-slate-500">Contract Outcome</h5>
                                                            <p className="text-xs font-bold text-slate-900">{verificationResult.actualOutcome}</p>
                                                        </div>
                                                    )}
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </div>
                        )}

                        {/* Logic Trace Visualization */}
                        {verificationResult?.logicTrace && (
                            <div className="mt-6">
                                <LogicTraceVisualization
                                    logicTrace={verificationResult.logicTrace}
                                    verdict={verificationResult.verdict}
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
