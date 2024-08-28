package de.chojo.callstats.services;

import de.chojo.callstats.configuration.security.Role;
import de.chojo.callstats.data.Repositories;
import de.chojo.callstats.entites.User;
import de.chojo.callstats.repositories.UserRepository;
import org.springframework.security.crypto.factory.PasswordEncoderFactories;
import org.springframework.security.crypto.password.PasswordEncoder;

import java.util.Optional;
import java.util.Set;

public class UserService {
    private final PasswordEncoder passwordEncoder = PasswordEncoderFactories.createDelegatingPasswordEncoder();
    private final UserRepository userRepository;

    public UserService(Repositories repositories) {
        userRepository = repositories.userRepository();
    }

    public String encodePassword(String password) {
        return passwordEncoder.encode(password);
    }

    public User createUser(User user) {
        return userRepository.save(new User(null, user.name(), encodePassword(user.password()), user.enabled(), Set.of(Role.USER, Role.USER_READ)));
    }

    public Optional<User> authUser(String username, String password) {
        User byName = userRepository.findByName(username);
        if (byName.password().equals(encodePassword(password))) {
            return Optional.of(byName);
        }
        return Optional.empty();
    }
}
