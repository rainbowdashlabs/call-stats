package de.chojo.callstats.controller;

import de.chojo.callstats.configuration.security.Role;
import io.javalin.http.Context;

import static io.javalin.apibuilder.ApiBuilder.delete;
import static io.javalin.apibuilder.ApiBuilder.get;
import static io.javalin.apibuilder.ApiBuilder.patch;
import static io.javalin.apibuilder.ApiBuilder.path;
import static io.javalin.apibuilder.ApiBuilder.post;

public class UserController implements RestController {
    @Override
    public void routes() {
        path("user", () -> {
            get("me", this::me, Role.ANYONE);
            post(this::createUser, Role.ADMIN);
            delete(this::deleteUser, Role.ADMIN);
            patch(this::update, Role.ADMIN);
        });
    }

    private void update(Context context) {

    }

    private void deleteUser(Context ctx) {

    }

    private void createUser(Context ctx) {

    }

    private void me(Context ctx) {

    }
}
