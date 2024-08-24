package de.chojo.callstats.data;

import de.chojo.callstats.repositories.CallRepository;
import de.chojo.callstats.repositories.CrewRepository;
import de.chojo.callstats.repositories.ExercisesRepository;

public class Repositories {
    private final CallRepository callRepository;
    private final CrewRepository crewRepository;
    private final ExercisesRepository exercisesRepository;

    public Repositories() {
        callRepository = new CallRepository(this);
        crewRepository = new CrewRepository(this);
        exercisesRepository = new ExercisesRepository(this);
    }

    public CallRepository callRepository() {
        return callRepository;
    }

    public CrewRepository crewRepository() {
        return crewRepository;
    }

    public ExercisesRepository exercisesRepository() {
        return exercisesRepository;
    }
}
