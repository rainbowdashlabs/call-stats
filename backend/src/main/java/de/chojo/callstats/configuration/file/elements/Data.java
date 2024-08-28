package de.chojo.callstats.configuration.file.elements;

import de.chojo.sadu.core.configuration.DatabaseConfig;
import de.chojo.sadu.core.configuration.SchemaProvider;

public class Data implements SchemaProvider, DatabaseConfig {

    private String host = "localhost";
    private String port = "5432";
    private String user = "postgres";
    private String password = "postgres";
    private String database = "postgres";
    private String schema = "public";
    private int poolSize = 3;

    public Data() {
    }

    @Override
    public String host() {
        return host;
    }

    @Override
    public String port() {
        return port;
    }

    @Override
    public String user() {
        return user;
    }

    @Override
    public String password() {
        return password;
    }

    @Override
    public String database() {
        return database;
    }

    @Override
    public String schema() {
        return schema;
    }

    public int poolSize() {
        return poolSize;
    }
}
