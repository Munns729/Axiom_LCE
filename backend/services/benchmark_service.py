"""
Benchmark service for dual-layer intelligence:
1. External market benchmarks
2. Internal historical performance
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, List, Optional
import statistics

from models import (
    DealTemplate,
    DealMetrics,
    BenchmarkInsight,
    MarketBenchmark,
    Analysis
)

class BenchmarkService:
    
    @staticmethod
    def extract_deal_terms(analysis: Analysis, document_text: str) -> Dict:
        """
        Extract structured deal terms from analysis
        This is simplified - production would use better NLP/extraction
        """
        # This would ideally use Mistral AI to extract structured data
        # For now, return mock extracted terms
        
        return {
            "vesting_years": 4.0,
            "cliff_months": 6.0,
            "good_reason_salary_cut_pct": 30.0,
            "good_reason_includes_relocation": True,
            "good_reason_includes_medical": False,
            "bad_leaver_forfeit": "all_shares"  # or "unvested_only"
        }
    
    @staticmethod
    def calculate_compliance_score(
        extracted_terms: Dict,
        target_terms: Dict
    ) -> tuple[float, List[Dict]]:
        """
        Calculate how well deal matches target template
        
        Returns: (compliance_score, deviations)
        """
        total_checks = 0
        passed_checks = 0
        deviations = []
        
        for key, target_spec in target_terms.items():
            total_checks += 1
            
            if key not in extracted_terms:
                continue
            
            actual_value = extracted_terms[key]
            target_value = target_spec.get('target')
            min_value = target_spec.get('min')
            max_value = target_spec.get('max')
            priority = target_spec.get('priority', 'medium')
            
            # Check compliance
            compliant = False
            
            if isinstance(target_value, bool):
                compliant = actual_value == target_value
            elif isinstance(target_value, (int, float)):
                if min_value is not None and max_value is not None:
                    compliant = min_value <= actual_value <= max_value
                else:
                    compliant = actual_value == target_value
            else:
                compliant = actual_value == target_value
            
            if compliant:
                passed_checks += 1
            else:
                deviations.append({
                    "term": key,
                    "target": target_value,
                    "actual": actual_value,
                    "priority": priority,
                    "severity": "high" if priority == "high" else "medium"
                })
        
        compliance_score = (passed_checks / total_checks * 100) if total_checks > 0 else 0
        
        return compliance_score, deviations
    
    @staticmethod
    def get_market_benchmark(
        metric_name: str,
        document_category: str,
        db: Session
    ) -> Optional[MarketBenchmark]:
        """Get external market benchmark for a metric"""
        return db.query(MarketBenchmark).filter(
            MarketBenchmark.metric_name == metric_name,
            MarketBenchmark.document_category == document_category
        ).first()
    
    @staticmethod
    def calculate_historical_performance(
        metric_name: str,
        organization_id: str,
        document_category: str,
        db: Session
    ) -> Dict:
        """
        Calculate organization's historical performance on a metric
        """
        # Get all closed deals for this organization
        deals = db.query(DealMetrics).filter(
            DealMetrics.organization_id == organization_id,
            DealMetrics.document_category == document_category,
            DealMetrics.deal_status == 'closed'
        ).all()
        
        if not deals:
            return {
                "sample_size": 0,
                "average": None,
                "median": None,
                "min": None,
                "max": None
            }
        
        # Extract values for this metric
        values = []
        for deal in deals:
            if metric_name in deal.terms:
                values.append(float(deal.terms[metric_name]))
        
        if not values:
            return {"sample_size": 0}
        
        return {
            "sample_size": len(values),
            "average": statistics.mean(values),
            "median": statistics.median(values),
            "min": min(values),
            "max": max(values),
            "std_dev": statistics.stdev(values) if len(values) > 1 else 0
        }
    
    @staticmethod
    def calculate_target_achievement_rate(
        metric_name: str,
        organization_id: str,
        template: DealTemplate,
        db: Session
    ) -> float:
        """
        Calculate % of deals that achieved target for this metric
        """
        deals = db.query(DealMetrics).filter(
            DealMetrics.organization_id == organization_id,
            DealMetrics.template_id == template.id,
            DealMetrics.deal_status == 'closed'
        ).all()
        
        if not deals:
            return 0.0
        
        target_spec = template.target_terms.get(metric_name, {})
        target_value = target_spec.get('target')
        min_value = target_spec.get('min')
        
        achieved_count = 0
        for deal in deals:
            if metric_name not in deal.terms:
                continue
            
            actual_value = deal.terms[metric_name]
            
            # Check if achieved target
            if isinstance(target_value, bool):
                if actual_value == target_value:
                    achieved_count += 1
            elif isinstance(target_value, (int, float)):
                if min_value is not None and actual_value >= min_value:
                    achieved_count += 1
                elif actual_value == target_value:
                    achieved_count += 1
        
        return (achieved_count / len(deals) * 100) if deals else 0.0
    
    @staticmethod
    def generate_dual_benchmark_analysis(
        extracted_terms: Dict,
        organization_id: str,
        document_category: str,
        db: Session
    ) -> Dict:
        """
        Generate complete dual-layer benchmark analysis
        Combines external market data with internal performance
        """
        # Get active template
        template = db.query(DealTemplate).filter(
            DealTemplate.organization_id == organization_id,
            DealTemplate.document_category == document_category,
            DealTemplate.active == True
        ).first()
        
        if not template:
            return {"error": "No active template found"}
        
        # Calculate compliance
        compliance_score, deviations = BenchmarkService.calculate_compliance_score(
            extracted_terms,
            template.target_terms
        )
        
        # Analyze each metric
        metrics_analysis = {}
        
        for metric_name, actual_value in extracted_terms.items():
            # Get market benchmark
            market_bench = BenchmarkService.get_market_benchmark(
                metric_name,
                document_category,
                db
            )
            
            # Get historical performance
            historical = BenchmarkService.calculate_historical_performance(
                metric_name,
                organization_id,
                document_category,
                db
            )
            
            # Get target from template
            target_spec = template.target_terms.get(metric_name, {})
            
            # Calculate achievement rate
            achievement_rate = BenchmarkService.calculate_target_achievement_rate(
                metric_name,
                organization_id,
                template,
                db
            )
            
            # Calculate vs. average
            vs_average = None
            if historical.get('average'):
                vs_average = actual_value - historical['average']
            
            # Determine assessment
            assessment = "unknown"
            if target_spec.get('min') and actual_value < target_spec['min']:
                assessment = "below_target"
            elif target_spec.get('target') and actual_value >= target_spec['target']:
                assessment = "holding_target"
            elif historical.get('average'):
                if actual_value < historical['average']:
                    assessment = "unusual_concession"
                else:
                    assessment = "above_average"
            
            # Build metric analysis
            metrics_analysis[metric_name] = {
                "current_deal": actual_value,
                
                "external_benchmark": {
                    "market_median": market_bench.market_median if market_bench else None,
                    "market_25th_percentile": market_bench.market_25th_percentile if market_bench else None,
                    "market_75th_percentile": market_bench.market_75th_percentile if market_bench else None,
                    "percentile": calculate_percentile(actual_value, market_bench) if market_bench else None,
                    "assessment": assess_vs_market(actual_value, market_bench) if market_bench else None
                },
                
                "internal_benchmark": {
                    "target": target_spec.get('target'),
                    "min": target_spec.get('min'),
                    "max": target_spec.get('max'),
                    "priority": target_spec.get('priority'),
                    "average_achieved": historical.get('average'),
                    "median_achieved": historical.get('median'),
                    "success_rate": achievement_rate,
                    "sample_size": historical.get('sample_size', 0),
                    "matches_target": assessment in ['holding_target', 'above_average'],
                    "vs_average": vs_average,
                    "assessment": assessment
                },
                
                "recommendation": generate_recommendation(
                    metric_name,
                    actual_value,
                    target_spec,
                    historical,
                    assessment
                )
            }
        
        return {
            "compliance_score": compliance_score,
            "deviations": deviations,
            "metrics": metrics_analysis,
            "template_name": template.name
        }

def calculate_percentile(value: float, market_bench: MarketBenchmark) -> int:
    """Calculate which percentile the value falls in"""
    if not market_bench:
        return 50
    
    if value <= market_bench.market_25th_percentile:
        return 25
    elif value <= market_bench.market_median:
        return 50
    elif value <= market_bench.market_75th_percentile:
        return 75
    else:
        return 90

def assess_vs_market(value: float, market_bench: MarketBenchmark) -> str:
    """Assess value vs. market"""
    if not market_bench:
        return "unknown"
    
    if value < market_bench.market_median:
        return "below_market"
    elif value > market_bench.market_75th_percentile:
        return "above_market"
    else:
        return "market_standard"

def generate_recommendation(
    metric_name: str,
    actual_value: float,
    target_spec: Dict,
    historical: Dict,
    assessment: str
) -> str:
    """Generate recommendation based on benchmarks"""
    
    if assessment == "holding_target":
        return f"✓ Holding target position. Good negotiation."
    
    elif assessment == "below_target":
        gap = target_spec.get('min', target_spec.get('target', 0)) - actual_value
        return f"⚠️ {gap} below your target. Consider pushing back - you typically achieve better terms."
    
    elif assessment == "unusual_concession":
        avg = historical.get('average', 0)
        gap = avg - actual_value
        rate = historical.get('sample_size', 0)
        return f"⚠️ Unusual concession. You're {gap:.1f} below your average of {avg:.1f} (based on {rate} deals). Only accept if strategic reason exists."
    
    else:
        return "Standard terms for this scenario."
