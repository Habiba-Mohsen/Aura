import { LucideIcon } from 'lucide-react';
import { cn } from '@renderer/lib/utils';

interface HeadingProps {
  title: string;
  description: string;
  icon: LucideIcon;
  iconColor?: string;
  bgColor?: string;
}

export default function Heading({
  title,
  description,
  icon: Icon,
  iconColor,
  bgColor
}: HeadingProps) {
  return (
    <div className="px-4 lg:px-8 pt-0 flex items-center gap-x-3 mb-6">
      <div className={cn('p-2 w-fit rounded-md', bgColor)}>
        <Icon className={cn('w-10 h-10', iconColor)} />
      </div>
      <div>
        <h2 className="text-3xl font-bold">{title}</h2>
        <h3 className="text-sm text-muted-foreground">{description}</h3>
      </div>
    </div>
  );
}
