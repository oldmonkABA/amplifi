"use client";

import { useState, useMemo } from "react";
import { useApi } from "@/hooks/use-api";
import { getCalendar } from "@/lib/api/content";
import { StatusBadge } from "@/components/status-badge";
import { PlatformIcon } from "@/components/platform-icon";
import {
  startOfMonth,
  endOfMonth,
  startOfWeek,
  endOfWeek,
  eachDayOfInterval,
  format,
  isSameMonth,
  isSameDay,
  addMonths,
  subMonths,
} from "date-fns";
import type { ContentCalendarResponse, ContentResponse } from "@/types/api";

import { DEV_SITE_ID as SITE_ID } from "@/lib/constants";

export default function CalendarPage() {
  const [currentMonth, setCurrentMonth] = useState(new Date());
  const [selectedDate, setSelectedDate] = useState<Date | null>(null);

  const monthStart = startOfMonth(currentMonth);
  const monthEnd = endOfMonth(currentMonth);

  const { data } = useApi<ContentCalendarResponse>(
    (token) =>
      getCalendar(token, SITE_ID, monthStart.toISOString(), monthEnd.toISOString()),
    [currentMonth.getMonth(), currentMonth.getFullYear()],
  );

  const calendarDays = useMemo(() => {
    const start = startOfWeek(monthStart);
    const end = endOfWeek(monthEnd);
    return eachDayOfInterval({ start, end });
  }, [currentMonth]);

  const getItemsForDay = (day: Date): ContentResponse[] => {
    if (!data?.items) return [];
    return data.items.filter((item) => {
      const date = item.scheduled_at || item.published_at;
      if (!date) return false;
      return isSameDay(new Date(date), day);
    });
  };

  const selectedItems = selectedDate ? getItemsForDay(selectedDate) : [];

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-3xl">Calendar</h2>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setCurrentMonth(subMonths(currentMonth, 1))}
            className="btn-ghost"
          >
            Prev
          </button>
          <span
            className="text-sm font-medium min-w-[140px] text-center"
            style={{ color: 'var(--text-primary)' }}
          >
            {format(currentMonth, "MMMM yyyy")}
          </span>
          <button
            onClick={() => setCurrentMonth(addMonths(currentMonth, 1))}
            className="btn-ghost"
          >
            Next
          </button>
        </div>
      </div>

      <div className="grid grid-cols-7 gap-px mb-px">
        {["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].map((day) => (
          <div
            key={day}
            className="text-center text-xs py-2 font-medium"
            style={{ color: 'var(--text-tertiary)' }}
          >
            {day}
          </div>
        ))}
      </div>

      <div
        className="card grid grid-cols-7 gap-px overflow-hidden"
        style={{ background: 'var(--border)', padding: 0 }}
      >
        {calendarDays.map((day) => {
          const items = getItemsForDay(day);
          const isCurrentMonth = isSameMonth(day, currentMonth);
          const isSelected = selectedDate && isSameDay(day, selectedDate);

          return (
            <button
              key={day.toISOString()}
              onClick={() => setSelectedDate(day)}
              className="min-h-[80px] p-2 text-left transition"
              style={{
                background: isSelected
                  ? 'var(--accent-dim)'
                  : isCurrentMonth
                    ? 'var(--bg-secondary)'
                    : 'var(--bg-primary)',
              }}
              onMouseEnter={(e) => {
                if (!isSelected) {
                  (e.currentTarget as HTMLButtonElement).style.background = 'var(--bg-hover)';
                }
              }}
              onMouseLeave={(e) => {
                (e.currentTarget as HTMLButtonElement).style.background = isSelected
                  ? 'var(--accent-dim)'
                  : isCurrentMonth
                    ? 'var(--bg-secondary)'
                    : 'var(--bg-primary)';
              }}
            >
              <span
                className="text-xs"
                style={{ color: isCurrentMonth ? 'var(--text-primary)' : 'var(--text-tertiary)' }}
              >
                {format(day, "d")}
              </span>
              {items.length > 0 && (
                <div className="mt-1 space-y-0.5">
                  {items.slice(0, 3).map((item) => (
                    <div
                      key={item.id}
                      className="flex items-center gap-1"
                    >
                      <div
                        className="w-1.5 h-1.5 rounded-full"
                        style={{
                          background:
                            item.status === "published"
                              ? 'var(--accent)'
                              : item.status === "scheduled"
                                ? 'var(--amber)'
                                : 'var(--text-tertiary)',
                        }}
                      />
                      <span
                        className="text-[10px] truncate"
                        style={{ color: 'var(--text-tertiary)' }}
                      >
                        {item.title}
                      </span>
                    </div>
                  ))}
                  {items.length > 3 && (
                    <span
                      className="text-[10px]"
                      style={{ color: 'var(--text-tertiary)' }}
                    >
                      +{items.length - 3} more
                    </span>
                  )}
                </div>
              )}
            </button>
          );
        })}
      </div>

      {selectedDate && (
        <div className="mt-6">
          <h3 className="text-lg font-medium mb-3">
            {format(selectedDate, "EEEE, MMMM d, yyyy")}
          </h3>
          {selectedItems.length === 0 ? (
            <p className="text-sm" style={{ color: 'var(--text-tertiary)' }}>
              Nothing scheduled for this day.
            </p>
          ) : (
            <div className="space-y-2">
              {selectedItems.map((item) => (
                <div
                  key={item.id}
                  className="card flex items-center gap-3 p-3"
                >
                  <PlatformIcon platform={item.platform} />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">{item.title}</p>
                    <p className="text-xs truncate" style={{ color: 'var(--text-tertiary)' }}>
                      {item.body}
                    </p>
                  </div>
                  <StatusBadge status={item.status} />
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
