export function select<T>(items: T[], value_mapper: (item: T) => string, input: string, all_on_empty:boolean = true): T[] {
    if (input === undefined || input === null || !input.trim()) {
        if(all_on_empty){
        return items;
        }
        return []
    }

    const searchTerms = input.trim().toLowerCase().split(/\s+/);

    return items.filter(item => {
        const value = value_mapper(item).toLowerCase();
        const words = value.split(/\s+/);

        let termIndex = 0;

        for (const word of words) {
            if (termIndex >= searchTerms.length) {
                break;
            }

            if (word.startsWith(searchTerms[termIndex]!)) {
                termIndex++;
            }
        }

        return termIndex === searchTerms.length;
    });
}