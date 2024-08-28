package de.chojo.callstats.configuration.security;

import io.javalin.security.RouteRole;

public enum Role implements RouteRole {
    ANYONE,
    USER_WRITE,
    USER_READ,
    ADMIN
}
