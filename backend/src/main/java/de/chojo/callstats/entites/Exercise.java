package de.chojo.callstats.entites;

import de.chojo.sadu.mapper.annotation.MappingProvider;
import de.chojo.sadu.mapper.rowmapper.RowMapping;

import java.time.LocalDate;

import static de.chojo.sadu.queries.converter.StandardValueConverter.LOCAL_DATE;

public record Exercise(Integer id, LocalDate date, Integer hours, Integer minutes, String subject) {
    @MappingProvider({"id", "date", "hours", "minutes", "subject"})
    public static RowMapping<Exercise> mapper() {
        return row -> new Exercise(
                row.getInt("id"),
                row.get("date", LOCAL_DATE),
                row.getInt("hours"),
                row.getInt("minutes"),
                row.getString("subject"));
    }
}
