package de.chojo.callstats.entites.security;

public record TokenDto(String token, long expiresIn) {
}
