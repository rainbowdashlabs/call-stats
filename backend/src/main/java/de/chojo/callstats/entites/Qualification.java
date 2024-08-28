package de.chojo.callstats.entites;

import de.chojo.sadu.mapper.rowmapper.RowMapping;

import java.time.LocalDate;

import static de.chojo.callstats.entites.QualificationType.CONVERTER;
import static de.chojo.sadu.queries.converter.StandardValueConverter.LOCAL_DATE;

public record Qualification(String crewId, QualificationType qualification, LocalDate since) {
    public static RowMapping<Qualification> mapper() {
        return (row) -> new Qualification(
                row.getString("crew_id"),
                row.get("qualification", CONVERTER),
                row.get("since", LOCAL_DATE)
        );
    }
}
