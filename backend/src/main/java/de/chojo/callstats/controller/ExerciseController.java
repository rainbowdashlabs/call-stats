package de.chojo.callstats.controller;

import de.chojo.callstats.services.ExerciseService;

public class ExerciseController {
    private final ExerciseService exerciseService;

    public ExerciseController(ExerciseService exerciseService) {
        this.exerciseService = exerciseService;
    }
}
