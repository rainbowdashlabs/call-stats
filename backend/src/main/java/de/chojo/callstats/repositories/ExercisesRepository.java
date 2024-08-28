package de.chojo.callstats.repositories;

import de.chojo.callstats.data.Repositories;
import de.chojo.callstats.entites.Crew;
import de.chojo.callstats.entites.Exercise;

import java.util.List;

import static de.chojo.sadu.queries.api.call.Call.call;
import static de.chojo.sadu.queries.api.query.Query.query;

public class ExercisesRepository extends AbstractRepository {
    public ExercisesRepository(Repositories repositories) {
        super(repositories);
    }

    public Exercise save(Exercise exercise) {
        return query("""
                INSERT INTO exercises(id, date, hours, subject)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(id)
                    DO UPDATE
                    SET date    = excluded.date,
                        hours   = excluded.hours,
                        subject = excluded.subject
                RETURNING id, date, hours, minutes, subject""")
                .single(call().bind(exercise.id()).bind(exercise.date()).bind(exercise.hours()).bind(exercise.subject()))
                .mapAs(Exercise.class)
                .first()
                .orElseThrow();
    }

    public void updateExerciseCrew(Exercise exercise, List<Crew> crewList) {
        query("DELETE FROM exercise_crew WHERE exercise_id = ?")
                .single(call().bind(exercise.id()))
                .delete();
        query("INSERT INTO exercise_crew(exercise_id, crew_id) VALUES (?,?)")
                .batch(crewList.stream().map(e -> call().bind(exercise.id()).bind(e.id())))
                .insert();
    }
}
