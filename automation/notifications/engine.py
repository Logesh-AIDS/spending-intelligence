"""
Module 3 – Smart Notification Engine
Evaluates user's financial state and generates intelligent notifications.
Each notification includes: trigger reason, supporting data, AI explanation, recommended action.
"""
from typing import List, Dict, Any
from dataclasses import dataclass, field


@dataclass
class SmartNotification:
    title: str
    message: str
    notification_type: str      # "alert" | "insight" | "goal" | "report"
    priority: str               # "high" | "medium" | "low"
    trigger_reason: str
    supporting_data: str        # stringified context
    ai_explanation: str
    recommended_action: str


class NotificationEngine:

    def evaluate(
        self,
        user_stats: Dict,
        cash_exhaustion: Dict = None,
        anomaly_results: Dict = None,
        goals: List[Dict] = None,
    ) -> List[SmartNotification]:

        notifications = []

        notifications.extend(self._budget_alerts(user_stats))
        notifications.extend(self._cash_exhaustion_alerts(cash_exhaustion or {}))
        notifications.extend(self._anomaly_alerts(anomaly_results or {}))
        notifications.extend(self._savings_alerts(user_stats))
        notifications.extend(self._goal_alerts(goals or []))

        # Sort by priority
        order = {"high": 0, "medium": 1, "low": 2}
        notifications.sort(key=lambda n: order[n.priority])

        return notifications

    def _budget_alerts(self, stats: Dict) -> List[SmartNotification]:
        notes = []

        today = stats.get("today_spending", 0)
        avg_daily = stats.get("average_daily_spending", 0)

        if avg_daily > 0 and today > avg_daily * 2:
            notes.append(SmartNotification(
                title="🔴 Daily Budget Exceeded",
                message=f"You've spent ₹{today:.0f} today — more than double your daily average of ₹{avg_daily:.0f}.",
                notification_type="alert",
                priority="high",
                trigger_reason="Daily spending > 2x daily average",
                supporting_data=f"today: {today}, daily_avg: {avg_daily}",
                ai_explanation="Your daily spending pattern shows significant deviation from your 30-day average.",
                recommended_action="Pause discretionary spending for the rest of the day."
            ))

        this_week = stats.get("this_week_spending", 0)
        avg_monthly = stats.get("average_monthly_spending", 0)
        weekly_expected = avg_monthly / 4 if avg_monthly > 0 else 0

        if weekly_expected > 0 and this_week > weekly_expected * 1.4:
            notes.append(SmartNotification(
                title="⚠️ Weekly Budget Warning",
                message=f"Weekly spending (₹{this_week:.0f}) is 40%+ above expected weekly rate.",
                notification_type="alert",
                priority="medium",
                trigger_reason="Weekly spending > 1.4x expected weekly amount",
                supporting_data=f"this_week: {this_week}, expected_weekly: {weekly_expected:.0f}",
                ai_explanation="Based on your monthly average, your weekly spending should be approximately ₹{:.0f}.".format(weekly_expected),
                recommended_action="Review this week's transactions and identify categories that exceeded budget."
            ))

        this_month = stats.get("this_month_spending", 0)
        if avg_monthly > 0 and this_month > avg_monthly * 1.25:
            notes.append(SmartNotification(
                title="📊 Monthly Budget Alert",
                message=f"Monthly spending (₹{this_month:.0f}) is 25% above your monthly average.",
                notification_type="alert",
                priority="medium",
                trigger_reason="Monthly spending > 1.25x monthly average",
                supporting_data=f"this_month: {this_month}, avg_monthly: {avg_monthly}",
                ai_explanation="Your spending this month is significantly above your historical average.",
                recommended_action="Identify and reduce the top spending category for the rest of the month."
            ))

        return notes

    def _cash_exhaustion_alerts(self, exhaustion: Dict) -> List[SmartNotification]:
        notes = []

        days = exhaustion.get("days_until_low_balance")
        threshold = exhaustion.get("threshold", 1000)
        risk = exhaustion.get("low_balance_risk", 0)

        if days is not None and days < 7:
            notes.append(SmartNotification(
                title="🚨 Critical Balance Warning",
                message=f"Your balance may drop below ₹{threshold:.0f} in approximately {days:.0f} days.",
                notification_type="alert",
                priority="high",
                trigger_reason="Predicted days until low balance < 7",
                supporting_data=f"days_remaining: {days}, threshold: {threshold}",
                ai_explanation="The cash exhaustion model predicts balance will reach critical levels based on your current spending velocity.",
                recommended_action="Reduce all non-essential spending immediately and ensure no large payments are scheduled."
            ))
        elif risk == 1:
            notes.append(SmartNotification(
                title="💸 30-Day Cash Risk",
                message="AI predicts a risk of your balance dropping critically low within 30 days.",
                notification_type="alert",
                priority="medium",
                trigger_reason="30-day low balance risk model = 1",
                supporting_data=f"risk_probability: {exhaustion.get('risk_probability', '?')}",
                ai_explanation="Your spending velocity and current balance indicate a medium-risk scenario for the next 30 days.",
                recommended_action="Review monthly expenses and consider deferring non-essential purchases."
            ))

        return notes

    def _anomaly_alerts(self, anomaly: Dict) -> List[SmartNotification]:
        notes = []
        count = anomaly.get("anomaly_count", 0)

        if count > 0:
            notes.append(SmartNotification(
                title="🔍 Unusual Transaction Detected",
                message=f"{count} transaction(s) were flagged as unusual compared to your normal spending.",
                notification_type="alert",
                priority="high",
                trigger_reason="Anomaly detection model flagged transactions",
                supporting_data=f"anomaly_count: {count}",
                ai_explanation="The Isolation Forest model identified spending patterns significantly different from your historical behaviour.",
                recommended_action="Review the flagged transactions in your transaction history and verify they are authorised."
            ))

        return notes

    def _savings_alerts(self, stats: Dict) -> List[SmartNotification]:
        notes = []
        savings_pct = stats.get("savings_percentage", 0)
        net = stats.get("net_cash_flow", 0)

        if net < 0:
            notes.append(SmartNotification(
                title="❌ Expenses Exceed Income",
                message=f"You are spending ₹{abs(net):.0f} more than you earn. This is unsustainable.",
                notification_type="alert",
                priority="high",
                trigger_reason="Net cash flow is negative",
                supporting_data=f"net_cash_flow: {net}",
                ai_explanation="Total expenses exceed total income in the current period.",
                recommended_action="Immediately identify and cut your two highest expense categories."
            ))
        elif savings_pct >= 30:
            notes.append(SmartNotification(
                title="✅ Excellent Savings This Month",
                message=f"You are saving {savings_pct:.1f}% of your income. Keep it up!",
                notification_type="insight",
                priority="low",
                trigger_reason="Savings rate >= 30%",
                supporting_data=f"savings_percentage: {savings_pct}",
                ai_explanation="Your income-to-expense ratio is excellent this period.",
                recommended_action="Consider directing surplus savings into an investment or emergency fund."
            ))

        return notes

    def _goal_alerts(self, goals: List[Dict]) -> List[SmartNotification]:
        notes = []

        for goal in goals:
            prediction = goal.get("ai_prediction")
            title = goal.get("title", "Goal")
            progress = goal.get("progress_percentage", 0)

            if prediction == "achieved":
                notes.append(SmartNotification(
                    title=f"🎯 Goal Achieved: {title}",
                    message=f"Congratulations! You have achieved your goal: {title}",
                    notification_type="goal",
                    priority="low",
                    trigger_reason="Goal progress = 100%",
                    supporting_data=f"progress: {progress}%",
                    ai_explanation="Goal target has been met based on current transaction data.",
                    recommended_action="Set a new, more ambitious goal to continue building good habits."
                ))
            elif prediction == "at_risk":
                notes.append(SmartNotification(
                    title=f"⚠️ Goal at Risk: {title}",
                    message=f"Your goal '{title}' is at risk with {progress:.0f}% progress and {goal.get('days_remaining', '?')} days remaining.",
                    notification_type="goal",
                    priority="medium",
                    trigger_reason="Goal predicted as at_risk",
                    supporting_data=f"progress: {progress}%, days_remaining: {goal.get('days_remaining')}",
                    ai_explanation="At the current rate, this goal may not be achieved by the deadline.",
                    recommended_action="Adjust spending to accelerate progress toward this goal."
                ))

        return notes


def generate_notifications(
    user_stats: Dict,
    cash_exhaustion: Dict = None,
    anomaly_results: Dict = None,
    goals: List[Dict] = None,
) -> List[Dict]:
    """Public interface — returns list of dicts for API and DB storage."""
    engine = NotificationEngine()
    notes = engine.evaluate(user_stats, cash_exhaustion, anomaly_results, goals)
    return [
        {
            "title": n.title,
            "message": n.message,
            "notification_type": n.notification_type,
            "priority": n.priority,
            "trigger_reason": n.trigger_reason,
            "supporting_data": n.supporting_data,
            "ai_explanation": n.ai_explanation,
            "recommended_action": n.recommended_action,
        }
        for n in notes
    ]
