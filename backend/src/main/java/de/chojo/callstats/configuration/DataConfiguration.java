package de.chojo.callstats.configuration;

import de.chojo.sadu.datasource.DataSourceCreator;
import de.chojo.sadu.postgresql.databases.PostgreSql;

import javax.sql.DataSource;

public class DataConfiguration {
    public DataConfiguration() {
        initDatasource()
    }

    private void initDatasource() {
        DataSourceCreator.create(PostgreSql.get())
                .configure(conf -> {
                    conf.addParameter()
                })
    }
}
