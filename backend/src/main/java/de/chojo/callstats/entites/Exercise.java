package de.chojo.callstats.entites;

import java.time.LocalDate;

public record Exercise(Integer id, LocalDate date, Integer hours, Integer minutes, String subject) {
}
