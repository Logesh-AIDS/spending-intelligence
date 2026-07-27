import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

// Accepts either the monthly trend shape or the spending-trend API shape
interface TrendData {
  label?: string;   // from spending-trend API
  month?: string;   // legacy prop shape
  amount?: number;  // from spending-trend API (spending only)
  expenses?: number;
  income?: number;
}

interface TrendChartProps {
  data: TrendData[];
}

const formatRupee = (value: number) =>
  `₹${value.toLocaleString('en-IN', { maximumFractionDigits: 0 })}`;

export function TrendChart({ data }: TrendChartProps) {
  // Normalise both data shapes into a unified format
  const normalised = data.map((d) => ({
    label: d.label || d.month || '',
    expenses: d.expenses ?? d.amount ?? 0,
    income: d.income ?? 0,
  }));

  return (
    <ResponsiveContainer width="100%" height={300}>
      <AreaChart data={normalised}>
        <defs>
          <linearGradient id="incomeGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#10b981" stopOpacity={0.15} />
            <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
          </linearGradient>
          <linearGradient id="expenseGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#ef4444" stopOpacity={0.15} />
            <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
        <XAxis dataKey="label" tick={{ fontSize: 12 }} />
        <YAxis tickFormatter={formatRupee} tick={{ fontSize: 11 }} width={70} />
        <Tooltip formatter={(value: number) => formatRupee(value)} />
        <Legend />
        {normalised[0]?.income > 0 && (
          <Area
            type="monotone"
            dataKey="income"
            stroke="#10b981"
            strokeWidth={2}
            fill="url(#incomeGrad)"
            name="Income"
          />
        )}
        <Area
          type="monotone"
          dataKey="expenses"
          stroke="#ef4444"
          strokeWidth={2}
          fill="url(#expenseGrad)"
          name="Expenses"
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}
