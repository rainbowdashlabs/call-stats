package de.chojo.callstats.entites.security;

public record TokenResponse(TokenDto token, TokenDto refresh) {

}
