package de.chojo.callstats.services;

import de.chojo.callstats.configuration.security.Role;
import de.chojo.callstats.data.Repositories;
import de.chojo.callstats.entites.User;
import de.chojo.callstats.entites.security.TokenDto;
import de.chojo.callstats.entites.security.TokenResponse;
import de.chojo.callstats.repositories.UserRepository;
import io.javalin.http.UnauthorizedResponse;
import org.springframework.security.crypto.factory.PasswordEncoderFactories;
import org.springframework.security.crypto.password.PasswordEncoder;

import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.HashSet;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;

import static de.chojo.callstats.services.JwtService.LOGIN_CLAIM;
import static de.chojo.callstats.services.JwtService.REFRESH_CLAIM;

public class UserService {
    private final PasswordEncoder passwordEncoder = PasswordEncoderFactories.createDelegatingPasswordEncoder();
    private final UserRepository userRepository;
    private final Services services;

    public UserService(Repositories repositories, Services services) {
        userRepository = repositories.userRepository();
        this.services = services;
    }

    public String encodePassword(String password) {
        return passwordEncoder.encode(password);
    }

    public User createUser(User user) {
        Set<Role> roles = Objects.requireNonNullElse(user.roles(), new HashSet<>());
        roles.addAll(Set.of(Role.USER, Role.USER_READ));
        return userRepository.save(new User(null, user.name(), encodePassword(user.password()), user.enabled(), roles));
    }

    public Optional<User> authUser(String username, String password) {
        User byName = userRepository.findByName(username);
        if (byName.password().equals(encodePassword(password))) {
            return Optional.of(byName);
        }
        return Optional.empty();
    }

    public TokenResponse login(User user) {
        return generateToken(user);
    }

    public TokenResponse refresh(User user, String token) {
        boolean consumed = userRepository.consumeRefreshToken(user, token);
        if (!consumed) throw new UnauthorizedResponse();
        return generateToken(user);
    }

    private TokenResponse generateToken(User user) {
        var token = new TokenResponse(
                new TokenDto(jwtService().generateToken(LOGIN_CLAIM, user, jwtService().jwtExpiration()), jwtService().jwtExpiration()),
                new TokenDto(jwtService().generateToken(REFRESH_CLAIM, user, jwtService().jwtRefreshExpiration()), jwtService().jwtRefreshExpiration())
        );
        userRepository.addRefreshToken(user, token.refresh().token(), Instant.now().plus(token.refresh().expiresIn(), ChronoUnit.MILLIS));
        return token;
    }

    public JwtService jwtService() {
        return services.jwtService();
    }
}
