package de.chojo.callstats.repositories;

import de.chojo.callstats.data.Repositories;
import de.chojo.callstats.entites.Call;
import de.chojo.callstats.entites.Crew;
import de.chojo.callstats.entites.Exercise;

import java.util.List;

import static de.chojo.sadu.queries.api.call.Call.call;
import static de.chojo.sadu.queries.api.query.Query.query;

public class CrewRepository extends AbstractRepository {
    public CrewRepository(Repositories repositories) {
        super(repositories);
    }

    public Crew save(Crew crew) {
        return query("""
                INSERT INTO crew(id, name)
                VALUES (?, ?)
                ON CONFLICT(id) DO UPDATE set name = excluded.name
                RETURNING id, name""")
                .single(call().bind(crew.id()).bind(crew.name()))
                .mapAs(Crew.class)
                .first()
                .orElseThrow();
    }

    public List<Crew> crewByExercise(Exercise exercise) {
        return query("SELECT c.name, c.id FROM exercise_crew ec LEFT JOIN crew c on ec.crew_id = c.id WHERE ec.exercise_id = ?")
                .single(call().bind(exercise.id()))
                .mapAs(Crew.class)
                .all();
    }

    public List<Crew> crewByCall(Call call) {
        return query("SELECT c.name, c.id FROM call_crew cc LEFT JOIN crew c on cc.crew_id = c.id WHERE cc.call_id = ?")
                .single(call().bind(call.id()))
                .mapAs(Crew.class)
                .all();
    }
}
