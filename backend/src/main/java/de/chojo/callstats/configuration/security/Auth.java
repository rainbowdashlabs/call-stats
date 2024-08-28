package de.chojo.callstats.configuration.security;

import de.chojo.callstats.entites.User;
import de.chojo.callstats.services.JwtService;
import io.javalin.http.Context;
import io.javalin.http.Header;
import io.javalin.http.UnauthorizedResponse;
import io.javalin.security.RouteRole;

import java.util.Optional;
import java.util.Set;

public class Auth {
    private final JwtService jwtService;

    public Auth(JwtService jwtService) {
        this.jwtService = jwtService;
    }

    public void handleAccess(Context ctx) {
        Set<RouteRole> routeRoles = ctx.routeRoles();
        if (routeRoles.contains(Role.ANYONE)) return;

        String header = ctx.header(Header.AUTHORIZATION);
        if (header == null) {
            ctx.header(Header.WWW_AUTHENTICATE, "Bearer");
            throw new UnauthorizedResponse();
        }
        String token = header.replace("Bearer ", "");
        User user = jwtService.extractUser(token);
        if (!jwtService.isTokenValid(token, user, JwtService.LOGIN_CLAIM)) {
            throw new UnauthorizedResponse();
        }

        if (user.roles().stream().anyMatch(routeRoles::contains)) {
            return;
        }
        throw new UnauthorizedResponse();
    }
}
