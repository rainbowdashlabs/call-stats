package de.chojo.callstats.services;

import de.chojo.callstats.data.Repositories;

public class ExerciseService {
    private final Repositories repositories;

    public ExerciseService(Repositories repositories) {
        this.repositories = repositories;
    }
}
