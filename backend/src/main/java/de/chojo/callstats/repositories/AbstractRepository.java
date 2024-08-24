package de.chojo.callstats.repositories;

import de.chojo.callstats.data.Repositories;

public class AbstractRepository {
    protected final Repositories repositories;

    public AbstractRepository(Repositories repositories) {
        this.repositories = repositories;
    }
}
