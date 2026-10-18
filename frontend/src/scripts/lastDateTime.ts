import {ADateTime} from "./datetime.ts";

const PREFIX = "last-datetime:"

/**
 * Returns the date and time that was last stored under the given key, or now if nothing was stored yet.
 */
export function loadLastDateTime(key: string): ADateTime {
    try {
        const raw = localStorage.getItem(PREFIX + key)
        if (raw !== null) {
            const timestamp = Number(raw)
            if (Number.isFinite(timestamp)) {
                return ADateTime.fromDate(new Date(timestamp * 1000))
            }
        }
    } catch (_) {
        // storage not available, fall through to now
    }
    return ADateTime.now()
}

/**
 * Remembers the given date and time under the key so the next form keeps it instead of reverting to today.
 */
export function storeLastDateTime(key: string, value: ADateTime) {
    try {
        localStorage.setItem(PREFIX + key, value.toUnixTimestamp().toString())
    } catch (_) {
        // storage not available, nothing to do
    }
}
