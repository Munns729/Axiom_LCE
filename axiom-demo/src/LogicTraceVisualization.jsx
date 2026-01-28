import React, { useCallback, useMemo } from 'react';
import ReactFlow, {
    Background,
    Controls,
    MiniMap,
    useNodesState,
    useEdgesState,
    MarkerType,
} from 'reactflow';
import 'reactflow/dist/style.css';
import './LogicTraceVisualization.css';

/**
 * LogicTraceVisualization Component
 * 
 * Displays a node-link diagram showing the causality chain
 * for assertion verification. Shows how the assertion flows
 * through definitions and clauses to reach a verdict.
 */
const LogicTraceVisualization = ({ logicTrace, verdict }) => {
    const buildNodesAndEdges = useCallback(() => {
        if (!logicTrace || !logicTrace.chain || logicTrace.chain.length === 0) {
            return { nodes: [], edges: [] };
        }

        const nodes = [];
        const edges = [];
        const chain = logicTrace.chain;

        // Layout configuration
        const nodeWidth = 250;
        const nodeHeight = 100;
        const horizontalSpacing = 350;
        const verticalSpacing = 150;

        chain.forEach((item, index) => {
            // Determine node color based on type and status
            let nodeColor = '#667eea'; // default purple
            let borderColor = '#667eea';

            if (item.type === 'input') {
                nodeColor = '#4299e1'; // blue for input
                borderColor = '#4299e1';
            } else if (item.type === 'definition') {
                nodeColor = '#48bb78'; // green for definitions
                borderColor = '#48bb78';
            } else if (item.type === 'clause') {
                nodeColor = '#ed8936'; // orange for clauses
                borderColor = '#ed8936';
            } else if (item.type === 'result') {
                if (verdict === 'pass') {
                    nodeColor = '#48bb78'; // green for pass
                    borderColor = '#48bb78';
                } else if (verdict === 'fail') {
                    nodeColor = '#f56565'; // red for fail
                    borderColor = '#f56565';
                } else {
                    nodeColor = '#ecc94b'; // yellow for ambiguous
                    borderColor = '#ecc94b';
                }
            }

            // Calculate position (simple vertical flow)
            const x = 100;
            const y = index * verticalSpacing;

            nodes.push({
                id: `node-${index}`,
                type: 'default',
                position: { x, y },
                data: {
                    label: (
                        <div className="logic-node-content">
                            <div className="logic-node-title">{item.node}</div>
                            <div className="logic-node-text">{item.text.substring(0, 100)}{item.text.length > 100 ? '...' : ''}</div>
                            {item.section && (
                                <div className="logic-node-section">§ {item.section}</div>
                            )}
                        </div>
                    ),
                },
                style: {
                    background: nodeColor,
                    color: 'white',
                    border: `3px solid ${borderColor}`,
                    borderRadius: '12px',
                    padding: '16px',
                    width: nodeWidth,
                    minHeight: nodeHeight,
                    boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
                    fontSize: '13px',
                },
            });

            // Create edge to next node
            if (index < chain.length - 1) {
                edges.push({
                    id: `edge-${index}`,
                    source: `node-${index}`,
                    target: `node-${index + 1}`,
                    type: 'smoothstep',
                    animated: true,
                    style: { stroke: '#999', strokeWidth: 2 },
                    markerEnd: {
                        type: MarkerType.ArrowClosed,
                        color: '#999',
                    },
                });
            }
        });

        return { nodes, edges };
    }, [logicTrace, verdict]);

    const { nodes: initialNodes, edges: initialEdges } = useMemo(
        () => buildNodesAndEdges(),
        [buildNodesAndEdges]
    );

    const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
    const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

    // Update nodes and edges when logicTrace changes
    React.useEffect(() => {
        const { nodes: newNodes, edges: newEdges } = buildNodesAndEdges();
        setNodes(newNodes);
        setEdges(newEdges);
    }, [logicTrace, verdict, buildNodesAndEdges, setNodes, setEdges]);

    if (!logicTrace || !logicTrace.chain || logicTrace.chain.length === 0) {
        return (
            <div className="logic-trace-empty">
                <div className="empty-icon">🔍</div>
                <div className="empty-text">No logic trace available</div>
                <div className="empty-subtext">Submit an assertion to see the causality chain</div>
            </div>
        );
    }

    return (
        <div className="logic-trace-container">
            <div className="logic-trace-header">
                <h4>Logic Causality Chain</h4>
                <div className="logic-trace-legend">
                    <span className="legend-item">
                        <span className="legend-dot" style={{ background: '#4299e1' }}></span>
                        Assertion
                    </span>
                    <span className="legend-item">
                        <span className="legend-dot" style={{ background: '#48bb78' }}></span>
                        Definition
                    </span>
                    <span className="legend-item">
                        <span className="legend-dot" style={{ background: '#ed8936' }}></span>
                        Clause
                    </span>
                    <span className="legend-item">
                        <span className="legend-dot" style={{ background: verdict === 'pass' ? '#48bb78' : '#f56565' }}></span>
                        Result
                    </span>
                </div>
            </div>

            <div className="logic-trace-flow">
                <ReactFlow
                    nodes={nodes}
                    edges={edges}
                    onNodesChange={onNodesChange}
                    onEdgesChange={onEdgesChange}
                    fitView
                    attributionPosition="bottom-left"
                >
                    <Background color="#aaa" gap={16} />
                    <Controls />
                    <MiniMap
                        nodeColor={(node) => {
                            return node.style?.background || '#667eea';
                        }}
                        maskColor="rgba(0, 0, 0, 0.1)"
                    />
                </ReactFlow>
            </div>
        </div>
    );
};

export default LogicTraceVisualization;
