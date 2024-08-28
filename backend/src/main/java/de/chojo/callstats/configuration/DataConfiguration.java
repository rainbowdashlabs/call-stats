package de.chojo.callstats.configuration;

import com.zaxxer.hikari.HikariDataSource;
import de.chojo.callstats.data.Repositories;
import de.chojo.sadu.datasource.DataSourceCreator;
import de.chojo.sadu.mapper.RowMapperRegistry;
import de.chojo.sadu.postgresql.databases.PostgreSql;
import de.chojo.sadu.postgresql.mapper.PostgresqlMapper;
import de.chojo.sadu.queries.api.configuration.QueryConfiguration;
import de.chojo.sadu.updater.SqlUpdater;
import org.slf4j.Logger;

import java.io.IOException;
import java.sql.SQLException;

import static org.slf4j.LoggerFactory.getLogger;

public class DataConfiguration {
    private final FileConfiguration fileConfiguration;
    private static final Logger log = getLogger(DataConfiguration.class);
    private Repositories repositories;
    private HikariDataSource datasource;

    public DataConfiguration(FileConfiguration fileConfiguration) throws SQLException, IOException {
        this.fileConfiguration = fileConfiguration;
        initDatasource();
    }

    private void initDatasource() throws SQLException, IOException {
        datasource = DataSourceCreator.create(PostgreSql.get())
                                      .configure(conf -> conf.withConfig(fileConfiguration.data()))
                                      .create()
                                      .withMaximumPoolSize(fileConfiguration.data().poolSize())
                                      .build();

        SqlUpdater.builder(datasource, PostgreSql.get())
                  .setSchemas(fileConfiguration.data().schema())
                  .execute();

        QueryConfiguration.setDefault(
                QueryConfiguration.builder(datasource)
                                  .setRowMapperRegistry(new RowMapperRegistry().register(PostgresqlMapper.getDefaultMapper()))
                                  .setExceptionHandler(ex -> log.error("Database error occurred", ex))
                                  .build());
    }

    private void initRepository() {
        repositories = new Repositories();
    }

    public Repositories repositories() {
        return repositories;
    }

    public HikariDataSource datasource() {
        return datasource;
    }
}
