package de.chojo.callstats.repositories;

import de.chojo.callstats.data.Repositories;
import de.chojo.callstats.entites.Crew;
import de.chojo.callstats.entites.Qualification;

import java.util.List;

import static de.chojo.callstats.entites.QualificationType.CONVERTER;
import static de.chojo.sadu.queries.api.call.Call.call;
import static de.chojo.sadu.queries.api.query.Query.query;

public class QualificationRepository extends AbstractRepository {
    public QualificationRepository(Repositories repositories) {
        super(repositories);
    }

    public List<Qualification> getByCrew(Crew crew) {
        return query("SELECT qualification, crew_id, since FROM qualifications WHERE crew_id = ?")
                .single(call().bind(crew.id()))
                .mapAs(Qualification.class)
                .all();
    }

    public void updateQualification(Crew crew, List<Qualification> qualifications) {
        query("DELETE FROM qualifications WHERE crew_id = ?")
                .single(call().bind(crew.id()))
                .delete();

        query("INSERT INTO qualifications(crew_id, qualification, since) VALUES(?,?,?)")
                .batch(qualifications.stream().map(e -> call().bind(e.crewId()).bind(e.qualification(), CONVERTER).bind(e.since())))
                .insert();
    }
}
