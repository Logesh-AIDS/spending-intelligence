"""
Module 6 – AI Insight Generator
Generates textual financial insights from analytics and ML outputs.
All insights are derived from real data — no templates without data backing.
"""
from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class Insight:
    insight_type: str    # "spending" | "saving" | "behaviour" | "trend"
    title: str
    description: str
    supporting_metric: str
    change_percentage: float
    is_positive: bool


def generate_insights(
    current_stats: Dict,
    merchant_data: Dict = None,
    behaviour_data: Dict = None,
) -> List[Dict]:
    """
    Generate insights by comparing current stats to historical patterns.
    
    Args:
        current_stats: from dashboard summary
        merchant_data: from analytics/merchants
        behaviour_data: from analytics/behaviour
    
    Returns:
        List of insight dicts
    """
    insights = []

    this_month = current_stats.get("this_month_spending", 0)
    avg_monthly = current_stats.get("average_monthly_spending", 0)

    # ── Spending trend ──
    if avg_monthly > 0:
        change = ((this_month - avg_monthly) / avg_monthly) * 100
        if abs(change) >= 10:
            is_positive = change < 0
            insights.append(Insight(
                insight_type="spending",
                title="Monthly Spending Change",
                description=(
                    f"Spending is {'down' if is_positive else 'up'} {abs(change):.0f}% "
                    f"compared to your monthly average. "
                    f"{'Great discipline!' if is_positive else 'Consider reviewing your expenses.'}"
                ),
                supporting_metric=f"This month: ₹{this_month:.0f} | Average: ₹{avg_monthly:.0f}",
                change_percentage=round(change, 1),
                is_positive=is_positive,
            ))

    # ── Savings trend ──
    savings_pct = current_stats.get("savings_percentage", 0)
    if savings_pct > 25:
        insights.append(Insight(
            insight_type="saving",
            title="Strong Savings Rate",
            description=f"You are saving {savings_pct:.1f}% of your income this period. This puts you above the recommended 20% threshold.",
            supporting_metric=f"Savings rate: {savings_pct:.1f}%",
            change_percentage=savings_pct,
            is_positive=True,
        ))
    elif savings_pct < 5:
        insights.append(Insight(
            insight_type="saving",
            title="Low Savings Rate",
            description=f"Your savings rate is only {savings_pct:.1f}%. A healthy target is 20%. Review your top spending categories.",
            supporting_metric=f"Savings rate: {savings_pct:.1f}%",
            change_percentage=savings_pct,
            is_positive=False,
        ))

    # ── Cash flow ──
    net = current_stats.get("net_cash_flow", 0)
    if net < 0:
        insights.append(Insight(
            insight_type="trend",
            title="Negative Cash Flow Detected",
            description=f"Your expenses exceed your income by ₹{abs(net):.0f}. This trend is unsustainable. Identify and reduce non-essential spending immediately.",
            supporting_metric=f"Net cash flow: ₹{net:.0f}",
            change_percentage=0,
            is_positive=False,
        ))
    elif net > 0:
        insights.append(Insight(
            insight_type="trend",
            title="Positive Cash Flow",
            description=f"You have a positive cash flow of ₹{net:.0f}. Consider allocating the surplus to savings or investments.",
            supporting_metric=f"Net cash flow: ₹{net:.0f}",
            change_percentage=0,
            is_positive=True,
        ))

    # ── Merchant diversity ──
    if behaviour_data:
        diversity = behaviour_data.get("weekend_spending", 0)
        weekday = behaviour_data.get("weekday_spending", 0)
        if weekday > 0:
            ratio = diversity / weekday if weekday > 0 else 0
            if ratio > 1.5:
                insights.append(Insight(
                    insight_type="behaviour",
                    title="Weekend Spending High",
                    description=f"Your weekend spending is {ratio:.1f}x your weekday spending. Weekend impulse purchases may be inflating your total spend.",
                    supporting_metric=f"Weekend: ₹{diversity:.0f} | Weekday: ₹{weekday:.0f}",
                    change_percentage=round((ratio - 1) * 100, 1),
                    is_positive=False,
                ))

    # ── Merchant insights ──
    if merchant_data and merchant_data.get("merchants"):
        top = merchant_data["merchants"][0]
        if top["percentage"] > 30:
            insights.append(Insight(
                insight_type="spending",
                title=f"High Concentration at {top['merchant']}",
                description=f"{top['percentage']:.0f}% of your spending goes to {top['merchant']}. Consider if this aligns with your budget.",
                supporting_metric=f"₹{top['total_spent']:.0f} across {top['transaction_count']} transactions",
                change_percentage=top["percentage"],
                is_positive=False,
            ))

    # ── Today's spending ──
    today = current_stats.get("today_spending", 0)
    avg_daily = current_stats.get("average_daily_spending", 0)
    if avg_daily > 0 and today > avg_daily * 1.5:
        insights.append(Insight(
            insight_type="spending",
            title="Above-Average Spending Today",
            description=f"You've spent ₹{today:.0f} today — {today/avg_daily:.1f}x your daily average of ₹{avg_daily:.0f}.",
            supporting_metric=f"Today: ₹{today:.0f} | Daily avg: ₹{avg_daily:.0f}",
            change_percentage=round(((today - avg_daily) / avg_daily) * 100, 1),
            is_positive=False,
        ))

    return [
        {
            "insight_type": i.insight_type,
            "title": i.title,
            "description": i.description,
            "supporting_metric": i.supporting_metric,
            "change_percentage": i.change_percentage,
            "is_positive": i.is_positive,
        }
        for i in insights
    ]
