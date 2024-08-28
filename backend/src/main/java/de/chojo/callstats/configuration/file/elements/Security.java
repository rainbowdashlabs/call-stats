package de.chojo.callstats.configuration.file.elements;

import java.util.concurrent.ThreadLocalRandom;

public class Security {
    private String secretKey = ThreadLocalRandom.current()
                                                .ints('a', 'z' + 1)
                                                .limit(48)
                                                .collect(StringBuilder::new, StringBuilder::appendCodePoint, StringBuilder::append)
                                                .toString();
    private long jwtExpiration = 900000; // 15 minutes
    private long jwtRefreshExpiration = 604800000; // 7 days

    public String secretKey() {
        return secretKey;
    }

    public long jwtExpiration() {
        return jwtExpiration;
    }

    public long jwtRefreshExpiration() {
        return jwtRefreshExpiration;
    }
}
