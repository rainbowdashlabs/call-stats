const UMLAUT_PLAIN: Record<string, string> = {'ä': 'a', 'ö': 'o', 'ü': 'u', 'ß': 's'}
const UMLAUT_EXPANDED: Record<string, string> = {'ä': 'ae', 'ö': 'oe', 'ü': 'ue', 'ß': 'ss'}

const TIER_WORD_PREFIX = 2
const TIER_INITIALS = 3
const TIER_SUBSTRING = 4
const TIER_ACRONYM = 5
const POSITION_PENALTY = 0.01

function normalize(text: string, folding: Record<string, string>): string[] {
    return text
        .toLowerCase()
        .replace(/[äöüß]/g, c => folding[c]!)
        .replace(/[^a-z0-9]+/g, ' ')
        .trim()
        .split(' ')
        .filter(Boolean)
}

interface Hit {
    tier: number
    nextWord: number
}

function matchesInitials(term: string, words: string[], start: number): boolean {
    if (term.length < 2 || start + term.length > words.length) return false
    for (let i = 0; i < term.length; i++) {
        if (!words[start + i]!.startsWith(term[i]!)) return false
    }
    return true
}

function matchesAcronym(term: string, word: string): boolean {
    if (term.length < 2 || !word.startsWith(term[0]!)) return false
    let cursor = 0
    for (const letter of word) {
        if (letter === term[cursor]) cursor++
        if (cursor === term.length) return true
    }
    return false
}

function findTerm(term: string, words: string[], from: number): Hit | null {
    for (let i = from; i < words.length; i++) {
        if (words[i]!.startsWith(term)) {
            return {tier: (i === 0 ? 1 : TIER_WORD_PREFIX) + i * POSITION_PENALTY, nextWord: i + 1}
        }
    }
    for (let i = from; i < words.length; i++) {
        if (matchesInitials(term, words, i)) {
            return {tier: TIER_INITIALS + i * POSITION_PENALTY, nextWord: i + term.length}
        }
    }
    for (let i = from; i < words.length; i++) {
        if (words[i]!.includes(term)) {
            return {tier: TIER_SUBSTRING + i * POSITION_PENALTY, nextWord: i + 1}
        }
    }
    for (let i = from; i < words.length; i++) {
        if (matchesAcronym(term, words[i]!)) {
            return {tier: TIER_ACRONYM + i * POSITION_PENALTY, nextWord: i + 1}
        }
    }
    return null
}

function scoreWords(terms: string[], words: string[]): number | null {
    let total = 0
    let cursor = 0
    for (const term of terms) {
        const hit = findTerm(term, words, cursor)
        if (hit === null) return null
        total += hit.tier
        cursor = hit.nextWord
    }
    return total
}

/**
 * Rates how well a query describes a label. All query terms must match, in the order they
 * were typed. A lower score is a better match: a label prefix beats a word prefix, which
 * beats the initials of consecutive words, which beats a substring, which beats the letters of
 * a compound word ("bma" finds "Brandmeldeanlage"). Returns null when the
 * label does not match at all. Umlauts match both their plain and their spelled-out form,
 * so "ol" and "oel" both find "Ölspur".
 */
export function score(query: string, label: string): number | null {
    const plain = scoreWords(normalize(query, UMLAUT_PLAIN), normalize(label, UMLAUT_PLAIN))
    const expanded = scoreWords(normalize(query, UMLAUT_EXPANDED), normalize(label, UMLAUT_EXPANDED))
    if (plain === null) return expanded
    if (expanded === null) return plain
    return Math.min(plain, expanded)
}

/**
 * Filters items to those matching the query and orders them by match quality, falling back
 * to the weight (a usage count, higher first) and then the label. An empty query keeps every
 * item and orders it by weight alone.
 */
export function rank<T>(items: T[],
                        valueMapper: (item: T) => string,
                        query: string,
                        weightMapper: (item: T) => number = () => 0): T[] {
    const trimmed = query.trim()
    const scored: { item: T, score: number, label: string }[] = []
    for (const item of items) {
        const label = valueMapper(item)
        const value = trimmed ? score(trimmed, label) : 0
        if (value === null) continue
        scored.push({item, score: value, label})
    }
    scored.sort((a, b) => a.score - b.score
        || weightMapper(b.item) - weightMapper(a.item)
        || a.label.localeCompare(b.label))
    return scored.map(e => e.item)
}
