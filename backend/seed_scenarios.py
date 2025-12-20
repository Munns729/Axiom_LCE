from sqlalchemy.orm import Session
import uuid
from datetime import datetime
from database import SessionLocal, engine
from models import Base, ScenarioTemplate

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

FOUNDER_AGREEMENT_SCENARIOS = [
    {
        "transaction_type": "founder_agreement",
        "category": "termination",
        "priority": 10,  # Highest priority
        "name": "Quits to join competitor",
        "description": "Founder voluntarily resigns to join a competitor or start competing business",
        "trigger_event": "Voluntary resignation without Good Reason for better opportunity",
        "expected_behavior": "Should only forfeit unvested shares; vested shares should be retained",
        "common_conflicts": {
            "bad_leaver_override": "Classified as Bad Leaver without checking Good Reason protections",
            "all_shares_forfeited": "Agreement forces forfeiture of vested shares"
        },
        "test_strategy": {
            "check_for": ["Good Reason definition", "Bad Leaver definition", "Voluntary resignation handling"],
            "red_flags": ["forfeit all shares", "Bad Leaver without exception", "voluntary resignation = Bad Leaver"],
            "required_clauses": ["Good Reason protections should apply first"]
        }
    },
    {
        "transaction_type": "founder_agreement",
        "category": "medical",
        "priority": 9,
        "name": "Medical emergency (cancer diagnosis)",
        "description": "Founder diagnosed with serious illness requiring extended medical leave",
        "trigger_event": "Cannot perform duties due to cancer, heart attack, or other serious illness",
        "expected_behavior": "Should have medical/disability exception; not classified as Bad Leaver",
        "common_conflicts": {
            "no_medical_exception": "Good Reason definition doesn't include medical/disability",
            "bad_leaver_on_disability": "Inability to work treated as voluntary resignation"
        },
        "test_strategy": {
            "check_for": ["disability exception", "medical leave clause", "Good Reason medical provision"],
            "red_flags": ["no medical exception", "inability to perform = termination", "Bad Leaver on disability"],
            "required_clauses": ["Medical leave should not trigger forfeiture"]
        }
    },
    {
        "transaction_type": "founder_agreement",
        "category": "change_of_control",
        "priority": 8,
        "name": "Company acquired by competitor",
        "description": "Company is acquired and founder's role is eliminated or significantly changed",
        "trigger_event": "Acquisition by larger company, founder role eliminated or demoted",
        "expected_behavior": "Should have single-trigger or double-trigger acceleration; Good Reason if demoted",
        "common_conflicts": {
            "no_acceleration": "No acceleration clause on change of control",
            "no_good_reason_on_demotion": "Role change after acquisition not covered by Good Reason"
        },
        "test_strategy": {
            "check_for": ["change of control definition", "acceleration clause", "constructive termination"],
            "red_flags": ["no acceleration", "acquisition doesn't trigger protections"],
            "required_clauses": ["Acceleration on change of control", "Good Reason includes role change"]
        }
    },
    {
        "transaction_type": "founder_agreement",
        "category": "termination",
        "priority": 7,
        "name": "Laid off in restructuring",
        "description": "Company eliminates founder role in cost-cutting or restructuring",
        "trigger_event": "Termination without Cause due to business needs",
        "expected_behavior": "Keep vested shares, potentially some acceleration of unvested",
        "common_conflicts": {
            "no_severance": "No severance or acceleration on involuntary termination without Cause",
            "treated_as_bad_leaver": "Non-Cause termination still triggers Bad Leaver"
        },
        "test_strategy": {
            "check_for": ["termination without Cause", "severance provisions", "acceleration on termination"],
            "red_flags": ["no protection for layoff", "forfeit vested shares on non-Cause termination"],
            "required_clauses": ["Without Cause termination preserves vested shares"]
        }
    },
    {
        "transaction_type": "founder_agreement",
        "category": "economic",
        "priority": 8,
        "name": "Salary reduced by 50%+",
        "description": "Company cuts founder's salary by more than half",
        "trigger_event": "Material reduction in base salary (>25-50%)",
        "expected_behavior": "Should qualify as Good Reason for resignation with protections",
        "common_conflicts": {
            "no_salary_protection": "Good Reason doesn't include salary reduction",
            "threshold_too_high": "Salary reduction threshold >50% (too high to be protective)"
        },
        "test_strategy": {
            "check_for": ["Good Reason salary threshold", "material reduction definition"],
            "red_flags": ["no salary protection", "threshold above 40%", "no economic protections"],
            "required_clauses": ["Good Reason includes material salary reduction <30%"]
        }
    },
    {
        "transaction_type": "founder_agreement",
        "category": "termination",
        "priority": 9,
        "name": "Terminated for cause (alleged fraud)",
        "description": "Company terminates founder alleging fraud or gross misconduct",
        "trigger_event": "Termination for Cause based on alleged fraud, embezzlement, or gross negligence",
        "expected_behavior": "Should have narrow Cause definition, require evidence, potentially allow cure period",
        "common_conflicts": {
            "overly_broad_cause": "Cause includes minor infractions or subjective standards",
            "no_cure_period": "Immediate termination without chance to cure",
            "no_evidence_required": "Company can terminate without proving Cause"
        },
        "test_strategy": {
            "check_for": ["Cause definition", "cure period", "notice requirements", "evidence standards"],
            "red_flags": ["Cause includes 'poor performance'", "no cure period", "unilateral determination"],
            "required_clauses": ["Narrow Cause definition", "Notice + cure period for fixable issues"]
        }
    }
]

def seed_scenario_templates():
    """Populate database with standard scenario templates"""
    db = SessionLocal()
    try:
        # Check if templates already exist to avoid duplicates
        existing = db.query(ScenarioTemplate).filter(
            ScenarioTemplate.transaction_type == "founder_agreement"
        ).first()
        
        if existing:
            print("Founder agreement scenarios already exist. Skipping seed.")
            return

        for scenario_data in FOUNDER_AGREEMENT_SCENARIOS:
            template = ScenarioTemplate(**scenario_data)
            db.add(template)
        
        db.commit()
        print(f"Seeded {len(FOUNDER_AGREEMENT_SCENARIOS)} founder agreement scenarios")
        
    except Exception as e:
        print(f"Error seeding scenarios: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_scenario_templates()
