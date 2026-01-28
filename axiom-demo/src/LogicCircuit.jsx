import React, { useState, useCallback } from 'react';
import ReactFlow, {
    Background,
    Controls,
    MiniMap,
    useNodesState,
    useEdgesState
} from 'reactflow';
import 'reactflow/dist/style.css';
import { AlertTriangle, Zap, Shield, FileText, Maximize2, Minimize2 } from 'lucide-react';

// Custom Node Component
const ClauseNode = ({ data }) => {
    const getNodeStyle = () => {
        const baseStyle = "px-4 py-3 rounded-lg border-2 shadow-md transition-all";

        if (data.is_conflict_node) {
            return `${baseStyle} border-red-400 bg-red-50 animate-pulse`;
        }

        switch (data.type) {
            case 'definition':
                return `${baseStyle} border-purple-400 bg-purple-50`;
            case 'condition':
                return `${baseStyle} border-amber-400 bg-amber-50`;
            case 'consequence':
                return `${baseStyle} border-red-300 bg-red-50`;
            case 'protection':
                return `${baseStyle} border-emerald-400 bg-emerald-50`;
            default:
                return `${baseStyle} border-slate-300 bg-white`;
        }
    };

    const getIcon = () => {
        switch (data.type) {
            case 'definition': return <FileText className="w-4 h-4" />;
            case 'condition': return <Zap className="w-4 h-4" />;
            case 'consequence': return <AlertTriangle className="w-4 h-4" />;
            case 'protection': return <Shield className="w-4 h-4" />;
            default: return null;
        }
    };

    return (
        <div className={getNodeStyle()}>
            <div className="flex items-center gap-2 mb-1">
                {getIcon()}
                <div className="font-bold text-sm text-slate-900">{data.label}</div>
            </div>
            {data.section_ref && (
                <div className="text-xs text-slate-500">§{data.section_ref}</div>
            )}
            {data.is_implicit && (
                <div className="text-xs text-red-600 font-semibold mt-1">⚠️ Missing</div>
            )}
        </div>
    );
};

const nodeTypes = {
    clauseNode: ClauseNode
};

const LogicCircuit = ({ conflictAnalysis, onNodeClick }) => {
    const [isExpanded, setIsExpanded] = useState(false);
    const [nodes, setNodes, onNodesChange] = useNodesState([]);
    const [edges, setEdges, onEdgesChange] = useEdgesState([]);
    const [isLoading, setIsLoading] = useState(false);

    // Generate graph from conflict analysis
    const generateGraph = useCallback(async () => {
        if (!conflictAnalysis?.has_conflict) return;

        setIsLoading(true);

        try {
            // Call backend to generate logic graph
            const response = await fetch(`/api/logic-graph`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    conflict_analysis: conflictAnalysis,
                    expand: isExpanded
                })
            });

            const data = await response.json();

            // Convert backend graph to React Flow format
            const flowNodes = data.graph.nodes.map((node, idx) => ({
                id: node.id,
                type: 'clauseNode',
                position: { x: 250 * (idx % 3), y: 150 * Math.floor(idx / 3) },
                data: node
            }));

            const flowEdges = data.graph.edges.map((edge, idx) => ({
                id: `edge-${idx}`,
                source: edge.from,
                target: edge.to,
                label: edge.label,
                type: edge.is_conflict_edge ? 'step' : 'smoothstep',
                animated: edge.is_conflict_edge,
                style: {
                    stroke: edge.is_conflict_edge ? '#ef4444' : '#94a3b8',
                    strokeWidth: edge.is_conflict_edge ? 3 : 2
                },
                markerEnd: {
                    type: 'arrowclosed',
                    color: edge.is_conflict_edge ? '#ef4444' : '#94a3b8'
                }
            }));

            setNodes(flowNodes);
            setEdges(flowEdges);
        } catch (error) {
            console.error('Failed to generate logic graph:', error);
        } finally {
            setIsLoading(false);
        }
    }, [conflictAnalysis, isExpanded, setNodes, setEdges]);

    // Load graph on mount or when expand changes
    React.useEffect(() => {
        if (conflictAnalysis?.has_conflict) {
            generateGraph();
        }
    }, [conflictAnalysis, isExpanded, generateGraph]);

    const handleNodeClick = useCallback((event, node) => {
        if (onNodeClick && node.data.section_ref) {
            onNodeClick(node.data.section_ref);
        }
    }, [onNodeClick]);

    if (!conflictAnalysis?.has_conflict) {
        return (
            <div className="flex flex-col items-center justify-center h-full text-center px-8 text-slate-400">
                <Zap className="w-12 h-12 mb-4 opacity-20" />
                <p className="text-sm">No logic conflicts detected.</p>
                <p className="text-xs mt-2">The Logic Circuit will appear here when conflicts are found.</p>
            </div>
        );
    }

    return (
        <div className="flex flex-col h-full">
            {/* Header */}
            <div className="p-4 border-b border-slate-200 bg-white">
                <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                        <AlertTriangle className="w-5 h-5 text-amber-600" />
                        <h3 className="font-bold text-slate-900">
                            {conflictAnalysis.conflict_type?.replace(/_/g, ' ').toUpperCase() || 'Logic Conflict'}
                        </h3>
                        <span className={`text-xs px-2 py-0.5 rounded-full font-semibold ${conflictAnalysis.severity === 'high' ? 'bg-red-100 text-red-700' :
                                conflictAnalysis.severity === 'medium' ? 'bg-amber-100 text-amber-700' :
                                    'bg-slate-100 text-slate-600'
                            }`}>
                            {conflictAnalysis.severity?.toUpperCase() || 'MEDIUM'} RISK
                        </span>
                    </div>
                    <button
                        onClick={() => setIsExpanded(!isExpanded)}
                        className="flex items-center gap-1 px-3 py-1.5 text-xs bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors"
                    >
                        {isExpanded ? <Minimize2 className="w-3 h-3" /> : <Maximize2 className="w-3 h-3" />}
                        {isExpanded ? 'Simplify' : 'Expand Full Tree'}
                    </button>
                </div>
                <p className="text-sm text-slate-600">{conflictAnalysis.details}</p>
            </div>

            {/* Graph Canvas */}
            <div className="flex-1 bg-slate-50 relative">
                {isLoading ? (
                    <div className="absolute inset-0 flex items-center justify-center">
                        <div className="text-slate-400">Generating circuit...</div>
                    </div>
                ) : (
                    <ReactFlow
                        nodes={nodes}
                        edges={edges}
                        onNodesChange={onNodesChange}
                        onEdgesChange={onEdgesChange}
                        onNodeClick={handleNodeClick}
                        nodeTypes={nodeTypes}
                        fitView
                        attributionPosition="bottom-left"
                    >
                        <Background color="#e2e8f0" gap={16} />
                        <Controls />
                        <MiniMap
                            nodeColor={(node) => {
                                if (node.data.is_conflict_node) return '#fca5a5';
                                switch (node.data.type) {
                                    case 'definition': return '#c4b5fd';
                                    case 'condition': return '#fcd34d';
                                    case 'consequence': return '#fca5a5';
                                    case 'protection': return '#6ee7b7';
                                    default: return '#cbd5e1';
                                }
                            }}
                            maskColor="rgba(0, 0, 0, 0.1)"
                        />
                    </ReactFlow>
                )}
            </div>

            {/* Legend */}
            <div className="p-3 border-t border-slate-200 bg-white">
                <div className="flex items-center gap-4 text-xs text-slate-600">
                    <div className="flex items-center gap-1">
                        <FileText className="w-3 h-3 text-purple-500" />
                        <span>Definition</span>
                    </div>
                    <div className="flex items-center gap-1">
                        <Zap className="w-3 h-3 text-amber-500" />
                        <span>Condition</span>
                    </div>
                    <div className="flex items-center gap-1">
                        <AlertTriangle className="w-3 h-3 text-red-500" />
                        <span>Consequence</span>
                    </div>
                    <div className="flex items-center gap-1">
                        <Shield className="w-3 h-3 text-emerald-500" />
                        <span>Protection</span>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default LogicCircuit;
