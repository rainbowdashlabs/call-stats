package de.chojo.callstats.controller;

import de.chojo.callstats.configuration.security.Role;
import de.chojo.callstats.services.ExerciseService;
import io.javalin.http.Context;

import static io.javalin.apibuilder.ApiBuilder.delete;
import static io.javalin.apibuilder.ApiBuilder.get;
import static io.javalin.apibuilder.ApiBuilder.patch;
import static io.javalin.apibuilder.ApiBuilder.path;
import static io.javalin.apibuilder.ApiBuilder.post;

public class ExerciseController implements RestController {
    private final ExerciseService exerciseService;

    public ExerciseController(ExerciseService exerciseService) {
        this.exerciseService = exerciseService;
    }

    @Override
    public void routes() {
        path("exercise", () -> {
            post(this::create, Role.USER_WRITE);
            delete(this::remove, Role.USER_WRITE);
            patch(this::update, Role.USER_WRITE);
            path("{id}/member", () -> {
                patch(this::updateMember, Role.USER_WRITE);
                get(this::getMember, Role.USER_READ);
            });
        });
    }

    private void create(Context ctx) {
    }

    private void remove(Context ctx) {
    }

    private void update(Context ctx) {
    }

    private void updateMember(Context ctx) {
    }

    private void getMember(Context ctx) {
    }
}
