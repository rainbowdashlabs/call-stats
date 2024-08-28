package de.chojo.callstats.data;

import de.chojo.callstats.repositories.CallRepository;
import de.chojo.callstats.repositories.CrewRepository;
import de.chojo.callstats.repositories.ExercisesRepository;
import de.chojo.callstats.repositories.QualificationRepository;

public class Repositories {
    private final CallRepository callRepository;
    private final CrewRepository crewRepository;
    private final ExercisesRepository exercisesRepository;
    private final QualificationRepository qualificationRepository;

    public Repositories() {
        callRepository = new CallRepository(this);
        crewRepository = new CrewRepository(this);
        exercisesRepository = new ExercisesRepository(this);
        qualificationRepository = new QualificationRepository(this);
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

    public QualificationRepository qualificationRepository() {
        return qualificationRepository;
    }
}
