package de.chojo.callstats.repositories;

import de.chojo.callstats.data.Repositories;
import de.chojo.callstats.entites.Call;

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
}
