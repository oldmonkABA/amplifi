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

const SITE_ID = "default";

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
        <h2 className="text-2xl font-semibold">Calendar</h2>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setCurrentMonth(subMonths(currentMonth, 1))}
            className="px-3 py-1 rounded bg-gray-900 border border-gray-800 text-gray-300 hover:bg-gray-800 transition text-sm"
          >
            Prev
          </button>
          <span className="text-sm font-medium min-w-[140px] text-center">
            {format(currentMonth, "MMMM yyyy")}
          </span>
          <button
            onClick={() => setCurrentMonth(addMonths(currentMonth, 1))}
            className="px-3 py-1 rounded bg-gray-900 border border-gray-800 text-gray-300 hover:bg-gray-800 transition text-sm"
          >
            Next
          </button>
        </div>
      </div>

      <div className="grid grid-cols-7 gap-px mb-px">
        {["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].map((day) => (
          <div key={day} className="text-center text-xs text-gray-500 py-2 font-medium">
            {day}
          </div>
        ))}
      </div>

      <div className="grid grid-cols-7 gap-px bg-gray-800 border border-gray-800 rounded-lg overflow-hidden">
        {calendarDays.map((day) => {
          const items = getItemsForDay(day);
          const isCurrentMonth = isSameMonth(day, currentMonth);
          const isSelected = selectedDate && isSameDay(day, selectedDate);

          return (
            <button
              key={day.toISOString()}
              onClick={() => setSelectedDate(day)}
              className={`min-h-[80px] p-2 text-left transition ${
                isSelected
                  ? "bg-blue-900/30"
                  : isCurrentMonth
                    ? "bg-gray-900 hover:bg-gray-800/70"
                    : "bg-gray-950"
              }`}
            >
              <span
                className={`text-xs ${
                  isCurrentMonth ? "text-gray-300" : "text-gray-600"
                }`}
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
                        className={`w-1.5 h-1.5 rounded-full ${
                          item.status === "published"
                            ? "bg-blue-400"
                            : item.status === "scheduled"
                              ? "bg-amber-400"
                              : "bg-gray-500"
                        }`}
                      />
                      <span className="text-[10px] text-gray-400 truncate">{item.title}</span>
                    </div>
                  ))}
                  {items.length > 3 && (
                    <span className="text-[10px] text-gray-500">+{items.length - 3} more</span>
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
            <p className="text-sm text-gray-500">Nothing scheduled for this day.</p>
          ) : (
            <div className="space-y-2">
              {selectedItems.map((item) => (
                <div
                  key={item.id}
                  className="flex items-center gap-3 p-3 bg-gray-900 border border-gray-800 rounded-lg"
                >
                  <PlatformIcon platform={item.platform} />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">{item.title}</p>
                    <p className="text-xs text-gray-500 truncate">{item.body}</p>
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
