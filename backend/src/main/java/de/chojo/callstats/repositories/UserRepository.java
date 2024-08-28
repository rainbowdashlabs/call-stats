package de.chojo.callstats.repositories;

import de.chojo.callstats.data.Repositories;
import de.chojo.callstats.entites.User;

import static de.chojo.sadu.queries.api.call.Call.call;
import static de.chojo.sadu.queries.api.query.Query.query;

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

    public User findByName(String username) {
        return query("SELECT * FROM users WHERE name = ?")
                .single(call().bind(username))
                .mapAs(User.class)
                .first()
                .orElseThrow();
    }
}
