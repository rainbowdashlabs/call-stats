package de.chojo.callstats.controller;

import de.chojo.callstats.configuration.security.Role;
import de.chojo.callstats.services.CrewService;
import io.javalin.http.Context;

import static io.javalin.apibuilder.ApiBuilder.delete;
import static io.javalin.apibuilder.ApiBuilder.get;
import static io.javalin.apibuilder.ApiBuilder.patch;
import static io.javalin.apibuilder.ApiBuilder.path;
import static io.javalin.apibuilder.ApiBuilder.post;

public class CrewController implements RestController {
    private final CrewService crewService;

    public CrewController(CrewService crewService) {
        this.crewService = crewService;
    }

    @Override
    public void routes() {
        path("crew", () -> {
            post(this::create, Role.USER_WRITE);
            delete(this::remove, Role.USER_WRITE);
            patch(this::update, Role.USER_WRITE);
            path("{id}", () -> {
                get(this::byId, Role.USER_READ);
                get("calls", this::calls, Role.USER_READ);
                get("exercises", this::exercises, Role.USER_READ);
            });
        });
    }

    private void byId(Context context) {
    }

    private void create(Context ctx) {
    }

    private void remove(Context ctx) {
    }

    private void update(Context ctx) {
    }

    private void calls(Context ctx) {
    }

    private void exercises(Context context) {
    }
}
