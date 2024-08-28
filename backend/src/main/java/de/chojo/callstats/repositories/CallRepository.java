package de.chojo.callstats.repositories;

import de.chojo.callstats.data.Repositories;
import de.chojo.callstats.entites.Call;
import de.chojo.callstats.entites.Crew;

import java.util.List;

import static de.chojo.sadu.queries.api.call.Call.call;
import static de.chojo.sadu.queries.api.query.Query.query;
import static de.chojo.sadu.queries.converter.StandardValueConverter.INSTANT_SECONDS;

public class CallRepository extends AbstractRepository {
    public CallRepository(Repositories repositories) {
        super(repositories);
    }

    public Call save(Call call) {
        return query("""
                INSERT
                INTO
                    calls(id, start_timestamp, end_timestamp, call_type, abort_reason, note, at_station)
                VALUES
                    (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id)
                    DO UPDATE SET
                                  start_timestamp = excluded.start_timestamp,
                                  end_timestamp   = excluded.end_timestamp,
                                  call_type       = excluded.call_type,
                                  abort_reason    = excluded.abort_reason,
                                  note            = excluded.note,
                                  at_station      = excluded.at_station
                RETURNING id, start_timestamp, end_timestamp, duration, call_type, abort_reason, note, at_station""")
                .single(call().bind(call.id()).bind(call.start(), INSTANT_SECONDS).bind(call.end(), INSTANT_SECONDS)
                              .bind(call.callType()).bind(call.abortReason()).bind(call.note()).bind(call.atStation()))
                .mapAs(Call.class)
                .first()
                .orElseThrow();
    }

    public void updateCallCrew(Call call, List<Crew> crewList) {
        query("DELETE FROM call_crew WHERE call_id = ?")
                .single(call().bind(call.id()))
                .delete();
        query("INSERT INTO call_crew(call_id, crew_id) VALUES (?,?)")
                .batch(crewList.stream().map(e -> call().bind(call.id()).bind(e.id())))
                .insert();
    }
}
