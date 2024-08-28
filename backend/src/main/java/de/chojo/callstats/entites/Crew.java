package de.chojo.callstats.entites;

import de.chojo.sadu.mapper.annotation.MappingProvider;
import de.chojo.sadu.mapper.rowmapper.RowMapping;

public record Crew(
        Integer id,
        String name) {

    @MappingProvider({"id", "name"})
    public static RowMapping<Crew> mapper() {
        return row -> new Crew(row.getInt("id"), row.getString("name"));
    }
}
