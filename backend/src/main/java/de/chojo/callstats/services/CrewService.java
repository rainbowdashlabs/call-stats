package de.chojo.callstats.services;

import de.chojo.callstats.data.Repositories;

public class CrewService {
    private final Repositories repositories;

    public CrewService(Repositories repositories) {
        this.repositories = repositories;
    }
}
