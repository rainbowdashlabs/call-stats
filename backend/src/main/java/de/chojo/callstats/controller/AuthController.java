package de.chojo.callstats.controller;

import de.chojo.callstats.configuration.security.Role;
import de.chojo.callstats.entites.security.LoginDto;
import de.chojo.callstats.entites.security.TokenResponse;
import de.chojo.callstats.services.Services;
import de.chojo.callstats.services.UserService;
import io.javalin.http.BadRequestResponse;
import io.javalin.http.Context;
import io.javalin.http.HttpStatus;
import io.javalin.http.UnauthorizedResponse;
import io.javalin.openapi.HttpMethod;
import io.javalin.openapi.OpenApi;
import io.javalin.openapi.OpenApiContent;
import io.javalin.openapi.OpenApiParam;
import io.javalin.openapi.OpenApiRequestBody;
import io.javalin.openapi.OpenApiResponse;

import static io.javalin.apibuilder.ApiBuilder.path;
import static io.javalin.apibuilder.ApiBuilder.post;

public class AuthController implements RestController {
    private final UserService userService;

    public AuthController(Services services) {
        this.userService = services.userService();
    }

    @Override
    public void routes() {
        path("auth", () -> {
            post("login", this::login, Role.ANYONE);
            post("refresh", this::refresh, Role.ANYONE);
        });
    }

    @OpenApi(path = "api/auth/login",
            methods = {HttpMethod.POST},
            tags = {"auth"},
            description = "Login and receive a session and refresh token",
            requestBody = @OpenApiRequestBody(
                    required = true,
                    description = "Login payload",
                    content = {
                            @OpenApiContent(from = LoginDto.class)}))
    private void login(Context ctx) {
        LoginDto loginDto = ctx.bodyAsClass(LoginDto.class);
        var optUser = userService.authUser(loginDto.username(), loginDto.password());
        if (optUser.isEmpty()) throw new UnauthorizedResponse();
        ctx.status(HttpStatus.ACCEPTED);
        ctx.json(userService.login(optUser.get()));
    }

    @OpenApi(path = "api/auth/refresh",
            methods = {HttpMethod.POST},
            tags = {"auth"},
            description = "Receive a new session and refresh token",
            queryParams = {
                    @OpenApiParam(
                            name = "token",
                            description = "The refresh token",
                            required = true)},
            responses = {
                    @OpenApiResponse(
                            status = "202",
                            content = {@OpenApiContent(from = TokenResponse.class)},
                            description = "When the token was valid"),
                    @OpenApiResponse(
                            status = "401",
                            description = "The refresh token was invalid")})
    private void refresh(Context ctx) {
        String refresh = ctx.queryParam("token");
        if (refresh == null) throw new BadRequestResponse("Token parameter is missing");
        TokenResponse token = userService.refresh(ctx.attribute("user"), refresh);
        ctx.status(HttpStatus.ACCEPTED);
        ctx.json(token);
    }

    private void logout(Context ctx) {

    }
}
