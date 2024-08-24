package de.chojo.callstats.services;

import de.chojo.callstats.data.Repositories;

public class CallService {
    private final Repositories repositories;

    public CallService(Repositories repositories) {
        this.repositories = repositories;
    }
}
