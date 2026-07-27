import { Card } from '@/components/ui/card';
import { ArrowUp, ArrowDown } from 'lucide-react';

interface StatCardProps {
  title: string;
  value: number;
  trend?: 'up' | 'down';
  format?: 'currency' | 'number' | 'percent';
}

export function StatCard({ title, value, trend, format = 'number' }: StatCardProps) {
  const formattedValue =
    format === 'currency'
      ? `$${value.toFixed(2)}`
      : format === 'percent'
        ? `${value.toFixed(1)}%`
        : value.toLocaleString();

  return (
    <Card className="p-6">
      <div className="space-y-2">
        <p className="text-sm text-slate-600">{title}</p>
        <div className="flex items-end justify-between">
          <p className="text-3xl font-bold">{formattedValue}</p>
          {trend && (
            <div className={`flex items-center gap-1 text-sm ${trend === 'up' ? 'text-green-600' : 'text-red-600'}`}>
              {trend === 'up' ? <ArrowUp size={16} /> : <ArrowDown size={16} />}
              {trend === 'up' ? 'Up' : 'Down'}
            </div>
          )}
        </div>
      </div>
    </Card>
  );
}
