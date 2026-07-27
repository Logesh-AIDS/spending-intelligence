"""
Module 5 – Recommendation Engine
Generates personalised financial recommendations using model outputs + business rules.

Design: hybrid approach
- ML models provide signals (anomaly scores, exhaustion predictions, cluster labels)
- Business rules interpret those signals into human-readable recommendations
- This is explainable, auditable, and does not require labels for training
"""
from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class Recommendation:
    title: str
    message: str
    priority: str        # "high" | "medium" | "low"
    category: str        # "spending" | "savings" | "budget" | "behaviour" | "alert"
    basis: str           # explanation of why this recommendation was generated


class RecommendationEngine:
    
    def generate(
        self,
        user_stats: Dict[str, Any],
        anomaly_results: Dict = None,
        cash_exhaustion: Dict = None,
        cluster_label: int = None,
    ) -> List[Recommendation]:
        """
        Generate recommendations from model outputs and user stats.
        
        Args:
            user_stats: from dashboard summary (savings_rate, spending, etc.)
            anomaly_results: from anomaly detector
            cash_exhaustion: from cash exhaustion predictor
            cluster_label: from user segmentation model
        
        Returns:
            List of Recommendation objects, sorted by priority
        """
        recs = []
        
        recs.extend(self._spending_rules(user_stats))
        recs.extend(self._savings_rules(user_stats))
        recs.extend(self._cash_exhaustion_rules(cash_exhaustion or {}))
        recs.extend(self._anomaly_rules(anomaly_results or {}))
        recs.extend(self._segment_rules(cluster_label, user_stats))
        recs.extend(self._category_rules(user_stats))
        
        # Sort: high → medium → low
        priority_order = {"high": 0, "medium": 1, "low": 2}
        recs.sort(key=lambda r: priority_order[r.priority])
        
        return recs
    
    # ── Spending Rules ─────────────────────────────────────────────
    
    def _spending_rules(self, stats: Dict) -> List[Recommendation]:
        recs = []
        
        this_month = stats.get("this_month_spending", 0)
        last_month_avg = stats.get("average_monthly_spending", 0)
        
        if last_month_avg > 0 and this_month > last_month_avg * 1.3:
            pct = round((this_month - last_month_avg) / last_month_avg * 100)
            recs.append(Recommendation(
                title="Spending Increase Alert",
                message=f"Your spending this month is {pct}% higher than your monthly average. Consider reviewing recent expenses.",
                priority="high",
                category="spending",
                basis=f"This month: ₹{this_month:.0f} vs avg ₹{last_month_avg:.0f}"
            ))
        
        daily_avg = stats.get("average_daily_spending", 0)
        today = stats.get("today_spending", 0)
        
        if daily_avg > 0 and today > daily_avg * 2:
            recs.append(Recommendation(
                title="High Spending Today",
                message=f"You've spent ₹{today:.0f} today, which is {round(today/daily_avg, 1)}x your daily average. Avoid further non-essential purchases.",
                priority="medium",
                category="spending",
                basis=f"Today: ₹{today:.0f}, daily average: ₹{daily_avg:.0f}"
            ))
        
        return recs
    
    # ── Savings Rules ──────────────────────────────────────────────
    
    def _savings_rules(self, stats: Dict) -> List[Recommendation]:
        recs = []
        
        savings_pct = stats.get("savings_percentage", 0)
        
        if savings_pct < 0:
            recs.append(Recommendation(
                title="Expenses Exceed Income",
                message="Your total expenses have exceeded your income. Review your spending immediately and identify areas to cut back.",
                priority="high",
                category="savings",
                basis=f"Savings rate: {savings_pct:.1f}%"
            ))
        elif savings_pct < 10:
            recs.append(Recommendation(
                title="Low Savings Rate",
                message=f"You're saving only {savings_pct:.1f}% of your income. Aim for at least 20% to build financial resilience.",
                priority="medium",
                category="savings",
                basis=f"Savings rate: {savings_pct:.1f}%, target: 20%"
            ))
        elif savings_pct >= 30:
            recs.append(Recommendation(
                title="Great Savings Habit",
                message=f"You're saving {savings_pct:.1f}% of your income. Consider investing the surplus for long-term growth.",
                priority="low",
                category="savings",
                basis=f"Savings rate: {savings_pct:.1f}%"
            ))
        
        return recs
    
    # ── Cash Exhaustion Rules ──────────────────────────────────────
    
    def _cash_exhaustion_rules(self, exhaustion: Dict) -> List[Recommendation]:
        recs = []
        
        days_remaining = exhaustion.get("days_until_low_balance")
        risk = exhaustion.get("low_balance_risk", 0)
        threshold = exhaustion.get("threshold", 1000)
        
        if days_remaining is not None and days_remaining < 7:
            recs.append(Recommendation(
                title="🚨 Critical: Low Balance Warning",
                message=f"Based on your spending pattern, your balance may drop below ₹{threshold:.0f} in approximately {days_remaining} days. Reduce spending immediately.",
                priority="high",
                category="alert",
                basis=f"Predicted days until low balance: {days_remaining}"
            ))
        elif days_remaining is not None and days_remaining < 30:
            recs.append(Recommendation(
                title="Balance Warning",
                message=f"Your balance may drop below ₹{threshold:.0f} in approximately {days_remaining} days at your current spending rate.",
                priority="medium",
                category="alert",
                basis=f"Predicted days until low balance: {days_remaining}"
            ))
        
        if risk == 1 and (days_remaining is None or days_remaining >= 7):
            recs.append(Recommendation(
                title="30-Day Cash Risk Detected",
                message="Your spending pattern suggests a risk of running low on funds within 30 days. Consider reducing discretionary spending.",
                priority="medium",
                category="alert",
                basis="30-day low balance risk model prediction"
            ))
        
        return recs
    
    # ── Anomaly Rules ──────────────────────────────────────────────
    
    def _anomaly_rules(self, anomaly: Dict) -> List[Recommendation]:
        recs = []
        
        recent_anomalies = anomaly.get("recent_anomalies", [])
        anomaly_count = anomaly.get("anomaly_count", 0)
        
        if anomaly_count > 0:
            recs.append(Recommendation(
                title="Unusual Transaction Detected",
                message=f"{anomaly_count} unusual transaction(s) detected recently. Please review your recent activity for unauthorised charges.",
                priority="high",
                category="alert",
                basis=f"Anomaly detection model flagged {anomaly_count} transaction(s)"
            ))
        
        return recs
    
    # ── Segment-based Rules ────────────────────────────────────────
    
    def _segment_rules(self, cluster: int, stats: Dict) -> List[Recommendation]:
        recs = []
        
        if cluster is None:
            return recs
        
        segment_messages = {
            2: Recommendation(
                title="Heavy Spender Profile",
                message="Your spending pattern places you in the Heavy Spender segment. Setting monthly category budgets can help control outflows.",
                priority="medium",
                category="behaviour",
                basis="User segmentation model — Heavy Spender cluster"
            ),
            3: Recommendation(
                title="Frequent Small Transactions",
                message="You make many small transactions. These add up quickly — consolidating purchases (e.g. weekly grocery run instead of daily) could reduce spend.",
                priority="low",
                category="behaviour",
                basis="User segmentation model — Frequent Micro-Spender cluster"
            ),
            4: Recommendation(
                title="Luxury Spending Pattern",
                message="Your profile shows above-average spending on high-value items. Ensure luxury purchases align with your savings goals.",
                priority="low",
                category="behaviour",
                basis="User segmentation model — Luxury Buyer cluster"
            ),
        }
        
        if cluster in segment_messages:
            recs.append(segment_messages[cluster])
        
        return recs
    
    # ── Category-based Rules ───────────────────────────────────────
    
    def _category_rules(self, stats: Dict) -> List[Recommendation]:
        recs = []
        
        top_category = stats.get("top_category")
        top_category_pct = stats.get("top_category_percentage", 0)
        
        if top_category and top_category_pct > 40:
            recs.append(Recommendation(
                title=f"High {top_category} Spend",
                message=f"{top_category_pct:.0f}% of your spending is on {top_category}. Diversifying spending categories typically leads to better financial health.",
                priority="low",
                category="spending",
                basis=f"{top_category} accounts for {top_category_pct:.1f}% of total spending"
            ))
        
        return recs


def get_recommendations(
    user_stats: Dict,
    anomaly_results: Dict = None,
    cash_exhaustion: Dict = None,
    cluster_label: int = None,
) -> List[Dict]:
    """
    Public interface — returns recommendations as list of dicts (for API serialisation).
    """
    engine = RecommendationEngine()
    recs = engine.generate(user_stats, anomaly_results, cash_exhaustion, cluster_label)
    
    return [
        {
            "title": r.title,
            "message": r.message,
            "priority": r.priority,
            "category": r.category,
            "basis": r.basis,
        }
        for r in recs
    ]
