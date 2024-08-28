package de.chojo.callstats.entites;

import de.chojo.callstats.configuration.security.Role;
import de.chojo.sadu.mapper.annotation.MappingProvider;
import de.chojo.sadu.mapper.rowmapper.RowMapping;

import java.util.Collections;
import java.util.Set;

public record User(Integer id, String name, String password, boolean enabled, Set<Role> roles) {

    @MappingProvider({"id", "name", "password", "enabled"})
    public static RowMapping<User> mapper() {
        return row -> new User(row.getInt("id"), row.getString("name"), row.getString("password"), row.getBoolean("enabled"), Collections.emptySet());
    }

    public User roles(Set<Role> roles) {
        return new User(id, name, password, enabled, roles);
    }
}
