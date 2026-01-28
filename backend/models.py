"""
SQLAlchemy database models for Axiom LCE
"""
from sqlalchemy import Column, String, Text, DateTime, JSON, ForeignKey, Integer, Boolean, Float, LargeBinary
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

class Document(Base):
    """Stores uploaded legal documents"""
    __tablename__ = "documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String(255), nullable=False)
    original_text = Column(Text, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    file_type = Column(String(10), nullable=False)  # 'docx', 'pdf', 'txt'
    file_size = Column(String(50))  # e.g., "245 KB"
    file_content = Column(LargeBinary) # Original binary content
    tree = Column(JSON) # Structured representation of the document
    
    # Relationship to analyses
    analyses = relationship("Analysis", back_populates="document", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Document(id={self.id}, filename={self.filename})>"

class Analysis(Base):
    """Stores AI analysis results for documents"""
    __tablename__ = "analyses"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey('documents.id'), nullable=False)
    
    # Analysis results (stored as JSON)
    timeline = Column(JSON, nullable=False)  # Timeline steps array
    scenarios = Column(JSON, nullable=False)  # Scenario test results array
    definitions = Column(JSON)  # Extracted definitions
    conflict_analysis = Column(JSON)  # Conflict detection results
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    model_used = Column(String(50), default="mistral-small-latest")
    analysis_duration_ms = Column(String(20))  # e.g., "2340ms"
    
    # Relationship to document
    document = relationship("Document", back_populates="analyses")
    
    def __repr__(self):
        return f"<Analysis(id={self.id}, document_id={self.document_id})>"

class ClauseSuggestion(Base):
    """AI-generated clause alternatives for conflicts"""
    __tablename__ = "clause_suggestions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_id = Column(UUID(as_uuid=True), ForeignKey('analyses.id'), nullable=False)
    scenario_id = Column(String(50))  # e.g., "scenario-4"
    
    # Original problematic clause
    original_clause_text = Column(Text, nullable=False)
    original_section = Column(String(50))  # e.g., "4.2"
    conflict_type = Column(String(100))  # e.g., "good_reason_override"
    
    # Generated suggestions (JSON array)
    suggestions = Column(JSON, nullable=False)
    
    # Metadata
    generated_at = Column(DateTime, default=datetime.utcnow)
    model_used = Column(String(50), default="mistral-small-latest")
    generation_time_ms = Column(Integer)
    
    # User interaction tracking
    selected_option = Column(String(50))  # "founder_friendly", "market_standard", etc.
    selected_at = Column(DateTime)
    
    def __repr__(self):
        return f"<ClauseSuggestion(id={self.id}, conflict_type={self.conflict_type})>"

class DealTemplate(Base):
    """Organization's target positions and standards"""
    __tablename__ = "deal_templates"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True))  # For multi-tenancy
    
    name = Column(String(255), nullable=False)  # "Standard Founder Agreement 2024"
    description = Column(Text)
    template_type = Column(String(50), nullable=False)  # "target_position", "fallback_position"
    document_category = Column(String(100))  # "founder_agreement", "safe", "employment"
    
    # Reference to template document
    document_id = Column(UUID(as_uuid=True), ForeignKey('documents.id'))
    
    # Target parameters (JSON)
    target_terms = Column(JSON, nullable=False)
    
    # Metadata
    active = Column(Boolean, default=True)
    created_by = Column(String(255))  # User who created
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<DealTemplate(id={self.id}, name={self.name})>"

class DealMetrics(Base):
    """Extracted metrics from actual deals for historical tracking"""
    __tablename__ = "deal_metrics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_id = Column(UUID(as_uuid=True), ForeignKey('analyses.id'), nullable=False)
    organization_id = Column(UUID(as_uuid=True))
    
    # Deal identification
    deal_name = Column(String(255))  # "Acme Series A", "Founder John Doe"
    document_category = Column(String(100))  # "founder_agreement", "safe", etc.
    
    # Extracted term values
    terms = Column(JSON, nullable=False)
    
    # Deal context
    deal_type = Column(String(100))  # "Series A", "Series B", "acquisition", "founder_grant"
    deal_stage = Column(String(50))  # "proposed", "negotiating", "signed"
    deal_value = Column(String(100))  # "$5M", "N/A"
    counterparty_type = Column(String(100))  # "VC", "acquirer", "founder"
    leverage_assessment = Column(String(50))  # "high", "medium", "low"
    
    # Compliance metrics
    template_id = Column(UUID(as_uuid=True), ForeignKey('deal_templates.id'))
    compliance_score = Column(Float)  # 0-100, % match to target
    deviations = Column(JSON)  # List of deviations from target
    
    # Outcome
    deal_status = Column(String(50))  # "active", "closed", "abandoned"
    closed_at = Column(DateTime)
    notes = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    analysis = relationship("Analysis", backref="deal_metrics")
    template = relationship("DealTemplate")
    
    def __repr__(self):
        return f"<DealMetrics(id={self.id}, deal_name={self.deal_name})>"

class BenchmarkInsight(Base):
    """Auto-calculated insights from historical deal data"""
    __tablename__ = "benchmark_insights"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), nullable=False)
    document_category = Column(String(100))  # "founder_agreement"
    
    # What metric this insight is about
    metric_name = Column(String(100), nullable=False)  # "cliff_months", "vesting_years"
    
    # Statistical aggregates
    target_value = Column(String(100))  # From template
    average_achieved = Column(Float)
    median_achieved = Column(Float)
    std_dev = Column(Float)
    min_value = Column(Float)
    max_value = Column(Float)
    
    # Success metrics
    target_achievement_rate = Column(Float)  # % of deals that hit target
    sample_size = Column(Integer)  # Number of deals analyzed
    
    # Patterns (JSON)
    patterns = Column(JSON)
    
    # Recommendations
    recommendations = Column(JSON)
    
    # Metadata
    calculated_at = Column(DateTime, default=datetime.utcnow)
    data_freshness = Column(String(50))  # "real_time", "last_hour", "last_day"
    
    def __repr__(self):
        return f"<BenchmarkInsight(metric={self.metric_name}, org={self.organization_id})>"

class MarketBenchmark(Base):
    """External market benchmark data (from public sources)"""
    __tablename__ = "market_benchmarks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_category = Column(String(100))
    metric_name = Column(String(100))
    
    # Market statistics
    market_25th_percentile = Column(Float)  # Company-friendly
    market_median = Column(Float)
    market_75th_percentile = Column(Float)  # Founder-friendly
    market_mean = Column(Float)
    
    # Data source
    source = Column(String(255))  # "YC", "NVCA", "AngelList", "Cooley GO"
    source_url = Column(String(500))
    sample_size = Column(Integer)
    
    # Filters
    deal_stage_filter = Column(String(100))  # "Series A", "Series B", "all"
    geography_filter = Column(String(100))  # "US", "EU", "global"
    industry_filter = Column(String(100))  # "tech", "all"
    
    # Metadata
    data_date = Column(DateTime)  # When this market data is from
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<MarketBenchmark(metric={self.metric_name}, source={self.source})>"

class ScenarioTemplate(Base):
    """Pre-defined scenario templates by transaction type"""
    __tablename__ = "scenario_templates"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Classification
    transaction_type = Column(String(100), nullable=False)  # "founder_agreement", "m&a", "employment"
    category = Column(String(100))  # "termination", "change_of_control", "vesting"
    priority = Column(Integer, default=5)  # 1-10, higher = more important
    
    # Scenario definition
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    
    # What to test
    trigger_event = Column(Text, nullable=False)
    expected_behavior = Column(Text, nullable=False)
    
    # Common failure patterns
    common_conflicts = Column(JSON)
    
    # How to test
    test_strategy = Column(JSON)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<ScenarioTemplate(type={self.transaction_type}, name={self.name})>"

class ScenarioTest(Base):
    """Actual scenario test results for a specific analysis"""
    __tablename__ = "scenario_tests"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_id = Column(UUID(as_uuid=True), ForeignKey('analyses.id'), nullable=False)
    
    # Source of scenario
    source_type = Column(String(50), nullable=False)  # "template", "contract_generated", "user_custom"
    template_id = Column(UUID(as_uuid=True), ForeignKey('scenario_templates.id'))  # If from template
    
    # Scenario details
    name = Column(String(255), nullable=False)
    description = Column(Text)
    trigger_event = Column(Text, nullable=False)
    
    # Test results
    status = Column(String(20), nullable=False)  # "pass", "fail", "warning"
    
    # Pass/Fail reasoning (from LLM)
    reasoning = Column(JSON)
    
    # Additional context
    severity = Column(String(20))  # "critical", "high", "medium", "low"
    affected_clauses = Column(JSON)  # ["Section 4.2", "Section 1.4"]
    
    # User interaction
    user_acknowledged = Column(Boolean, default=False)
    user_notes = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    analysis = relationship("Analysis", backref="scenario_tests")
    template = relationship("ScenarioTemplate")
    
    def __repr__(self):
        return f"<ScenarioTest(name={self.name}, status={self.status})>"

class AssertionVerification(Base):
    """User-submitted assertions and their verification results"""
    __tablename__ = "assertion_verifications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey('documents.id'), nullable=False)
    analysis_id = Column(UUID(as_uuid=True), ForeignKey('analyses.id'))  # Optional link to analysis
    
    # User's assertion
    assertion_text = Column(Text, nullable=False)
    
    # Parsed assertion structure
    parsed_assertion = Column(JSON)  # Entities, conditions, expected outcome
    
    # Verification result
    verdict = Column(String(20), nullable=False)  # "pass", "fail", "ambiguous"
    logic_trace = Column(JSON, nullable=False)  # Causality chain
    
    # Conflicts found
    has_conflict = Column(Boolean, default=False)
    conflict_severity = Column(String(20))  # "high", "medium", "low"
    conflict_details = Column(Text)
    conflicting_clauses = Column(JSON)  # List of clause IDs/sections
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    verification_duration_ms = Column(Integer)
    model_used = Column(String(50), default="mistral-small-latest")
    
    # Relationships
    document = relationship("Document", backref="assertion_verifications")
    analysis = relationship("Analysis", backref="assertion_verifications")
    
    def __repr__(self):
        return f"<AssertionVerification(id={self.id}, verdict={self.verdict})>"
