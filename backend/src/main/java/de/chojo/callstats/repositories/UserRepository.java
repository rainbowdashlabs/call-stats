package de.chojo.callstats.repositories;

import de.chojo.callstats.data.Repositories;
import de.chojo.callstats.entites.User;

import java.time.Instant;

import static de.chojo.sadu.queries.api.call.Call.call;
import static de.chojo.sadu.queries.api.query.Query.query;
import static de.chojo.sadu.queries.converter.StandardValueConverter.INSTANT_SECONDS;

public class UserRepository extends AbstractRepository {
    public UserRepository(Repositories repositories) {
        super(repositories);
    }

    public User save(User user) {
        var saved = query("""
                INSERT
                INTO
                    users(id, name, password)
                VALUES
                    (?, ?, ?)
                ON CONFLICT (id)
                    DO UPDATE
                    SET
                        name     = excluded.name,
                        password = password
                RETURNING id, name, password""")
                .single(call().bind(user.id()).bind(user.name()).bind(user.password()))
                .mapAs(User.class)
                .first()
                .orElseThrow();
        updateRoles(saved.roles(user.roles()));
        return saved;
    }

    public void updateRoles(User user) {
        query("DELETE FROM user_roles WHERE user_id = ?")
                .single(call().bind(user.id()))
                .delete();
        query("INSERT INTO user_roles(user_id, role) VALUES(?,?)")
                .batch(user.roles().stream().map(e -> call().bind(user.id()).bind(e)))
                .insert();
    }

    public boolean consumeRefreshToken(User user, String token) {
        return query("DELETE FROM user_session WHERE user_id = ? AND token = ?")
                .single(call().bind(user.id()).bind(token))
                .delete()
                .changed();
    }

    public void addRefreshToken(User user, String token, Instant valid) {
        query("INSERT INTO user_session(user_id, token, valid_until) VALUES(?,?,?)")
                .single(call().bind(user.id()).bind(token).bind(valid, INSTANT_SECONDS))
                .insert();
    }

    public User findByName(String username) {
        return query("SELECT * FROM users WHERE name = ?")
                .single(call().bind(username))
                .mapAs(User.class)
                .first()
                .orElseThrow();
    }
}
