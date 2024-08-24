package de.chojo.callstats.controller;

import de.chojo.callstats.services.CallService;

public class CallController {
    private final CallService callService;

    public CallController(CallService callService) {
        this.callService = callService;
    }
}
