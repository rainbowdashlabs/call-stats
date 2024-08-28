package de.chojo.callstats.entites;

import de.chojo.sadu.mapper.reader.ValueReader;
import de.chojo.sadu.mapper.wrapper.Row;
import de.chojo.sadu.queries.api.call.adapter.Adapter;
import de.chojo.sadu.queries.converter.ValueConverter;

import java.util.Arrays;

public enum QualificationType {
    LEADER("Staffelführer"),
    DRIVER("Maschinist");

    private final String name;

    QualificationType(String name) {
        this.name = name;
    }

    @Override
    public String toString() {
        return name;
    }

    public static QualificationType parse(String value) {
        return Arrays.stream(values()).filter(e -> e.name.equals(value)).findFirst().orElseThrow();
    }

    public static final ValueConverter<QualificationType, String> CONVERTER = ValueConverter.create(Adapter.create(QualificationType.class, (stmt, index, value) -> stmt.setString(index, value.toString()), 12), ValueReader.create(QualificationType::parse, Row::getString, Row::getString));
}
