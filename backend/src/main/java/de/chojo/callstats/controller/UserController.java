package de.chojo.callstats.controller;

import de.chojo.callstats.configuration.security.Role;
import de.chojo.callstats.entites.User;
import de.chojo.callstats.services.UserService;
import io.javalin.http.Context;
import io.javalin.http.HttpStatus;
import io.javalin.openapi.HttpMethod;
import io.javalin.openapi.OpenApi;
import io.javalin.openapi.OpenApiContent;
import io.javalin.openapi.OpenApiParam;
import io.javalin.openapi.OpenApiRequestBody;
import io.javalin.openapi.OpenApiResponse;

import static io.javalin.apibuilder.ApiBuilder.delete;
import static io.javalin.apibuilder.ApiBuilder.get;
import static io.javalin.apibuilder.ApiBuilder.patch;
import static io.javalin.apibuilder.ApiBuilder.path;
import static io.javalin.apibuilder.ApiBuilder.post;

public class UserController implements RestController {
    private final UserService userService;

    public UserController(UserService userService) {
        this.userService = userService;
    }

    @Override
    public void routes() {
        path("user", () -> {
            get("me", this::me, Role.USER);
            get(this::all, Role.USER);
            get("{id}", this::me, Role.USER);
            post(this::createUser, Role.ADMIN);
            delete(this::deleteUser, Role.ADMIN);
            patch(this::update, Role.ADMIN);
        });
    }

    @OpenApi(path = "api/user",
            summary = "Delete a user",
            tags = {"user"},
            methods = {HttpMethod.DELETE},
            requestBody = @OpenApiRequestBody(
                    required = true,
                    content = {@OpenApiContent(from = User.class)}))
    private void deleteUser(Context ctx) {

    }

    @OpenApi(path = "api/user",
            summary = "Get all users",
            tags = {"user"},
            methods = {HttpMethod.GET},
            responses = {
                    @OpenApiResponse(
                            status = "200",
                            description = "All existing users",
                            content = {@OpenApiContent(from = User[].class)})})
    private void all(Context ctx) {

    }

    @OpenApi(path = "api/user",
            summary = "Update an existing user",
            tags = {"user"},
            methods = {HttpMethod.PATCH},
            responses = {
                    @OpenApiResponse(
                            status = "202",
                            description = "The user of the updated user",
                            content = {@OpenApiContent(from = User.class)})},
            requestBody = @OpenApiRequestBody(
                    required = true,
                    content = {@OpenApiContent(from = User.class)}))
    private void update(Context context) {
    }

    @OpenApi(path = "api/user",
            summary = "Create a new user",
            tags = {"user"},
            methods = {HttpMethod.POST},
            responses = {
                    @OpenApiResponse(
                            status = "202",
                            description = "The user object of created user",
                            content = {@OpenApiContent(from = User.class)})},
            requestBody = @OpenApiRequestBody(
                    required = true,
                    content = {@OpenApiContent(from = User.class)}))
    public void createUser(Context ctx) {
        User user = ctx.bodyAsClass(User.class);
        User created = userService.createUser(user);
        ctx.status(HttpStatus.ACCEPTED);
        ctx.json(created);
    }

    @OpenApi(path = "api/user/me",
            summary = "Get the currently logged in user",
            tags = {"user"},
            responses = {
                    @OpenApiResponse(
                            status = "200",
                            description = "The user object of the currently logged in user",
                            content = {@OpenApiContent(from = User.class)})})
    private void me(Context ctx) {

    }

    @OpenApi(path = "api/user/{id}",
            summary = "Get a user by id",
            tags = {"user"},
            pathParams = {@OpenApiParam(
                    name = "id",
                    description = "Id of the requested user",
                    required = true,
                    type = Integer.class)},
            responses = {
                    @OpenApiResponse(
                            status = "200",
                            description = "The user object of the requested user",
                            content = {@OpenApiContent(from = User.class)})})
    private void id(Context ctx) {

    }
}
