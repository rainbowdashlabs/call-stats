package de.chojo.callstats.controller;

import de.chojo.callstats.services.CrewService;

public class CrewController {
    private final CrewService crewService;

    public CrewController(CrewService crewService) {
        this.crewService = crewService;
    }
}
