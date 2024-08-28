package de.chojo.callstats.entites;

import io.javalin.security.RouteRole;

import java.util.Set;

public record User(Integer id, String name, String password, Set<RouteRole> roles) {
}
