package de.chojo.callstats.controller;

import de.chojo.callstats.configuration.security.Role;
import io.javalin.http.Context;

import static io.javalin.apibuilder.ApiBuilder.path;
import static io.javalin.apibuilder.ApiBuilder.post;

public class AuthController implements RestController {

    @Override
    public void routes() {
        path("auth", () -> {
            post("login", this::login, Role.ANYONE);
            post("refresh", this::refresh, Role.ANYONE);
        });
    }

    private void login(Context ctx) {

    }

    private void refresh(Context ctx) {

    }

    private void logout(Context ctx) {

    }
}
