package de.chojo.callstats.controller;

import de.chojo.callstats.configuration.security.Role;
import de.chojo.callstats.entites.User;
import de.chojo.callstats.entites.security.LoginDto;
import de.chojo.callstats.entites.security.TokenDto;
import de.chojo.callstats.entites.security.TokenResponse;
import de.chojo.callstats.services.JwtService;
import de.chojo.callstats.services.Services;
import de.chojo.callstats.services.UserService;
import io.javalin.http.Context;
import io.javalin.http.HttpStatus;
import io.javalin.http.UnauthorizedResponse;

import static de.chojo.callstats.services.JwtService.LOGIN_CLAIM;
import static de.chojo.callstats.services.JwtService.REFRESH_CLAIM;
import static io.javalin.apibuilder.ApiBuilder.path;
import static io.javalin.apibuilder.ApiBuilder.post;

public class AuthController implements RestController {
    private final UserService userService;
    private final JwtService jwtService;

    public AuthController(Services services) {
        this.userService = services.userService();
        this.jwtService = services.jwtService();
    }

    @Override
    public void routes() {
        path("auth", () -> {
            post("login", this::login, Role.ANYONE);
            post("refresh", this::refresh, Role.ANYONE);
        });
    }

    private void login(Context ctx) {
        LoginDto loginDto = ctx.bodyAsClass(LoginDto.class);
        var optUser = userService.authUser(loginDto.username(), loginDto.password());
        if (!optUser.isEmpty()) throw new UnauthorizedResponse();
        User user = optUser.get();
        TokenResponse tokenResponse = new TokenResponse(
                new TokenDto(jwtService.generateToken(LOGIN_CLAIM, user, jwtService.jwtExpiration()), jwtService.jwtExpiration()),
                new TokenDto(jwtService.generateToken(REFRESH_CLAIM, user, jwtService.jwtRefreshExpiration()), jwtService.jwtRefreshExpiration())
        );
        ctx.status(HttpStatus.ACCEPTED);
        ctx.json(tokenResponse);
    }

    private void refresh(Context ctx) {

    }

    private void logout(Context ctx) {

    }
}
