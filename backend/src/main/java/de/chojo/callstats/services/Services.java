package de.chojo.callstats.services;

import de.chojo.callstats.configuration.FileConfiguration;
import de.chojo.callstats.data.Repositories;

public class Services {
    private final CallService callService;
    private final CrewService crewService;
    private final ExerciseService exerciseService;
    private final JwtService jwtService;

    public Services(Repositories repositories, FileConfiguration fileConfiguration) {
        callService = new CallService(repositories);
        crewService = new CrewService(repositories);
        exerciseService = new ExerciseService(repositories);
        jwtService = new JwtService(fileConfiguration);
    }

    public CallService callService() {
        return callService;
    }

    public CrewService crewService() {
        return crewService;
    }

    public ExerciseService exerciseService() {
        return exerciseService;
    }

    public JwtService jwtService() {
        return jwtService;
    }
}
