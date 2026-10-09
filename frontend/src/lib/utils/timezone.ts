/** Timezone utilities for frontend display. */

/**
 * Normalize a UTC timestamp string from the backend.
 *
 * SQLite's DEFAULT CURRENT_TIMESTAMP produces bare strings like
 * "2026-10-07 11:33:07" with no timezone suffix. When passed to
 * `new Date()`, the browser interprets them as **local time**, causing
 * displayed times to be offset by the user's UTC offset (e.g. 5h30m wrong
 * for UTC+5:30 users).
 *
 * This helper ensures all backend timestamps are parsed as UTC by:
 *  1. Replacing the space separator with "T" (ISO 8601 requirement).
 *  2. Appending "Z" when no explicit timezone offset (+HH:MM / Z) is present.
 */
function parseUTCDate(utcString: string): Date {
  if (!utcString) return new Date(NaN);

  let normalized = utcString.trim();

  // Replace space separator with "T" for ISO 8601 compliance
  // e.g. "2026-10-07 11:33:07" → "2026-10-07T11:33:07"
  normalized = normalized.replace(' ', 'T');

  // Append "Z" if no timezone offset is already present
  // Matches strings that already end with Z, +HH:MM, or -HH:MM
  if (!/Z|[+-]\d{2}:\d{2}$/.test(normalized)) {
    normalized += 'Z';
  }

  return new Date(normalized);
}

export interface TimezoneInfo {
  utc_time: string;
  local_time: string;
  local_date: string;
  local_datetime: string;
  timezone_offset: string;
  timezone_name: string;
  full_display: string;
  date_display: string;
}

export interface CommonTimezone {
  value: string;
  label: string;
  offset: string;
}

/**
 * Get user's timezone from browser
 */
export function getUserTimezone(): string {
  return Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC';
}

/**
 * Get timezone offset string (e.g., "GMT+5:30")
 */
export function getTimezoneOffset(timezone: string = getUserTimezone()): string {
  try {
    const parts = new Intl.DateTimeFormat("en-US", {
      timeZone: timezone,
      timeZoneName: "longOffset",
    }).formatToParts(new Date());

    const tz = parts.find(p => p.type === "timeZoneName")?.value; // e.g. GMT+05:30
    return tz ?? "GMT";
  } catch (error) {
    console.error("Error getting timezone offset:", error);
    return "GMT";
  }
}


/**
 * Format UTC timestamp for user display
 */
export function formatTimeForUser(
  utcString: string, 
  userTimezone: string = getUserTimezone()
): TimezoneInfo {
  try {
    const utcDate = parseUTCDate(utcString);
    
    if (isNaN(utcDate.getTime())) {
      throw new Error('Invalid UTC date');
    }
    
    // Format in user's timezone
    const options: Intl.DateTimeFormatOptions = {
      timeZone: userTimezone,
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    };
    
    const dateOptions: Intl.DateTimeFormatOptions = {
      timeZone: userTimezone,
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    };
    
    const datetimeOptions: Intl.DateTimeFormatOptions = {
      timeZone: userTimezone,
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false
    };
    
    const localTime = new Intl.DateTimeFormat('en-US', options).format(utcDate);
    const localDate = new Intl.DateTimeFormat('en-US', dateOptions).format(utcDate);
    const localDatetime = new Intl.DateTimeFormat('en-US', datetimeOptions).format(utcDate);
    
    const timezoneOffset = getTimezoneOffset(userTimezone);
    const timezoneName = Intl.DateTimeFormat('en-US', {
      timeZone: userTimezone,
      timeZoneName: 'short'
    }).formatToParts(utcDate).find(part => part.type === 'timeZoneName')?.value || userTimezone;
    
    const fullDisplay = `${localTime} (${timezoneOffset})`;
    const dateDisplay = `${localDate} at ${localTime} (${timezoneOffset})`;
    
    return {
      utc_time: utcString,
      local_time: localTime,
      local_date: localDate,
      local_datetime: localDatetime,
      timezone_offset: timezoneOffset,
      timezone_name: timezoneName,
      full_display: fullDisplay,
      date_display: dateDisplay
    };
    
  } catch (error) {
    console.error('Error formatting time for user:', error);
    return {
      utc_time: utcString,
      local_time: 'Unknown',
      local_date: 'Unknown',
      local_datetime: 'Unknown',
      timezone_offset: 'GMT',
      timezone_name: 'UTC',
      full_display: 'Unknown Time',
      date_display: 'Unknown Time'
    };
  }
}

/**
 * Get list of common timezones
 */
export function getCommonTimezones(): CommonTimezone[] {
  return [
    { value: 'UTC', label: 'UTC (GMT+0)', offset: 'GMT+0' },
    { value: 'America/New_York', label: 'Eastern Time (GMT-5/-4)', offset: 'GMT-5' },
    { value: 'America/Chicago', label: 'Central Time (GMT-6/-5)', offset: 'GMT-6' },
    { value: 'America/Denver', label: 'Mountain Time (GMT-7/-6)', offset: 'GMT-7' },
    { value: 'America/Los_Angeles', label: 'Pacific Time (GMT-8/-7)', offset: 'GMT-8' },
    { value: 'Europe/London', label: 'London (GMT+0/+1)', offset: 'GMT+0' },
    { value: 'Europe/Paris', label: 'Paris (GMT+1/+2)', offset: 'GMT+1' },
    { value: 'Europe/Berlin', label: 'Berlin (GMT+1/+2)', offset: 'GMT+1' },
    { value: 'Asia/Kolkata', label: 'India (GMT+5:30)', offset: 'GMT+5:30' },
    { value: 'Asia/Shanghai', label: 'China (GMT+8)', offset: 'GMT+8' },
    { value: 'Asia/Tokyo', label: 'Japan (GMT+9)', offset: 'GMT+9' },
    { value: 'Asia/Seoul', label: 'Korea (GMT+9)', offset: 'GMT+9' },
    { value: 'Asia/Singapore', label: 'Singapore (GMT+8)', offset: 'GMT+8' },
    { value: 'Australia/Sydney', label: 'Sydney (GMT+10/+11)', offset: 'GMT+10' },
    { value: 'Pacific/Auckland', label: 'New Zealand (GMT+12/+13)', offset: 'GMT+12' },
  ];
}

/**
 * Format relative time (e.g., "2 hours ago", "3 days ago")
 */
export function formatRelativeTime(utcString: string, userTimezone: string = getUserTimezone()): string {
  try {
    const utcDate = parseUTCDate(utcString);
    const now = new Date();
    const diffMs = now.getTime() - utcDate.getTime();
    const diffSeconds = Math.floor(diffMs / 1000);
    const diffMinutes = Math.floor(diffSeconds / 60);
    const diffHours = Math.floor(diffMinutes / 60);
    const diffDays = Math.floor(diffHours / 24);
    
    if (diffSeconds < 60) {
      return 'just now';
    } else if (diffMinutes < 60) {
      return `${diffMinutes} minute${diffMinutes > 1 ? 's' : ''} ago`;
    } else if (diffHours < 24) {
      return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    } else if (diffDays < 7) {
      return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
    } else {
      // For older dates, show the formatted date
      const timeInfo = formatTimeForUser(utcString, userTimezone);
      return timeInfo.date_display;
    }
  } catch (error) {
    console.error('Error formatting relative time:', error);
    return 'Unknown time';
  }
}

/**
 * Store user's preferred timezone in localStorage
 */
export function storeUserTimezone(timezone: string): void {
  try {
    localStorage.setItem('user_timezone', timezone);
  } catch (error) {
    console.error('Error storing user timezone:', error);
  }
}

/**
 * Get user's preferred timezone from localStorage
 */
export function getStoredUserTimezone(): string | null {
  try {
    return localStorage.getItem('user_timezone');
  } catch (error) {
    console.error('Error getting stored user timezone:', error);
    return null;
  }
}

/**
 * Get effective user timezone (stored preference or browser default)
 */
export function getEffectiveUserTimezone(): string {
  const stored = getStoredUserTimezone();
  if (stored) {
    return stored;
  }
  return getUserTimezone();
}
