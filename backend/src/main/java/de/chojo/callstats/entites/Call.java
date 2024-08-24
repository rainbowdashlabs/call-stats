package de.chojo.callstats.entites;

import de.chojo.sadu.mapper.rowmapper.RowMapper;

import java.time.Instant;

import static de.chojo.sadu.queries.converter.StandardValueConverter.INSTANT_SECONDS;

public record Call(
        Integer id,
        Instant start,
        Instant end,
        Integer duration,
        String callType,
        String abortReason,
        String note,
        boolean atStation) {
    public static RowMapper<Call> mapper() {
        return RowMapper.forClass(Call.class)
                        .mapper(row -> new Call(
                                row.getInt("id"),
                                row.get("start_timestamp", INSTANT_SECONDS),
                                row.get("end_timestamp", INSTANT_SECONDS),
                                row.getInt("duration"),
                                row.getString("call_type"),
                                row.getString("abort_reason"),
                                row.getString("note"),
                                row.getBoolean("at_station"))
                        )
                        .addColumns("id", "start_timestamp", "end_timestamp", "duration", "call_type", "abort_reason", "note", "at_station")
                        .build();
    }
}
